"""Bulk orchestrator runner driven by Google Sheet configuration."""

from __future__ import annotations

import argparse
import io
import concurrent.futures
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
import requests

from main_orchestrator import build_arg_parser, orchestrate


@dataclass
class SheetRow:
    index: int
    team: str
    job_role: str
    job_level: str
    language: str
    model: Optional[str]
    research_model: Optional[str]
    question_model: Optional[str]
    data_model: Optional[str]
    starter_model: Optional[str]
    builder_model: Optional[str]
    designer_model: Optional[str]
    with_designer: bool
    topic: Optional[str]
    external_link: Optional[str]
    raw: Dict[str, Any]



_ROLE_TOKEN_MAP = {
    "developer": "dev",
    "development": "dev",
    "engineer": "eng",
    "engineering": "eng",
    "frontend": "fe",
    "back": "back",
    "backend": "be",
    "fullstack": "fullstack",
    "full": "full",
    "stack": "stack",
    "mobile": "mobile",
    "ios": "ios",
    "android": "android",
    "aos": "aos",
    "data": "data",
    "product": "product",
    "qa": "qa",
}

_LEVEL_ALIAS_MAP = {
    "junior": "jr",
    "junior level": "jr",
    "entry": "jr",
    "entry level": "jr",
    "associate": "assoc",
    "intern": "intern",
    "mid": "mid",
    "mid level": "mid",
    "midlevel": "mid",
    "mid-level": "mid",
    "low mid": "low_mid",
    "low-mid": "low_mid",
    "mid senior": "mid_senior",
    "mid-senior": "mid_senior",
    "mid senior level": "mid_senior",
    "mid-senior level": "mid_senior",
    "senior": "sr",
    "senior level": "sr",
    "staff": "staff",
    "lead": "lead",
    "principal": "principal",
    "director": "director",
}

_LANGUAGE_CODE_MAP = {
    "korean": "ko",
    "korea": "ko",
    "english": "en",
    "eng": "en",
    "japanese": "ja",
    "japan": "ja",
    "chinese": "zh",
    "mandarin": "zh",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "vietnamese": "vi",
    "thai": "th",
    "indonesian": "id",
    "portuguese": "pt",
}


def _tokenize(value: str) -> List[str]:
    if not value:
        return []
    return [tok for tok in re.split(r"[^0-9A-Za-z]+", value.lower()) if tok]


def _normalize_tokens(tokens: List[str], replacements: Dict[str, str]) -> str:
    mapped = [replacements.get(tok, tok) for tok in tokens]
    value = "_".join(mapped)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def _job_role_slug(job_role: str, team: str) -> str:
    slug = _normalize_tokens(_tokenize(job_role), _ROLE_TOKEN_MAP) if job_role else ""
    if slug:
        return slug
    fallback = _normalize_tokens(_tokenize(team), _ROLE_TOKEN_MAP)
    return fallback or "role"


def _level_slug(level: str) -> str:
    if not level:
        return "level"
    normalized = re.sub(r"\s+", " ", level.lower().replace("-", " ")).strip()
    if normalized in _LEVEL_ALIAS_MAP:
        return _LEVEL_ALIAS_MAP[normalized]
    tokens = _tokenize(level)
    token_str = " ".join(tokens)
    if token_str in _LEVEL_ALIAS_MAP:
        return _LEVEL_ALIAS_MAP[token_str]
    slug = _normalize_tokens(tokens, {})
    slug = slug or "level"
    return slug


def _language_slug(language: str) -> str:
    if not language:
        return "lang"
    key = re.sub(r"\s+", " ", language.lower()).strip()
    if key in _LANGUAGE_CODE_MAP:
        return _LANGUAGE_CODE_MAP[key]
    key = key.replace(" ", "_")
    key = re.sub(r"_+", "_", key).strip("_")
    if key in _LANGUAGE_CODE_MAP:
        return _LANGUAGE_CODE_MAP[key]
    return key[:2] if len(key) >= 2 else key or "lang"


def _compose_output_folder(row: SheetRow) -> str:
    job_slug = _job_role_slug(row.job_role, row.team)
    level_slug = _level_slug(row.job_level)
    language_slug = _language_slug(row.language)
    parts = [part for part in (job_slug, level_slug, language_slug) if part]
    if not parts:
        return _slugify(row.team or "assignment")
    return "_".join(parts)

def _slugify(value: str) -> str:
    clean = re.sub(r"[^0-9A-Za-z가-힣]+", "-", value.strip())
    clean = re.sub(r"-+", "-", clean).strip("-")
    return clean.lower() or "assignment"


def _select_model_value(row_value: Optional[str], default_value: Optional[str]) -> Optional[str]:
    return row_value or default_value

def _bool_from_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "t"}


