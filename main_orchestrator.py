import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from agent_researcher import run_researcher
from agent_question_generator import run_question_generator
from agent_data_provider import run_data_provider
from agent_web_builder import run_web_builder
from agent_starter_code import run_starter_code_generator

try:
    from agent_web_designer import run_web_designer
except ImportError:  # pragma: no cover - optional dependency
    run_web_designer = None  # type: ignore


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _resolve_model(step_model: Optional[str], default_model: Optional[str]) -> Optional[str]:
    return step_model or default_model


def _print_plan(args) -> None:
    shared_model = args.model or "default"
    topic_label = args.topic if args.topic else "[auto]"
    lines = [
        "오케스트레이션 계획:",
        f"  1. Researcher ▶︎ 토픽 '{topic_label}' 조사 (model={_resolve_model(args.research_model, args.model) or shared_model})",
        f"  2. Question Generator ▶︎ '{args.job_level} {args.job_role}' 과제 JSON 생성 (model={_resolve_model(args.question_model, args.model) or shared_model})",
        "  3. Data Provider ▶︎ 과제별 데이터셋 생성",
        f"  4. Starter Code ▶︎ 과제별 샘플 코드 생성 (model={_resolve_model(args.starter_model, args.model) or shared_model})",
        f"  5. Web Builder ▶︎ 인터랙티브 페이지 생성 (model={_resolve_model(args.builder_model, args.model) or shared_model})",
    ]
    if args.with_designer:
        lines.append(
            f"  6. Web Designer ▶︎ 스타일 시스템 생성 (model={_resolve_model(args.designer_model, args.model) or shared_model})"
        )
    else:
        lines.append("  6. Web Designer ▶︎ (건너뜀)")
    print("\n".join(lines))
    print()


