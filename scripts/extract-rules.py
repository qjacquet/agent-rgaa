#!/usr/bin/env python3
"""Extract RGAA criteria and tests from rules.html into structured JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError:
    print("Error: beautifulsoup4 required. Run: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

EXPECTED_CRITERIA = 106
EXPECTED_TESTS = 258

# Step-level patterns — human must use real AT (VoiceOver, NVDA…)
AT_STEP_PATTERNS = [
    r"restitu[ée]* par les technologies d.assistance",
    r"correctement restitu[ée]* par les technologies",
    r"restituable par les technologies",
]

# Tests where agent concludes on automation but human should cross-check (keyboard, pointer)
HUMAN_COMPLEMENT_TEST_IDS = {
    "7.3.1",
    "7.3.2",
    "7.4.1",
    "8.9.1",
    "8.9.2",
    "9.3.1",
    "9.3.2",
    "9.3.3",
    "10.7.1",
    "10.7.2",
    "10.7.3",
    "12.7.1",
    "12.7.2",
}

# Subjective steps — agent may pre-analyse but human confirms
JUDGMENT_PATTERNS = [
    r"déterminer si l.élément",
    r"déterminer si l.image",
    r"déterminer la nature",
    r"porteuse d.information",
    r"image de décoration",
    r"pertinence",
    r"nom pertinent",
    r"intitulé visible",
]


def split_methodology_steps(methodology_steps: list[str]) -> tuple[list[str], list[str]]:
    agent_steps: list[str] = []
    human_steps: list[str] = []
    for step in methodology_steps:
        low = step.lower().replace("'", "'").replace("'", "'")
        if any(re.search(p, low) for p in AT_STEP_PATTERNS):
            human_steps.append(step)
        else:
            agent_steps.append(step)
    return agent_steps, human_steps


def extract_verdict_hints(methodology_steps: list[str]) -> dict:
    success = ""
    failure_hints: list[str] = []
    for step in methodology_steps:
        low = step.lower()
        if "test est validé" in low or "si c'est le cas" in low.replace("'", "'"):
            success = step
        if low.startswith("sinon,") or low.startswith("sinon "):
            failure_hints.append(step)
    nc_default = (
        "Au moins un élément ne respecte pas les conditions de la méthodologie "
        "(voir étapes « Sinon » ou critère de validation)."
    )
    return {
        "success_criterion": success or "Toutes les étapes de la méthodologie sont satisfaites.",
        "failure_criterion": failure_hints[0] if failure_hints else nc_default,
        "failure_hints": failure_hints,
    }


def classify_agent_scope(
    test_id: str,
    title: str,
    methodology_steps: list[str],
) -> dict:
    """Classify how the agent and human share each test."""
    blob = " ".join([title, *methodology_steps]).lower()
    agent_steps, human_steps = split_methodology_steps(methodology_steps)
    verdict = extract_verdict_hints(methodology_steps)

    requires_judgment = any(re.search(p, blob) for p in JUDGMENT_PATTERNS)

    if not agent_steps and human_steps:
        scope = "at_only"
    elif human_steps:
        scope = "partial"
    elif requires_judgment:
        scope = "partial"
    else:
        scope = "full"

    human_complement = scope in {"partial", "at_only"} or test_id in HUMAN_COMPLEMENT_TEST_IDS

    return {
        "agent_scope": scope,
        "agent_steps": agent_steps,
        "human_steps": human_steps,
        "human_complement_required": human_complement,
        "success_criterion": verdict["success_criterion"],
        "failure_criterion": verdict["failure_criterion"],
        # Legacy fields
        "agent_excluded": scope == "at_only",
        "exclusion_reason": "assistive_tech" if scope == "at_only" else ("human_judgment" if requires_judgment and scope == "partial" else None),
        "agent_may_pre_analyse": scope in {"partial", "at_only"},
    }


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def element_text(el: Tag | None) -> str:
    if el is None:
        return ""
    return normalize_text(el.get_text(" ", strip=True))


def parse_wcag_levels(raw: str | None) -> list[str]:
    if not raw:
        return []
    return sorted({level.strip() for level in raw.split(",") if level.strip()})


def extract_list_items(ol: Tag | None) -> list[str]:
    if ol is None:
        return []
    steps: list[str] = []
    for li in ol.find_all("li", recursive=False):
        parts: list[str] = []
        for child in li.children:
            if isinstance(child, NavigableString):
                text = normalize_text(str(child))
                if text:
                    parts.append(text)
            elif isinstance(child, Tag):
                if child.name in {"ul", "ol"}:
                    for sub in child.find_all("li", recursive=False):
                        sub_text = element_text(sub)
                        if sub_text:
                            parts.append(f"- {sub_text}")
                else:
                    text = element_text(child)
                    if text:
                        parts.append(text)
        step = normalize_text(" ".join(parts))
        if step:
            steps.append(step)
    return steps


def extract_wcag_references(test_div: Tag) -> list[str]:
    refs: list[str] = []
    for h5 in test_div.find_all("h5", class_="fr-h6"):
        if "EN 301 549" in element_text(h5):
            break
        sibling = h5.find_next_sibling("div", class_="ref")
        if not sibling:
            continue
        for tag in sibling.select("a.fr-tag"):
            label = normalize_text(tag.get_text())
            if label:
                refs.append(label)
    return refs


def extract_en301549_references(test_div: Tag) -> list[str]:
    refs: list[str] = []
    for h5 in test_div.find_all("h5", class_="fr-h6"):
        if "EN 301 549" not in element_text(h5):
            continue
        sibling = h5.find_next_sibling("div", class_="ref")
        if not sibling:
            continue
        for li in sibling.find_all("li", class_="fr-text--sm"):
            text = element_text(li)
            if text:
                refs.append(text)
    return refs


def extract_test(test_div: Tag, criterion_title: str = "") -> dict:
    test_id = test_div.get("id", "")
    title_p = test_div.select_one(".title > p")
    methodology_section = test_div.select_one("section.methodologie")
    methodology_ol = None
    if methodology_section:
        methodology_ol = methodology_section.select_one("ol")

    title = element_text(title_p)
    methodology_steps = extract_list_items(methodology_ol)
    scope = classify_agent_scope(test_id, title, methodology_steps)

    return {
        "id": test_id,
        "title": title,
        "methodology_steps": methodology_steps,
        "references": {
            "wcag": extract_wcag_references(test_div),
            "en301549": extract_en301549_references(test_div),
        },
        **scope,
    }


def extract_criterion(criterion_li: Tag) -> dict:
    number_el = criterion_li.select_one(".number")
    title_el = criterion_li.select_one("span.title")
    criterion_id = ""
    if title_el and title_el.get("id"):
        criterion_id = title_el["id"]
    elif number_el:
        criterion_id = element_text(number_el)

    tests_div = criterion_li.select_one("div.tests")
    criterion_title = element_text(title_el)
    tests = []
    if tests_div:
        for test_div in tests_div.find_all("div", class_="test", recursive=False):
            tests.append(extract_test(test_div, criterion_title))

    at_excluded = sum(1 for t in tests if t.get("agent_scope") == "at_only")
    partial = sum(1 for t in tests if t.get("agent_scope") == "partial")
    human_complement = sum(1 for t in tests if t.get("human_complement_required"))

    return {
        "id": criterion_id,
        "title": criterion_title,
        "wcag_levels": parse_wcag_levels(criterion_li.get("data-wcag-level")),
        "tests": tests,
        "agent_excluded_tests": at_excluded,
        "partial_tests": partial,
        "human_complement_tests": human_complement,
    }


def extract_themes(container: Tag) -> list[dict]:
    themes: list[dict] = []
    theme_headers = container.find_all("h2", class_="fr-mt-6w", id=True)

    for header in theme_headers:
        theme_id = header["id"]
        title = element_text(header)
        title = re.sub(r"^\d+\.\s*", "", title).strip()

        ul = header.find_next_sibling("ul")
        criteria = []
        if ul:
            for criterion_li in ul.find_all("li", class_="criterion", recursive=False):
                criteria.append(extract_criterion(criterion_li))

        themes.append({"id": theme_id, "title": title, "criteria": criteria})

    return themes


def extract_rules(html_path: Path) -> dict:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    container = soup.find(id="criteria-container")
    if container is None:
        raise ValueError("Could not find #criteria-container in HTML")

    themes = extract_themes(container)
    criteria_count = sum(len(t["criteria"]) for t in themes)
    tests_count = sum(len(c["tests"]) for t in themes for c in t["criteria"])
    at_excluded_count = sum(
        1
        for t in themes
        for c in t["criteria"]
        for test in c["tests"]
        if test.get("agent_scope") == "at_only"
    )
    partial_count = sum(
        1
        for t in themes
        for c in t["criteria"]
        for test in c["tests"]
        if test.get("agent_scope") == "partial"
    )
    human_complement_count = sum(
        1
        for t in themes
        for c in t["criteria"]
        for test in c["tests"]
        if test.get("human_complement_required")
    )

    return {
        "version": "4.1.2",
        "source": html_path.name,
        "counts": {
            "themes": len(themes),
            "criteria": criteria_count,
            "tests": tests_count,
            "agent_scope_at_only": at_excluded_count,
            "agent_scope_partial": partial_count,
            "human_complement_required": human_complement_count,
            "agent_excluded_tests": at_excluded_count,
        },
        "themes": themes,
    }


def validate_counts(data: dict) -> None:
    criteria = data["counts"]["criteria"]
    tests = data["counts"]["tests"]
    if criteria != EXPECTED_CRITERIA or tests != EXPECTED_TESTS:
        raise ValueError(
            f"Count mismatch: expected {EXPECTED_CRITERIA} criteria and {EXPECTED_TESTS} tests, "
            f"got {criteria} criteria and {tests} tests"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract RGAA rules from rules.html")
    parser.add_argument("input", type=Path, nargs="?", default=Path("rules.html"))
    parser.add_argument("-o", "--output", type=Path, default=Path("data/rgaa-rules.json"))
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    data = extract_rules(args.input)
    validate_counts(data)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"Extracted {data['counts']['themes']} themes, "
        f"{data['counts']['criteria']} criteria, "
        f"{data['counts']['tests']} tests "
        f"(at_only={data['counts']['agent_scope_at_only']}, "
        f"partial={data['counts']['agent_scope_partial']}, "
        f"human_complement={data['counts']['human_complement_required']}) "
        f"→ {args.output}"
    )


if __name__ == "__main__":
    main()