def _clean_optional_string(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() in {"none", "null", "n/a", "na"}:
        return None
    return text


def _infer_job_role(team: str, job_role: Optional[str]) -> str:
    if job_role and job_role.strip():
        return job_role.strip()
    base = team.strip()
    lowered = base.lower()
    if lowered.endswith("developer") or lowered.endswith("engineer"):
        return base
    return f"{base} Developer"


def _sheet_csv_url(sheet_url: str) -> str:
    match = re.search(r"/d/([\w-]+)/", sheet_url)
    if not match:
        raise ValueError("유효한 Google Sheet URL이 아닙니다.")
    sheet_id = match.group(1)
    gid_match = re.search(r"gid=(\d+)", sheet_url)
    gid = gid_match.group(1) if gid_match else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def _fetch_sheet_records(args: argparse.Namespace) -> pd.DataFrame:
    if args.sheet_csv:
        csv_path = Path(args.sheet_csv)
        if not csv_path.exists():
            raise FileNotFoundError(f"지정한 CSV 파일을 찾을 수 없습니다: {csv_path}")
        return pd.read_csv(csv_path)

    if not args.sheet_url:
        raise ValueError("--sheet-url 또는 --sheet-csv 중 하나는 필수입니다.")

    csv_url = _sheet_csv_url(args.sheet_url)
    headers = {"User-Agent": "Myrealtrip-BulkRunner/1.0"}
    response = requests.get(csv_url, headers=headers, timeout=30)
    response.raise_for_status()
    return pd.read_csv(io.StringIO(response.text))


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={col: col.strip().lower() for col in df.columns})
    return df


def _iter_sheet_rows(df: pd.DataFrame) -> Iterable[SheetRow]:
    required_cols = {"team", "level"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"필수 컬럼이 누락되었습니다: {', '.join(sorted(missing))}")

    for idx, row in df.iterrows():
        team = str(row.get("team", "")).strip()
        if not team:
            continue
        job_level = str(row.get("level", "")).strip() or "Mid-level"
        language = str(row.get("language", "Korean") or "Korean").strip() or "Korean"

        model = _clean_optional_string(row.get("model"))
        research_model = _clean_optional_string(row.get("research_model"))
        question_model = _clean_optional_string(row.get("question_model"))
        data_model = _clean_optional_string(row.get("data_model"))
        starter_model = _clean_optional_string(row.get("starter_model"))
        builder_model = _clean_optional_string(row.get("builder_model"))
        designer_model = _clean_optional_string(row.get("designer_model"))

        with_designer = _bool_from_value(row.get("with_designer"))

        topic = _clean_optional_string(row.get("topic"))
        external_link = _clean_optional_string(row.get("external_link"))
        job_role = _infer_job_role(team, row.get("job_role"))

        yield SheetRow(
            index=idx,
            team=team,
            job_role=job_role,
            job_level=job_level,
            language=language,
            model=model,
            research_model=research_model,
            question_model=question_model,
            data_model=data_model,
            starter_model=starter_model,
            builder_model=builder_model,
            designer_model=designer_model,
            with_designer=with_designer,
            topic=topic,
            external_link=external_link,
            raw={k: row.get(k) for k in df.columns},
        )


def _has_external_link(row: SheetRow) -> bool:
    if not row.external_link:
        return False
    normalized = row.external_link.strip().lower()
    if normalized in {"no", "n", "none"}:
        return False
    return True


def _prepare_cli_args(row: SheetRow, output_root: Path, defaults: argparse.Namespace) -> Tuple[List[str], Path]:
    base_dir = output_root / _compose_output_folder(row)
    base_dir.mkdir(parents=True, exist_ok=True)

    research_path = base_dir / "research_report.txt"
    assignments_path = base_dir / "assignments.json"
    datasets_dir = base_dir / "datasets"
    starter_dir = base_dir / "starter_code"
    html_output = base_dir / "index.html"
    css_output = base_dir / "styles.css"
    design_notes = base_dir / "design_notes.md"

    cli_args: List[str] = [
        "--job-role",
        row.job_role,
        "--job-level",
        row.job_level,
        "--language",
        row.language,
        "--company-name",
        defaults.company_name,
        "--research-output",
        str(research_path),
        "--question-output",
        str(assignments_path),
        "--datasets-dir",
        str(datasets_dir),
        "--starter-dir",
        str(starter_dir),
        "--html-output",
        str(html_output),
        "--css-output",
        str(css_output),
        "--design-notes",
        str(design_notes),
    ]

    model_value = _select_model_value(row.model, defaults.model)
    if model_value:
        cli_args.extend(["--model", model_value])

    stage_flags = [
        ("--research-model", row.research_model, defaults.research_model),
        ("--question-model", row.question_model, defaults.question_model),
        ("--data-model", row.data_model, defaults.data_model),
        ("--starter-model", row.starter_model, defaults.starter_model),
        ("--builder-model", row.builder_model, defaults.builder_model),
        ("--designer-model", row.designer_model, defaults.designer_model),
    ]
    for flag, row_value, default_value in stage_flags:
        value = _select_model_value(row_value, default_value)
        if value:
            cli_args.extend([flag, value])

    topic_value = _select_model_value(row.topic, defaults.topic)
    if topic_value:
        cli_args.extend(["--topic", topic_value])

    if defaults.with_designer or row.with_designer:
        cli_args.append("--with-designer")

    if defaults.skip_research:
        cli_args.append("--skip-research")
    if defaults.skip_questions:
        cli_args.append("--skip-questions")
    if defaults.skip_datasets:
        cli_args.append("--skip-datasets")
    if defaults.skip_starter:
        cli_args.append("--skip-starter")
    if defaults.skip_builder:
        cli_args.append("--skip-builder")

    return cli_args, base_dir


