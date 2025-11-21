
from __future__ import annotations
import argparse
import json
import os
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

LOGO_URL = (
    "https://cdn.prod.website-files.com/652cf379a649f747375f2efe/65b9f0d4c60108a9d95c20c2_"
    "%EB%B3%80%EA%B2%BD%ED%95%84%EC%9A%94)%EB%A7%88%EC%9D%B4%EB%A6%AC%EC%96%BC%ED%8A%B8%EB%A6%BD.jpg"
)
CAREER_URL = "https://careers.myrealtrip.com/"
SITE_URL = "https://www.myrealtrip.com/"
_ALLOWED_EXTRA = "\n\t\r"

def _sanitize_string(value: str) -> str:
    return "".join(ch for ch in value if ch.isprintable() or ch in _ALLOWED_EXTRA)

def _sanitize(data: Any) -> Any:
    if isinstance(data, str):
        return _sanitize_string(data)
    if isinstance(data, dict):
        return {k: _sanitize(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_sanitize(item) for item in data]
    return data

def _load_assignments(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Assignments JSON not found: {path}")
    return _sanitize(json.loads(path.read_text(encoding="utf-8")))

def _read_text(path: Optional[str]) -> str:
    if not path:
        return ""
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return _sanitize_string(file_path.read_text(encoding="utf-8"))

def _resolve_href(raw: Optional[str], html_dir: Path) -> Optional[str]:
    if not raw:
        return None
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    if candidate.exists():
        try:
            return candidate.relative_to(html_dir).as_posix()
        except ValueError:
            return os.path.relpath(candidate, html_dir).replace(os.sep, "/")
    return raw

def _default_intro(language: str = "Korean") -> Dict[str, Any]:
    """Return language-specific intro content."""
    if language.lower() in ["japanese", "日本語", "japanese (日本語)"]:
        return {
            "north_star_title": 'The North Star: "旅行体験の完全な接続"',
            "north_star_body": (
                "MyRealtripは、すべての旅行者がより簡単に好みに合った旅行を計画し、体験できる世界を作ります。"
                "ビジョンを実現するために、最も創造的で革新的な方法で旅行体験を変革する人材を募集しています。"
            ),
            "culture_title": "Product Engineer 開発文化",
            "culture_body": (
                "AI時代、開発者の役割は一つの分野にとどまりません。MyRealtripのProduct Engineerは、顧客の問題を発見し、"
                "解決策が実際に効果を発揮するまで最後まで責任を持つ開発者です。私たちは技術的専門性を基盤に、製品と顧客体験全体を包括してこのように働きます。"
            ),
            "culture_points": [
                "顧客中心の問題定義：「何を作るか」より「なぜ作るべきか」を先に考え、問題解決の方向を自ら設定します。",
                "境界のない問題解決：様々な技術領域の境界を越えて、問題を最も速く解決できる方法を自ら見つけて実行します。",
                "機敏に実行、改善：複雑な手続きを減らして迅速に決定し、短いフィードバックサイクルで継続的に製品を改善します。",
                "最後まで責任を持つ姿勢：リリースが終わりではなく、顧客の問題が解決するまで改善と運用を続けます。",
            ],
            "ai_guidance_title": "AIツール活用ガイド",
            "ai_guidance_body": "本課題はGitHub Copilot、ChatGPTなどのAIツールを自由に活用して解決できます。AI時代をリードするProduct EngineerにとってAI活用能力は重要な能力です。",
            "ai_guidance_note": (
                "ただし、提出時にREADME.mdファイルにどのツールをどのように活用して問題解決に役立てたかを具体的に記述してください。"
                "（例：「API通信のためのURLSession基本コードをChatGPTで生成しました。」、「SwiftUIレイアウト関連の問題を解決するためにCopilotの提案を参考にしました。」）"
            ),
            "site_invite_text": "MyRealtripが提供する様々な旅行商品とサービスを公式ホームページでご確認ください。",
            "assignment_choice": "用意された課題の中から実行可能な項目を自由に選択して提出してください。",
        }
    elif language.lower() in ["chinese", "中文", "chinese (中文)"]:
        return {
            "north_star_title": 'The North Star: "旅行体验的完全连接"',
            "north_star_body": (
                "MyRealtrip致力于让所有旅行者更轻松地计划和体验符合自己喜好的旅行。"
                "为了实现这一愿景，我们正在招募能够以最具创意和创新的方式改变旅行体验的人才。"
            ),
            "culture_title": "Product Engineer 开发文化",
            "culture_body": (
                "在AI时代，开发者的角色不仅限于一个领域。MyRealtrip的Product Engineer是发现客户问题，"
                "并对解决方案的实际效果负责到底的开发者。我们以技术专业性为基础，涵盖产品和客户体验的各个方面，这样工作。"
            ),
            "culture_points": [
                "以客户为中心定义问题：先思考"为什么要做"而不是"做什么"，自主设定问题解决的方向。",
                "无边界问题解决：跨越各种技术领域的边界，自主寻找并执行最快解决问题的方法。",
                "敏捷执行、改进：减少复杂流程，快速决策，通过短反馈周期持续改进产品。",
                "负责到底的态度：发布不是终点，持续改进和运营直到客户问题消失。",
            ],
            "ai_guidance_title": "AI工具使用指南",
            "ai_guidance_body": "本课题可以自由使用GitHub Copilot、ChatGPT等AI工具来解决。对于引领AI时代的Product Engineer来说，AI应用能力是重要的能力。",
            "ai_guidance_note": (
                "但是，提交时必须在README.md文件中具体说明使用了哪些工具以及如何帮助解决问题。"
                "（例如："使用ChatGPT生成了用于API通信的URLSession基本代码。"、"参考了Copilot的建议来解决SwiftUI布局相关问题。"）"
            ),
            "site_invite_text": "请在官方网站上查看MyRealtrip提供的各种旅行产品和服务。",
            "assignment_choice": "请从准备好的课题中自由选择可执行的项目提交。",
        }
    else:  # English or default
        return {
            "north_star_title": 'The North Star: "Complete Connection of Travel Experiences"',
            "north_star_body": (
                "MyRealtrip creates a world where all travelers can more easily plan and experience trips that match their preferences. "
                "To realize this vision, we are looking for talented individuals who will transform travel experiences in the most creative and innovative ways."
            ),
            "culture_title": "Product Engineer Development Culture",
            "culture_body": (
                "In the AI era, a developer's role does not stay in one field. MyRealtrip's Product Engineers discover customer problems "
                "and take responsibility until the solution actually works. Based on technical expertise, we work across products and customer experiences in this way."
            ),
            "culture_points": [
                "Customer-Centric Problem Definition: Think about 'why we should build' before 'what to build,' and set the direction of problem-solving yourself.",
                "Borderless Problem Solving: Cross the boundaries of various technical domains and find and execute the fastest way to solve problems.",
                "Execute Agilely, Improve: Reduce complex procedures to make quick decisions and continuously improve products with short feedback cycles.",
                "Responsible to the End: Release is not the end; continue improvement and operation until customer problems disappear.",
            ],
            "ai_guidance_title": "AI Tool Usage Guide",
            "ai_guidance_body": "This assignment can be solved freely using AI tools such as GitHub Copilot and ChatGPT. AI utilization ability is an important competency for Product Engineers leading the AI era.",
            "ai_guidance_note": (
                "However, when submitting, you must specifically describe in the README.md file which tools you used and how they helped solve the problem. "
                "(Example: \"Generated basic URLSession code for API communication using ChatGPT.\", \"Referred to Copilot's suggestions to solve SwiftUI layout issues.\")"
            ),
            "site_invite_text": "Check out the various travel products and services provided by MyRealtrip on the official website.",
            "assignment_choice": "Feel free to choose and submit any of the prepared assignments that you can complete.",
        }
    
    # Korean default
    return {
        "north_star_title": 'The North Star: "여행 경험의 완전한 연결"',
        "north_star_body": (
            "마이리얼트립은 모든 여행자들이 더 쉽게 취향에 맞는 여행을 계획하고 경험할 수 있는 세상을 만들어 갑니다. "
            "비전을 이루기 위해 가장 창의적이고 혁신적인 방식으로 여행의 경험을 변화시켜 나갈 인재분들을 모시고 있습니다."
        ),
        "culture_title": "Product Engineer 개발 문화",
        "culture_body": (
            "AI 시대, 개발자의 역할은 한 분야에만 머무르지 않습니다. 마이리얼트립의 Product Engineer는 고객의 문제를 발견하고, "
            "해결책이 실제로 효과를 발휘할 때까지 끝까지 책임지는 개발자입니다. 우리는 기술 전문성을 기반으로, 제품과 고객 경험 전반을 아우르며 이렇게 일합니다."
        ),
        "culture_points": [
            "고객 중심 문제 정의: "무엇을 만들 것인가?"보다 "왜 만들어야 하는가?"를 먼저 고민하고, 문제 해결의 방향을 스스로 설정합니다.",
            "경계 없는 문제 해결: 다양한 기술 영역의 경계를 넘나들며, 문제를 가장 빠르게 해결할 수 있는 방법을 스스로 찾아 실행합니다.",
            "민첩하게 실행, 개선: 복잡한 절차를 줄여 빠르게 결정하고, 짧은 피드백 주기로 지속적으로 제품을 개선합니다.",
            "끝까지 책임지는 태도: 릴리즈가 끝이 아니라, 고객의 문제가 사라질 때까지 개선과 운영을 이어갑니다.",
        ],
        "ai_guidance_title": "AI 도구 활용 안내",
        "ai_guidance_body": "본 과제는 GitHub Copilot, ChatGPT 등 AI 도구를 자유롭게 활용하여 해결할 수 있습니다. AI 시대를 선도하는 Product Engineer에게 AI 활용 능력은 중요한 역량입니다.",
        "ai_guidance_note": (
            "단, 제출 시 README.md 파일에 어떤 도구를 어떻게 활용하여 문제 해결에 도움을 받았는지 구체적으로 서술해 주셔야 합니다. "
            "(예: \"API 통신을 위한 URLSession 기본 코드를 ChatGPT를 통해 생성했습니다.\", \"SwiftUI 레이아웃 관련 문제를 해결하기 위해 Copilot의 제안을 참고했습니다.\")"
        ),
        "site_invite_text": "마이리얼트립이 제공하는 다양한 여행 상품과 서비스를 공식 홈페이지에서 확인해 주세요.",
        "assignment_choice": "준비된 과제 중 수행 가능한 항목을 자유롭게 선택하여 제출하셔도 됩니다.",
    }

def _list_items(items: Optional[List[str]]) -> str:
    if not items:
        return "<li>정보 없음</li>"
    filtered = [escape(item) for item in items if item]
    if not filtered:
        return "<li>정보 없음</li>"
    return "\n".join(f"<li>{item}</li>" for item in filtered)

def _ordered_items(items: Optional[List[str]]) -> str:
    if not items:
        return "<li>정보 없음</li>"
    filtered = [escape(item) for item in items if item]
    if not filtered:
        return "<li>정보 없음</li>"
    return "\n".join(f"<li>{item}</li>" for item in filtered)

def _render_datasets(datasets: List[Dict[str, Any]], html_dir: Path) -> str:
    if not datasets:
        return "<li>제공된 데이터셋이 없습니다.</li>"
    rows: List[str] = []
    for dataset in datasets:
        href = _resolve_href(dataset.get("download_href") or dataset.get("path"), html_dir)
        name = escape(dataset.get("name") or dataset.get("filename") or "Dataset")
        desc = escape(dataset.get("description") or "")
        meta_parts: List[str] = []
        if dataset.get("format"):
            meta_parts.append(str(dataset["format"]).upper())
        if dataset.get("records"):
            meta_parts.append(f"{dataset['records']} rows")
        if dataset.get("filename"):
            meta_parts.append(dataset["filename"])
        meta = " · ".join(meta_parts)
        link = f"<a class='resource-link' href='{href}' download>{name}</a>" if href else f"<span class='resource-link is-disabled'>{name}</span>"
        info = f"<span class='resource-meta'>{escape(meta)}</span>" if meta else ""
        desc_html = f"<span class='resource-desc'>{desc}</span>" if desc else ""
        rows.append(f"<li>{link} {info} {desc_html}</li>")
    return "\n".join(rows)

def _render_starter(starter: Dict[str, Any], html_dir: Path) -> str:
    if not starter:
        return "<p class='dim'>제공된 스타터 코드가 없습니다.</p>"
    href = _resolve_href(starter.get("download_href") or starter.get("path"), html_dir)
    filename = escape(starter.get("filename") or "starter_code")
    description = escape(starter.get("description") or "핵심 로직 구현을 위한 기본 구조를 제공합니다.")
    language = starter.get("language")
    badge = f"<span class='resource-meta'>{escape(str(language).upper())}</span>" if language else ""
    link = f"<a class='resource-link' href='{href}' download>{filename}</a>" if href else f"<span class='resource-link is-disabled'>{filename}</span>"
    return f"<div class='starter-resource'>{link}{badge}<p class='resource-desc'>{description}</p></div>"

# -- Assignments rendering (card style) ----------------------------------------
def _render_assignments(assignments: List[Dict[str, Any]], html_dir: Path) -> str:
    if not assignments:
        return "<div class='assignments-empty'>등록된 과제가 없습니다.</div>"

    tab_buttons: List[str] = []
    panels: List[str] = []

    for idx, assignment in enumerate(assignments, start=1):
        tab_id = f"assignment-tab-{idx}"
        button_id = f"{tab_id}-button"
        is_active = idx == 1

        title = escape(assignment.get("title") or f"과제 {idx}")
        summary = escape(assignment.get("summary") or "")
        mission = escape(assignment.get("mission") or "")

        datasets_html = _render_datasets(assignment.get("datasets_resolved", []), html_dir)
        starter_html = _render_starter(assignment.get("starter_resolved", {}), html_dir)

        active_attr = ' data-active="true"' if is_active else ''
        tab_buttons.append(
            f"<button type='button' class='assignments-tabs__tab{' is-active' if is_active else ''}' "
            f"id='{button_id}' role='tab' aria-controls='{tab_id}' aria-selected='{str(is_active).lower()}' "
            f"data-tab-target='{tab_id}'{active_attr}>{title}</button>"
        )

        panels.append(f"""
<article class='assignment-panel{" is-active" if is_active else ""}' id='{tab_id}' role='tabpanel'
         aria-labelledby='{button_id}' data-tab-panel{' hidden' if not is_active else ''}>
  <div class="assignment-card">
    <h3 class="assignment-title">{title}</h3>
    <p class="assignment-summary">{summary}</p>

    <div class="assignment-section">
      <h4>✔️ 과제 설명</h4>
      <p>{mission}</p>
    </div>

    <div class="assignment-section">
      <h4>⚙️ 기술 요구사항</h4>
      <ul class="assignment-list">{_list_items(assignment.get("requirements"))}</ul>
    </div>

    <div class="assignment-section">
      <h4>📦 제출물</h4>
      <ul class="assignment-list">{_list_items(assignment.get("deliverables"))}</ul>
    </div>

    <div class="assignment-section">
      <h4>📂 데이터셋</h4>
      <ul class="resource-list">{datasets_html}</ul>
    </div>

    <div class="assignment-section">
      <h4>🧰 스타터 코드</h4>
      {starter_html}
    </div>

    {'<div class="assignment-section"><h4>💬 심층 토론 질문</h4><ol class="assignment-list">' + _ordered_items(assignment.get("discussion_questions")) + '</ol></div>' if assignment.get("discussion_questions") else ""}
  </div>
</article>
""")

    return (
        "<div class='assignments-tabs' data-tabs>"
        "<div class='assignments-tabs__list' role='tablist' aria-orientation='horizontal'>"
        + "".join(tab_buttons)
        + "</div>"
        + "<div class='assignments-tabs__panels'>"
        + "".join(panels)
        + "</div>"
        + "</div>"
    )

# -- HTML Builder ---------------------------------------------------------------
def _build_html(context: Dict[str, Any], html_path: Path) -> str:
    html_dir = html_path.parent.resolve()

    # prepare assignments (resolve file paths for datasets & starter)
    assignments_prepared: List[Dict[str, Any]] = []
    for assignment in context.get("assignments", []):
        assignments_prepared.append({
            **assignment,
            "datasets_resolved": assignment.get("datasets", []),
            "starter_resolved": assignment.get("starter_code", {}),
        })

    assignments_html = _render_assignments(assignments_prepared, html_dir)

    # intro data
    language = context.get("language", "Korean")
    intro_raw = {**_default_intro(language), **context.get("intro", {})}
    culture_points = intro_raw.get("culture_points", [])
    culture_html = (
        "\n".join(
            (
                f'<li><strong class="text-slate-800">{escape(parts[0])}:</strong> {escape(parts[1].strip())}</li>'
                if len(parts := point.split(":", 1)) == 2
                else f"<li>{escape(point)}</li>"
            )
            for point in culture_points
        )
        if culture_points
        else ""
    )

    # company/hero copy (no eyebrow text wanted)
    company = context.get("company", {})
    job_level = escape(company.get("job_level", "").strip())
    job_role = escape(company.get("job_role", "").strip())
    hero_role = " ".join(part for part in [job_level, job_role] if part).strip() or "Mid-level AOS Developer"

    page_title = escape(context.get("page_title", "Myrealtrip Take-Home Portal"))
    assignment_choice = escape(intro_raw.get("assignment_choice"))
    site_invite = escape(intro_raw.get("site_invite_text"))
    north_star_title = escape(intro_raw.get("north_star_title"))
    north_star_body = escape(intro_raw.get("north_star_body"))
    culture_title = escape(intro_raw.get("culture_title"))
    culture_body = escape(intro_raw.get("culture_body"))
    ai_guidance_title = escape(intro_raw.get("ai_guidance_title"))
    ai_guidance_body = escape(intro_raw.get("ai_guidance_body"))
    ai_guidance_note = escape(intro_raw.get("ai_guidance_note"))

    css_styles = """
      :root{
        --bg-color:#F7F9FC;--text-color:#1F2937;--accent-color:#059669;--card-color:#FFFFFF;
        --light-accent:#E6F4F1;--gray-color:#6B7280;--slate-100:#f1f5f9;--slate-700:#334155;
        --slate-800:#1e293b;--emerald-50:#ecfdf5;--emerald-500:#10b981;--emerald-800:#065f46;
        --shadow-sm:0 1px 2px rgba(0,0,0,.05);--shadow:0 1px 3px rgba(0,0,0,.1),0 1px 2px rgba(0,0,0,.06)
      }
      *{box-sizing:border-box}
      body{background:var(--bg-color);color:var(--text-color);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.6;margin:0;font-size:1rem}
      a{color:var(--accent-color);text-decoration:none}a:hover{text-decoration:underline}
      h1,h2,h3,h4{color:var(--text-color);line-height:1.2;margin:0 0 .5rem}
      .layout{max-width:1200px;margin:0 auto;padding:6.5rem 1rem 2rem} /* top padding for sticky header */
      /* Header (sticky) */
      .page-header{position:sticky;top:0;z-index:50;background:#fff;box-shadow:var(--shadow);padding:.75rem 0}
      .page-header__container{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between}
      .page-header__logo img{height:30px}
      .page-header__right{display:flex;align-items:center;gap:2rem}
      .page-header__nav{display:flex;gap:1rem}
      .page-header__nav-link{padding:.5rem 1rem;border-radius:8px;color:var(--gray-color)}
      .page-header__apply-btn{background:var(--accent-color);color:#fff;padding:.5rem 1rem;border-radius:8px;font-weight:700}
      /* Buttons */
      .btn{display:inline-flex;align-items:center;gap:.5rem;padding:.9rem 1.4rem;border-radius:12px;
           font-weight:700;text-decoration:none;border:2px solid transparent;transition:transform .02s ease,box-shadow .2s ease}
      .btn:active{transform:translateY(1px)}
      .btn-primary{background:var(--accent-color);color:#fff}
      .btn-outline{background:#fff;color:var(--accent-color);border-color:var(--accent-color)}
      .btn + .btn{margin-left:1rem}
      /* Hero */
      .hero-section{display:block;margin-bottom:1rem}
      .hero-section__title{font-size:2.25rem;font-weight:800;margin-top:.25rem}
      .hero-section__description{font-size:1.125rem;color:var(--gray-color);margin-bottom:1rem}
      .hero-section__actions{display:flex;gap:1rem;flex-wrap:wrap;margin-top:1rem;margin-bottom:.25rem}
      .hero-section__note{margin-top:1rem;font-size:1.05rem;color:var(--gray-color)}
      /* Intro Panels full-width */
      .intro-panels{display:flex;flex-direction:column;gap:2rem;margin-top:1.5rem}
      .card{background:#fff;border:1px solid var(--slate-100);box-shadow:var(--shadow-sm);padding:2rem;border-radius:12px}
      .accent{color:var(--accent-color)}
      .dim{color:var(--slate-700)}
      /* Resource list styling */
      .resource-list{list-style:none;padding-left:0;margin:0}
      .resource-list li{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;padding:.4rem 0;border-bottom:1px dashed #e5e7eb}
      .resource-list li:last-child{border-bottom:none}
      .resource-link{font-weight:700}
      .resource-link::before{content:"📎";margin-right:.35rem}
      .resource-meta{font-size:.9rem;color:var(--gray-color)}
      .resource-desc{display:block;color:var(--gray-color);font-size:.95rem}
      /* Assignments Tabs */
      .assignments-section{margin-top:2rem}
      .assignments-tabs__list{display:flex;gap:.5rem;border-bottom:1px solid #e5e7eb;margin-bottom:.75rem}
      .assignments-tabs__tab{padding:.75rem 1.25rem;background:transparent;border:none;cursor:pointer;color:var(--gray-color);
                             border-bottom:3px solid transparent;font-size:1.05rem;border-radius:8px 8px 0 0}
      .assignments-tabs__tab.is-active{color:var(--text-color);border-bottom-color:var(--accent-color);font-weight:700}
      .assignment-panel{display:none}
      .assignment-panel.is-active{display:block}
      /* Assignment Card */
      .assignment-card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:2rem;box-shadow:var(--shadow-sm)}
      .assignment-title{font-size:1.5rem;font-weight:700;margin-bottom:.25rem}
      .assignment-summary{color:var(--gray-color);margin-bottom:1.25rem}
      .assignment-section{margin-bottom:1.25rem}
      .assignment-section h4{font-size:1.1rem;font-weight:700;color:var(--accent-color);margin-bottom:.4rem}
      .assignment-list{padding-left:1.2rem}
      .assignment-list li{margin-bottom:.3rem}
      /* Footer */
      .apply-section{text-align:center;margin-top:3rem}
      .apply-section__cta{background:var(--accent-color);color:#fff;padding:1rem 2.8rem;border-radius:14px;font-size:1.125rem;font-weight:800}
      .page-footer{text-align:center;padding:1rem;border-top:1px solid #e5e7eb;margin-top:3rem;color:var(--gray-color)}
    """

    # Build HTML
    return f"""<!DOCTYPE html>
<html lang='ko'>
<head>
  <meta charset='UTF-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>{page_title}</title>
  <style>{css_styles}</style>
</head>
<body>
  <header class='page-header'>
    <div class='page-header__container'>
      <a href='{SITE_URL}' target='_blank' rel='noopener' class='page-header__logo' aria-label='Myrealtrip 홈으로 이동'>
        <img src='{LOGO_URL}' alt='Myrealtrip 로고'>
      </a>
      <div class='page-header__right'>
        <nav class='page-header__nav'>
          <a class='page-header__nav-link' href='#intro'>Intro</a>
          <a class='page-header__nav-link' href='#assignments'>Assignments</a>
        </nav>
        <a class='page-header__apply-btn' href='{CAREER_URL}' target='_blank' rel='noopener'>지원하기</a>
      </div>
    </div>
  </header>

  <main class='layout'>
    <!-- Hero -->
    <section id='intro' class='hero-section'>
      <h1 class='hero-section__title'>{hero_role}</h1>
      <p class='hero-section__description'>{assignment_choice}</p>
      <div class='hero-section__actions'>
        <a class='btn btn-primary' href='{CAREER_URL}' target='_blank' rel='noopener' aria-label='지원 페이지 열기'>지원하기</a>
        <a class='btn btn-outline' href='{SITE_URL}' target='_blank' rel='noopener' aria-label='회사 홈페이지 열기'>회사 홈페이지</a>
      </div>
      <p class='hero-section__note'>{site_invite}</p>
    </section>

    <!-- Full-width Intro Panels -->
    <section class='intro-panels'>
      <div class='card'>
        <h2 class='accent'>{north_star_title}</h2>
        <p class='dim'>{north_star_body}</p>
      </div>

      <div class='card'>
        <h2 class='accent'>{culture_title}</h2>
        <p class='dim'>{culture_body}</p>
        <ul class='assignment-list'>
          {culture_html}
        </ul>
      </div>

      <div class='card' style='border-left:4px solid var(--emerald-500);background:var(--emerald-50);'>
        <h3 class='accent'>{ai_guidance_title}</h3>
        <p class='dim'>{ai_guidance_body}</p>
        <p><strong>{ai_guidance_note}</strong></p>
      </div>
    </section>

    <!-- Assignments -->
    <section class='assignments-section' id='assignments'>
      <div class='section-heading'>
        <h2>Assignments</h2>
        <p class='dim'>실무형 과제를 확인하고 데이터/스타터 코드를 내려받아 시작해 보세요.</p>
      </div>
      {assignments_html}
    </section>

    <section class='apply-section'>
      <h2>지원 안내</h2>
      <p class='dim'>가장 자신 있는 과제를 선택하여 결과물, 구현 전략, 테스트 및 AI 도구 활용 내역을 정리해 제출해 주세요.</p>
      <a class='apply-section__cta' href='{CAREER_URL}' target='_blank' rel='noopener'>지원하기</a>
    </section>
  </main>

  <footer class='page-footer'>
    <p>© 2025 MyRealTrip. All Rights Reserved.<br> This is a fictional take-home assignment for recruitment purposes.</p>
  </footer>

  <script>
    (function() {{
      document.querySelectorAll('[data-tabs]').forEach(container => {{
        const tabs = Array.from(container.querySelectorAll('[data-tab-target]'));
        const panels = Array.from(container.querySelectorAll('[data-tab-panel]'));
        if (!tabs.length) return;
        const activate = id => {{
          tabs.forEach(t => {{
            const active = t.dataset.tabTarget === id;
            t.setAttribute('aria-selected', active ? 'true':'false');
            t.classList.toggle('is-active', active);
          }});
          panels.forEach(p => {{
            const active = p.id === id;
            p.classList.toggle('is-active', active);
            if (active) p.removeAttribute('hidden'); else p.setAttribute('hidden','hidden');
          }});
        }};
        tabs.forEach(t => {{
          t.addEventListener('click', () => activate(t.dataset.tabTarget));
          t.addEventListener('keydown', e => {{
            if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {{
              e.preventDefault();
              const i = tabs.indexOf(t);
              const offset = e.key === 'ArrowRight' ? 1 : -1;
              const next = tabs[(i + offset + tabs.length) % tabs.length];
              next.focus(); activate(next.dataset.tabTarget);
            }}
          }});
        }});
        activate((tabs.find(t => t.dataset.active==='true') || tabs[0]).dataset.tabTarget);
      }});
    }})();
  </script>
</body>
</html>
"""

def run_web_builder(
    assignments_path: str = "assignments.json",
    research_summary_path: Optional[str] = None,
    output_html: str = "index.html",
    language: str = "Korean",
    title: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    starter_dir: Optional[str] = None,
) -> Path:
    load_dotenv()
    assignments = _load_assignments(Path(assignments_path))
    _ = _read_text(research_summary_path)  # placeholder
    assignments_list = assignments.get("assignments", [])
    for item in assignments_list:
        item.pop("timeline", None)

    context = {
        "language": language,
        "page_title": title or assignments.get("page_title") or "Myrealtrip Take-Home Portal",
        "company": {
            "name": assignments.get("company", "Myrealtrip"),
            "job_role": assignments.get("job_role"),
            "job_level": assignments.get("job_level"),
        },
        "intro": assignments.get("intro", {}),
        "assignments": assignments_list,
        "navigation": assignments.get(
            "navigation",
            [
                {"label": "Intro", "target": "intro"},
                {"label": "Assignments", "target": "assignments"},
            ],
        ),
    }
    html_path = Path(output_html)
    html = _build_html(context, html_path)
    html_path.write_text(html, encoding="utf-8")
    print(f"--- Web page generated at {html_path} ---")
    return html_path

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Myrealtrip take-home assignment HTML page")
    parser.add_argument("--assignments", default="assignments.json", help="Path to structured assignments JSON")
    parser.add_argument("--research", help="Optional research summary path")
    parser.add_argument("--output", default="index.html", help="Output HTML file path")
    parser.add_argument("--title", help="Custom page title override")
    parser.add_argument("--language", default="Korean", help="Language of narrative content")
    parser.add_argument("--model", help="Compatibility placeholder (unused)")
    parser.add_argument("--temperature", type=float, help="Compatibility placeholder (unused)")
    parser.add_argument("--starter-dir", help="Starter code directory (unused)")
    parser.add_argument("--env-file", help="Extra .env file to load")
    parser.add_argument("--profile", help="Profile name (loads .env.<profile>)")
    return parser.parse_args()

def _load_env_overrides(args: argparse.Namespace) -> None:
    load_dotenv()
    if args.env_file:
        load_dotenv(args.env_file, override=True)
    if args.profile:
        profile_path = Path(__file__).resolve().parent / f".env.{args.profile}"
        if profile_path.exists():
            load_dotenv(profile_path, override=True)
        else:
            print(f"Warning: profile file not found: {profile_path}")

if __name__ == "__main__":
    cli_args = _parse_args()
    _load_env_overrides(cli_args)
    run_web_builder(
        assignments_path=cli_args.assignments,
        research_summary_path=cli_args.research,
        output_html=cli_args.output,
        language=cli_args.language,
        title=cli_args.title,
        model=cli_args.model,
        temperature=cli_args.temperature,
        starter_dir=cli_args.starter_dir,
    )
