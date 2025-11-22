import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from llm_client import create_llm_client, create_nvidia_llm_direct

UNICODE_QUOTE_MAP = {
    "“": '"',
    "”": '"',
    "„": '"',
    "‟": '"',
    "«": '"',
    "»": '"',
    "「": '"',
    "」": '"',
    "『": '"',
    "』": '"',
    "‚": "'",
    "‘": "'",
    "’": "'",
    "‛": "'",
    "´": "'",
    "ˮ": '"',
}


def _normalize_jsonish(text: str) -> str:
    """Normalize typographic punctuation that breaks JSON parsing."""
    if not text:
        return text
    for bad, good in UNICODE_QUOTE_MAP.items():
        text = text.replace(bad, good)
    # Replace full-width punctuation commonly emitted in non-English output
    text = text.replace("：", ":").replace("，", ",")
    return text


def _normalize_model_id(name: str) -> str:
    if not name:
        return name
    return name


def _openrouter_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    site = os.getenv("OPENROUTER_SITE_URL")
    app = os.getenv("OPENROUTER_APP_NAME")
    if site:
        headers["HTTP-Referer"] = site
    if app:
        headers["X-Title"] = app
    return headers


def _ensure_report_exists(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find research report at {path}. "
            "Run agent_researcher.py first or provide --input."
        )
    return path.read_text(encoding="utf-8")


def _extract_json_payload(raw: str) -> str:
    import re
    import json
    # Remove think blocks first
    raw = re.sub(r'&lt;think&gt;[\s\S]*?&lt;/think&gt;|\\&lt;think&gt;[\s\S]*?\\&lt;/think&gt;|&lt;think&gt;[\s\S]*?&lt;/think&gt;', '', raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r'<think>[\s\S]*?</think>', '', raw, flags=re.IGNORECASE | re.DOTALL)
    
    # Extract json code blocks, prefer last one
    blocks = re.findall(r"```\s*(?:json)?\s*([\s\S]+?)\s*```", raw, flags=re.IGNORECASE)
    candidates = [block.strip() for block in blocks] if blocks else []
    candidates.append(raw.strip())
    
    for candidate in candidates:
        # Extract outermost JSON if possible
        match = re.search(r'\{[\s\S]*\}', candidate)
        if match:
            candidate = match.group(0)
        
        # Remove trailing commas (common JSON error from LLMs)
        candidate = re.sub(r',(\s*[}\]])', r'\1', candidate)
        
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            continue
    
    # Fallback
    stripped = raw.strip()
    match = re.search(r'\{[\s\S]*\}', stripped)
    if match:
        candidate = match.group(0).strip()
        # Remove trailing commas again for fallback path
        candidate = re.sub(r',(\s*[}\]])', r'\1', candidate)
        # Attempt to balance braces if truncated
        open_braces = candidate.count('{')
        close_braces = candidate.count('}')
        if open_braces > close_braces:
            candidate += '}' * (open_braces - close_braces)
        return candidate
    return stripped



def _is_allowed_char(ch: str) -> bool:
    if ch in ("\n", "\r", "\t"):
        return True
    category = unicodedata.category(ch)
    return not category.startswith("C")


def _sanitize_string(text: str) -> str:
    return "".join(ch for ch in text if _is_allowed_char(ch))