def _run_pipeline(row: SheetRow, output_root: Path, defaults: argparse.Namespace) -> Dict[str, Any]:
    cli_args, base_dir = _prepare_cli_args(row, output_root, defaults)
    parser = build_arg_parser()
    args = parser.parse_args(cli_args)

    try:
        orchestrate(args)
        status = "completed"
        error = None
    except Exception as exc:  # noqa: BLE001
        status = "failed"
        error = str(exc)

    return {
        "row_index": row.index,
        "team": row.team,
        "job_role": row.job_role,
        "job_level": row.job_level,
        "language": row.language,
        "output_dir": str(base_dir),
        "status": status,
        "error": error,
    }


def _max_workers(value: Optional[int]) -> int:
    if value and value > 0:
        return value
    cpu_count = os.cpu_count() or 4
    return min(8, cpu_count * 2)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bulk run Myrealtrip take-home generator from Google Sheet")
    parser.add_argument("--sheet-url", help="Google Sheet URL (edit view)")
    parser.add_argument("--sheet-csv", help="Optional local CSV path")
    parser.add_argument("--output-root", default="bulk_output", help="Root directory for generated artifacts")
    parser.add_argument("--max-workers", type=int, help="Maximum concurrent workers")
    parser.add_argument("--default-model", help="Fallback model if sheet row omits it")
    parser.add_argument("--default-research-model", help="Fallback research model")
    parser.add_argument("--default-question-model", help="Fallback question generator model")
    parser.add_argument("--default-data-model", help="Fallback dataset model")
    parser.add_argument("--default-starter-model", help="Fallback starter code model")
    parser.add_argument("--default-builder-model", help="Fallback web builder model")
    parser.add_argument("--default-designer-model", help="Fallback designer model")
    parser.add_argument("--default-topic", help="Fallback topic if sheet row omits it")
    parser.add_argument("--with-designer", action="store_true", help="Force designer step for all rows")
    parser.add_argument("--skip-research", action="store_true")
    parser.add_argument("--skip-questions", action="store_true")
    parser.add_argument("--skip-datasets", action="store_true")
    parser.add_argument("--skip-starter", action="store_true")
    parser.add_argument("--skip-builder", action="store_true")
    parser.add_argument("--company-name", default="Myrealtrip OTA Company")
    parser.add_argument("--topic", dest="topic", help=argparse.SUPPRESS)
    parser.add_argument("--model", dest="model", help=argparse.SUPPRESS)
    parser.add_argument("--summary", help="Optional JSON result summary output path")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    df = _fetch_sheet_records(args)
    df = _normalize_columns(df)

    rows = list(_iter_sheet_rows(df))
    if not rows:
        print("생성할 유효한 행이 없습니다.")
        return

    tasks = [row for row in rows if not _has_external_link(row)]
    if not tasks:
        print("모든 행에 external_link가 존재하여 생성할 항목이 없습니다.")
        return

    defaults = SimpleNamespace(
        company_name=args.company_name,
        model=args.default_model,
        research_model=args.default_research_model,
        question_model=args.default_question_model,
        data_model=args.default_data_model,
        starter_model=args.default_starter_model,
        builder_model=args.default_builder_model,
        designer_model=args.default_designer_model,
        topic=args.default_topic,
        with_designer=args.with_designer,
        skip_research=args.skip_research,
        skip_questions=args.skip_questions,
        skip_datasets=args.skip_datasets,
        skip_starter=args.skip_starter,
        skip_builder=args.skip_builder,
    )

    worker_count = min(len(tasks), _max_workers(args.max_workers))
    print(f"총 {len(tasks)}개의 행을 {worker_count}개 작업자로 처리합니다.")

    results: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_row = {executor.submit(_run_pipeline, row, output_root, defaults): row for row in tasks}
        for future in concurrent.futures.as_completed(future_to_row):
            row = future_to_row[future]
            try:
                result = future.result()
                results.append(result)
                if result["status"] == "completed":
                    print(f"[완료] {row.team} / {row.job_role} → {result['output_dir']}")
                else:
                    print(f"[실패] {row.team} / {row.job_role}: {result['error']}")
            except Exception as exc:  # noqa: BLE001
                print(f"[치명적 오류] 행 {row.index} 처리 중 예외 발생: {exc}")

    if args.summary:
        summary_path = Path(args.summary)
        summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"결과 요약이 저장되었습니다: {summary_path}")


if __name__ == "__main__":
    main()