def _ensure_exists(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{description}이(가) 존재하지 않습니다: {path}")




def _apply_output_root(args, parser) -> None:
    if not getattr(args, "output_root", None):
        return

    root = Path(args.output_root)
    root.mkdir(parents=True, exist_ok=True)

    def _adjust(attr: str, default_name: str) -> None:
        default_value = parser.get_default(attr)
        current_value = getattr(args, attr)
        if current_value == default_value:
            setattr(args, attr, str(root / default_name))

    mappings = [
        ("research_output", "research_report.txt"),
        ("question_output", "assignments.json"),
        ("datasets_dir", "datasets"),
        ("starter_dir", "starter_code"),
        ("html_output", "index.html"),
        ("css_output", "styles.css"),
        ("design_notes", "design_notes.md"),
    ]

    for attr, filename in mappings:
        _adjust(attr, filename)

    args.output_root = str(root)


def orchestrate(args) -> None:
    print(f"[{_timestamp()}] --- Multi-agent generation requested ---")
    _print_plan(args)

    research_path = Path(args.research_output)
    assignments_path = Path(args.question_output)
    datasets_dir = Path(args.datasets_dir)
    html_output = Path(args.html_output)
    starter_dir = Path(args.starter_dir)

    # Step 1: Research
    if args.skip_research:
        _ensure_exists(research_path, "사전 조사 보고서")
    else:
        run_researcher(
            topic=args.topic,
            output_path=str(research_path),
            model=_resolve_model(args.research_model, args.model),
            temperature=args.research_temperature,
            job_role=args.job_role,
            job_level=args.job_level,
        )

    # Step 2: Question generation
    if args.skip_questions:
        _ensure_exists(assignments_path, "테이크홈 과제 JSON")
    else:
        run_question_generator(
            job_role=args.job_role,
            job_level=args.job_level,
            company_name=args.company_name,
            input_path=str(research_path),
            output_path=str(assignments_path),
            model=_resolve_model(args.question_model, args.model),
            temperature=args.question_temperature,
            language=args.language,
        )

    # Step 3: Data provider
    if args.skip_datasets:
        if datasets_dir.exists() and any(datasets_dir.iterdir()):
            print(f"[{_timestamp()}] --- Dataset generation skipped (existing files detected). ---")
        else:
            print(f"[{_timestamp()}] --- Dataset step skipped, but directory is empty: {datasets_dir}")
    else:
        run_data_provider(
            assignments_path=str(assignments_path),
            output_dir=str(datasets_dir),
            language=args.language,
        )

    # Step 4: Starter code
    if args.skip_starter:
        print(f"[{_timestamp()}] --- Starter code generation skipped. ---")
    else:
        run_starter_code_generator(
            assignments_path=str(assignments_path),
            output_dir=str(starter_dir),
            model=_resolve_model(args.starter_model, args.model),
            temperature=args.starter_temperature,
        )

    # Step 5: Web builder
    if args.skip_builder:
        print(f"[{_timestamp()}] --- Web builder 단계가 생략되었습니다. ---")
    else:
        run_web_builder(
            assignments_path=str(assignments_path),
            research_summary_path=str(research_path),
            output_html=str(html_output),
            language=args.language,
            title=args.site_title or f"{args.job_level} {args.job_role} Take-Home Portal",
            model=_resolve_model(args.builder_model, args.model),
            temperature=args.builder_temperature,
            starter_dir=str(starter_dir),
        )

    # Step 6: (optional) Web designer
    if args.with_designer:
        if run_web_designer is None:
            print("[경고] agent_web_designer.py 가 발견되지 않아 스타일링 단계를 건너뜁니다.")
        elif args.skip_builder:
            print("[경고] index.html이 생성되지 않아 디자이너 단계를 건너뜁니다.")
        else:
            run_web_designer(
                html_path=str(html_output),
                css_output=str(Path(args.css_output)),
                notes_output=str(Path(args.design_notes)),
                language=args.language,
                model=_resolve_model(args.designer_model, args.model),
                temperature=args.designer_temperature,
            )

    print(f"[{_timestamp()}] --- Pipeline complete. Review '{html_output}'. ---")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="End-to-end orchestrator for take-home assignment websites",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--job-role", "-r", default="iOS Developer", help="Target role, e.g., 'iOS Developer'")
    parser.add_argument("--job-level", "-l", default="Senior", help="Job level (Junior, Mid-level, Senior, Principal 등)")
    parser.add_argument("--language", default="Korean", help="Content language (final output remains Korean)")
    parser.add_argument("--company-name", default="Myrealtrip OTA Company", help="Company/brand name for prompts")
    parser.add_argument("--topic", help="Research topic override (auto-generated if omitted)")
    parser.add_argument("--model", help="Default OpenAI-compatible model for all agents")
    parser.add_argument("--research-model")
    parser.add_argument("--question-model")
    parser.add_argument("--data-model")
    parser.add_argument("--starter-model")
    parser.add_argument("--builder-model")
    parser.add_argument("--designer-model")
    parser.add_argument("--research-temperature", type=float)
    parser.add_argument("--question-temperature", type=float)
    parser.add_argument("--data-temperature", type=float)
    parser.add_argument("--starter-temperature", type=float)
    parser.add_argument("--builder-temperature", type=float)
    parser.add_argument("--designer-temperature", type=float)
    parser.add_argument("--skip-research", action="store_true", help="Skip research step (expects existing report)")
    parser.add_argument("--skip-questions", action="store_true", help="Skip question generation step")
    parser.add_argument("--skip-datasets", action="store_true", help="Skip dataset generation")
    parser.add_argument("--skip-starter", action="store_true", help="Skip starter code generation")
    parser.add_argument("--skip-builder", action="store_true", help="Skip web builder stage")
    parser.add_argument("--with-designer", action="store_true", help="Run web designer after builder")
    parser.add_argument("--output-root", help="Optional base directory to contain all generated artifacts")
    parser.add_argument("--research-output", default="research_report.txt")
    parser.add_argument("--question-output", default="assignments.json")
    parser.add_argument("--datasets-dir", default="datasets")
    parser.add_argument("--starter-dir", default="starter_code")
    parser.add_argument("--html-output", default="index.html")
    parser.add_argument("--css-output", default="styles.css")
    parser.add_argument("--design-notes", default="design_notes.md")
    parser.add_argument("--site-title", help="Override HTML <title>")
    return parser


def main(argv=None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    _apply_output_root(args, parser)

    try:
        orchestrate(args)
    except Exception as exc:  # noqa: BLE001
        print(f"[오류] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