def _sanitize_structure(value):  # type: ignore[no-untyped-def]
    if isinstance(value, str):
        return _sanitize_string(value)
    if isinstance(value, dict):
        return {key: _sanitize_structure(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_sanitize_structure(item) for item in value]
    return value


def _save_markdown(payload: dict, markdown_path: Path) -> None:
    lines: list[str] = []
    company = payload.get("company", "")
    job_role = payload.get("job_role", "")
    job_level = payload.get("job_level", "")

    if company or job_role:
        lines.append(f"# {company} {job_level} {job_role} 테이크홈 과제")
        lines.append("")

    for assignment in payload.get("assignments", []):
        title = assignment.get("title", "과제")
        lines.append(f"## {title}")
        if assignment.get("mission"):
            lines.append(assignment["mission"])
            lines.append("")
        sections = (
            ("요약", "summary"),
            ("핵심 요구사항", "requirements"),
            ("제출물", "deliverables"),
            ("AI 활용 가이드라인", "ai_guidelines"),
            ("평가 기준", "evaluation"),
            ("예상 소요 시간", "timeline"),
            ("심층 토론 질문", "discussion_questions"),
        )
        for header, key in sections:
            value = assignment.get(key)
            if not value:
                continue
            lines.append(f"### {header}")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(str(value))
            lines.append("")
    markdown_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def run_question_generator(
    job_role: str,
    job_level: str = "Senior",
    company_name: str = "Myrealtrip OTA Company",
    input_path: str = "research_report.txt",
    output_path: str = "assignments.json",
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    language: str = "Korean",
    markdown_preview_path: Optional[str] = None,
) -> str:
    load_dotenv()

    print(f"--- Generating assignments for: {job_role} ({job_level}) ---")

    report_path = Path(input_path)
    research_summary = _ensure_report_exists(report_path)

    temp_val = temperature if temperature is not None else float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    
    # Use direct NVIDIA if available (bypasses LiteLLM)
    if os.getenv("NVIDIA_API_KEY") and not model:
        llm = create_nvidia_llm_direct(temperature=temp_val)
    else:
        llm = create_llm_client(model=model, temperature=temp_val)

    schema_description = json.dumps(
        {
            "type": "object",
            "required": ["company", "job_role", "job_level", "assignments"],
            "properties": {
                "company": {"type": "string"},
                "job_role": {"type": "string"},
                "job_level": {"type": "string"},
                "assignments": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 1,
                    "items": {
                        "type": "object",
                        "required": [
                            "id",
                            "title",
                            "mission",
                            "requirements",
                            "deliverables",
                            "ai_guidelines",
                            "evaluation",
                            "timeline",
                            "discussion_questions",
                            "datasets",
                            "starter_code",
                        ],
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "mission": {"type": "string"},
                            "summary": {"type": "string"},
                            "requirements": {"type": "array", "items": {"type": "string"}},
                            "deliverables": {"type": "array", "items": {"type": "string"}},
                            "ai_guidelines": {"type": "array", "items": {"type": "string"}},
                            "evaluation": {"type": "array", "items": {"type": "string"}},
                            "timeline": {"type": "string"},
                            "discussion_questions": {
                                "type": "array",
                                "minItems": 3,
                                "maxItems": 5,
                                "items": {"type": "string"},
                            },
                            "datasets": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["name", "format", "records", "columns"],
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "format": {"type": "string", "enum": ["csv", "json"]},
                                        "records": {"type": "integer", "minimum": 10, "maximum": 2000},
                                        "filename": {"type": "string"},
                                        "columns": {
                                            "type": "array",
                                            "minItems": 2,
                                            "maxItems": 8,
                                            "items": {
                                                "type": "object",
                                                "required": ["name"],
                                                "properties": {
                                                    "name": {"type": "string"},
                                                    "type": {
                                                        "type": "string",
                                                        "enum": [
                                                            "string",
                                                            "text",
                                                            "integer",
                                                            "float",
                                                            "boolean",
                                                            "date",
                                                            "datetime",
                                                            "category",
                                                        ],
                                                        "default": "string",
                                                    },
                                                    "description": {"type": "string"},
                                                    "choices": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                            "starter_code": {
                                "type": "object",
                                "properties": {
                                    "language": {"type": "string"},
                                    "description": {"type": "string"},
                                    "filename": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
        },
        ensure_ascii=False,
        indent=2,
    )

    # Build language-specific system and user prompts
    if language.lower() in ["korean", "한국어"]:
        system_msg = """당신은 OTA 산업 전문 채용 디렉터입니다. 모든 결과는 JSON 형식으로 반환하며, 한국어와 영문 기술 용어만 사용하고 한자·중국어 문자를 절대 포함하지 않습니다."""
        user_msg = """회사명: {company_name}
직무: {job_level} {job_role}
언어: {language}

연구 요약:
{research_summary}

위 정보를 참고하여 OTA 서비스 맥락에 맞는 대표 테이크홈 과제 1개를 설계하세요.
- 이 과제는 Myrealtrip 고객 여정 중 가장 중요한 문제를 해결하도록 설계하고, 실무 수준의 깊이를 담아야 합니다.
- 과제에는 최소 1개의 맞춤형 데이터셋(`datasets`)과 스타터 코드 메타데이터(`starter_code`)를 포함시키고, 내용이 과제 요구사항과 긴밀히 연결되도록 하세요.
- 데이터셋의 `description`과 `columns`는 과제에서 다루는 문제를 해결하는 데 필요한 정보를 전달해야 하며, `records` 값은 10~2000 범위에서 현실적인 크기를 설정하세요.
- `starter_code`에는 후보자가 바로 활용할 수 있도록 언어(`language`), 파일명(`filename`), 제공 목적을 명확히 설명하고 과제 맥락과 연결하세요.
- 모든 설명은 간결하면서도 실무 지침이 되도록 작성하며, 기술 용어(예: API, Swift, Compose)는 영어를 유지할 수 있으나 그 외에는 한글을 사용하세요.

JSON Schema:
{schema_description}
"""
    elif language.lower() in ["japanese", "日本語", "japanese (日本語)"]:
        system_msg = """You are an OTA industry recruitment director. Return all results in JSON format. Write all assignment content in Japanese, but keep technical terms (API, Swift, JSON, etc.) in English."""
        user_msg = """Company: {company_name}
Role: {job_level} {job_role}
Language: {language}

Research Summary:
{research_summary}

Based on the above, design one flagship take-home assignment in the context of OTA services.
- The assignment should tackle the most critical customer journey or OTA feature area for Myrealtrip.
- Include at least 1 custom dataset (`datasets`) and starter code metadata (`starter_code`), tightly connected to the assignment requirements.
- Dataset `description` and `columns` should convey information needed to solve the problem, and `records` should be realistic (10-2000).
- `starter_code` should clearly explain the language, filename, and purpose so candidates can use it immediately.
- Write all descriptions in Japanese (日本語), keeping technical terms in English.

JSON Schema:
{schema_description}
"""
    elif language.lower() in ["chinese", "中文", "chinese (中文)"]:
        system_msg = """You are an OTA industry recruitment director. Return all results in JSON format. Write all assignment content in Chinese (Simplified), but keep technical terms (API, Swift, JSON, etc.) in English."""
        user_msg = """Company: {company_name}
Role: {job_level} {job_role}
Language: {language}

Research Summary:
{research_summary}

Based on the above, design one flagship take-home assignment in the context of OTA services.
- The assignment should tackle the most critical customer journey or OTA feature area for Myrealtrip.
- Include at least 1 custom dataset (`datasets`) and starter code metadata (`starter_code`), tightly connected to the assignment requirements.
- Dataset `description` and `columns` should convey information needed to solve the problem, and `records` should be realistic (10-2000).
- `starter_code` should clearly explain the language, filename, and purpose so candidates can use it immediately.
- Write all descriptions in Chinese (中文), keeping technical terms in English.

JSON Schema:
{schema_description}
"""
    else:  # English or default
        system_msg = """You are an OTA industry recruitment director. Return all results in JSON format. Write all assignment content in English."""
        user_msg = """Company: {company_name}
Role: {job_level} {job_role}
Language: {language}

Research Summary:
{research_summary}

Based on the above, design one flagship take-home assignment in the context of OTA services.
- The assignment should tackle the most critical customer journey or OTA feature area for Myrealtrip.
- Include at least 1 custom dataset (`datasets`) and starter code metadata (`starter_code`), tightly connected to the assignment requirements.
- Dataset `description` and `columns` should convey information needed to solve the problem, and `records` should be realistic (10-2000).
- `starter_code` should clearly explain the language, filename, and purpose so candidates can use it immediately.
- Write all descriptions in English, keeping technical terms as-is.

JSON Schema:
{schema_description}
"""
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_msg),
            ("user", user_msg),
        ]
    )

    chain = prompt | llm | StrOutputParser()
    raw_json = chain.invoke(
        {
            "company_name": company_name,
            "job_role": job_role,
            "job_level": job_level,
            "language": language,
            "research_summary": research_summary,
            "schema_description": schema_description,
        }
    )
    raw_json = _normalize_jsonish(raw_json)

    cleaned_json = _extract_json_payload(raw_json)

    try:
        parsed = json.loads(cleaned_json)
    except json.JSONDecodeError as exc:
        debug_path = Path(output_path).with_suffix(".raw.json")
        debug_path.write_text(raw_json, encoding="utf-8")
        cleaned_path = Path(output_path).with_suffix(".cleaned.json")
        cleaned_path.write_text(cleaned_json, encoding="utf-8")
        
        # Try one more aggressive cleanup
        print(f"⚠️  Initial JSON parse failed, attempting aggressive cleanup...")
        import re
        # Try to extract just the assignments array if present
        array_match = re.search(r'"assignments"\s*:\s*\[([\s\S]*)\]', cleaned_json)
        if array_match:
            try:
                fallback = '{"assignments": [' + array_match.group(1) + ']}'
                parsed = json.loads(fallback)
                print(f"✅ Recovered JSON using fallback extraction")
            except:
                raise ValueError(
                    "Failed to parse assignments JSON. Raw output saved to "
                    f"{debug_path} (raw) and {cleaned_path} (cleaned)."
                ) from exc
        else:
            raise ValueError(
                "Failed to parse assignments JSON. Raw output saved to "
                f"{debug_path} (raw) and {cleaned_path} (cleaned)."
            ) from exc

    sanitized = _sanitize_structure(parsed)
    sanitized["company"] = company_name
    sanitized["job_role"] = job_role
    sanitized["job_level"] = job_level

    output_file = Path(output_path)
    output_file.write_text(json.dumps(sanitized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"--- Assignments JSON saved to: {output_file} ---")

    if markdown_preview_path:
        _save_markdown(sanitized, Path(markdown_preview_path))
    else:
        preview_path = output_file.with_suffix(".md")
        _save_markdown(sanitized, preview_path)
        print(f"--- Preview markdown saved to: {preview_path} ---")

    return str(output_file)


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate structured take-home assignments from research report",
    )
    parser.add_argument("job_role", nargs="+", help="Role to tailor assignments for")
    parser.add_argument("--level", default="Senior", help="Job level calibration")
    parser.add_argument("--company", default="Myrealtrip OTA Company", help="Company/brand name")
    parser.add_argument("--input", default="research_report.txt", help="Path to research report input")
    parser.add_argument("--output", default="assignments.json", help="Path to write structured assignments JSON")
    parser.add_argument("--markdown", help="Optional markdown preview path")
    parser.add_argument("--model", help="Override model (e.g., deepseek/deepseek-chat-v3.1)")
    parser.add_argument("--temperature", type=float, help="Temperature override (default 0.35)")
    parser.add_argument("--language", default="Korean", help="Output language (default Korean)")
    parser.add_argument("--env-file", help="Extra .env file to load")
    parser.add_argument("--profile", help="Profile name to load .env.<profile>")
    return parser.parse_args(argv)


def _load_profiles(args: argparse.Namespace) -> None:
    load_dotenv()
    if args.env_file:
        load_dotenv(args.env_file, override=True)

    if args.profile:
        base_dir = Path(__file__).resolve().parent
        profile_path = base_dir / f".env.{args.profile}"
        if profile_path.exists():
            load_dotenv(profile_path, override=True)
        else:
            print(f"Warning: profile file not found: {profile_path}", file=sys.stderr)


if __name__ == "__main__":
    cli_args = _parse_args()
    _load_profiles(cli_args)

    role = " ".join(cli_args.job_role).strip()
    if not role:
        print("Error: job_role cannot be empty", file=sys.stderr)
        sys.exit(1)

    run_question_generator(
        job_role=role,
        job_level=cli_args.level,
        company_name=cli_args.company,
        input_path=cli_args.input,
        output_path=cli_args.output,
        model=cli_args.model,
        temperature=cli_args.temperature,
        language=cli_args.language,
        markdown_preview_path=cli_args.markdown,
    )
