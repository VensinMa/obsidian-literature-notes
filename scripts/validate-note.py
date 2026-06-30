#!/usr/bin/env python3
"""Validate standardized Obsidian literature notes."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FRONTMATTER = [
    "title",
    "title_cn",
    "date",
    "published",
    "authors",
    "journal",
    "doi",
    "url",
    "tags",
    "aliases",
    "status",
    "rating",
    "paper_type",
    "research_domain",
    "species",
    "methods",
    "data_type",
    "code_url",
    "data_url",
    "zotero_key",
]

REQUIRED_SECTIONS = [
    "基本信息",
    "核心摘要",
    "研究背景",
    "研究问题与目标",
    "数据与材料",
    "方法流程",
    "主要结果",
    "关键图表解读",
    "结论与意义",
    "创新点、验证与反常识发现",
    "局限性与注意事项",
    "对我的研究启发",
    "原文逐段完整翻译",
    "参考与链接",
]

ALLOWED_STATUS = {"unread", "reading", "read", "revisit"}
PLACEHOLDER_PATTERNS = [
    r"\{\{[^}]+\}\}",
    r"TODO",
    r"待填写",
    r"your\s+",
]

LEGACY_TRANSLATION_SECTIONS = {
    "原文翻译或精读摘录",
    "原文精读摘录",
    "摘要精读",
}


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise ValueError("missing YAML frontmatter opening delimiter")

    normalized = text.replace("\r\n", "\n")
    end = normalized.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing YAML frontmatter closing delimiter")

    return normalized[4:end], normalized[end + 5 :]


def scalar_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*)$", frontmatter)
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def has_key(frontmatter: str, key: str) -> bool:
    return re.search(rf"(?m)^{re.escape(key)}:", frontmatter) is not None


def extract_h2(body: str) -> list[tuple[str, int]]:
    sections = []
    for match in re.finditer(r"(?m)^##\s+(.+?)\s*$", body):
        sections.append((match.group(1).strip(), match.start()))
    return sections


def section_body(body: str, section: str) -> str:
    pattern = rf"(?m)^##\s+{re.escape(section)}\s*$"
    match = re.search(pattern, body)
    if not match:
        return ""
    next_match = re.search(r"(?m)^##\s+", body[match.end() :])
    end = match.end() + next_match.start() if next_match else len(body)
    return body[match.end() : end].strip()


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    try:
        frontmatter, body = split_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]

    for key in REQUIRED_FRONTMATTER:
        if not has_key(frontmatter, key):
            errors.append(f"missing frontmatter field: {key}")

    for key in ["title", "title_cn", "date", "published", "journal", "doi", "url", "status", "rating"]:
        value = scalar_value(frontmatter, key)
        if value is None:
            continue
        if value == "":
            errors.append(f"blank frontmatter field: {key}")

    for key in ["date", "published"]:
        value = scalar_value(frontmatter, key)
        if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            errors.append(f"{key} must use YYYY-MM-DD: {value}")

    status = scalar_value(frontmatter, "status")
    if status and status not in ALLOWED_STATUS:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUS)}: {status}")

    rating = scalar_value(frontmatter, "rating")
    if rating and not re.fullmatch(r"⭐{1,5}", rating):
        errors.append("rating must be 1-5 star characters")

    sections = extract_h2(body)
    found_names = [name for name, _ in sections]
    for section in REQUIRED_SECTIONS:
        count = found_names.count(section)
        if count == 0:
            errors.append(f"missing section: ## {section}")
        elif count > 1:
            errors.append(f"duplicate section: ## {section}")

    positions = {name: pos for name, pos in sections}
    ordered_positions = [positions[s] for s in REQUIRED_SECTIONS if s in positions]
    if ordered_positions != sorted(ordered_positions):
        errors.append("required sections are not in the standard order")

    for section in REQUIRED_SECTIONS:
        content = section_body(body, section)
        if section in positions and len(content) < 10:
            errors.append(f"section is effectively empty: ## {section}")

    for legacy in LEGACY_TRANSLATION_SECTIONS:
        if legacy in found_names:
            errors.append(f"legacy translation section is not allowed: ## {legacy}")

    full_translation = section_body(body, "原文逐段完整翻译")
    if full_translation:
        if len(full_translation) < 1500:
            errors.append("full body translation appears too short; translate the article body paragraph by paragraph")
        banned_translation_markers = ["精读摘录", "摘要精读", "关键概念翻译", "summary only", "仅摘要"]
        for marker in banned_translation_markers:
            if marker in full_translation:
                errors.append(f"full translation section contains summary/excerpt marker: {marker}")

    if "literature" not in frontmatter:
        errors.append("tags should include literature")

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            errors.append(f"placeholder remains: {pattern}")

    figure_section = section_body(body, "关键图表解读")
    if figure_section:
        if "![[images/" not in figure_section and "not-applicable" not in figure_section:
            errors.append("figure section should include Obsidian image embeds or not-applicable status")
        for status_value in ["publisher-original", "pdf-extracted", "not-found", "not-applicable"]:
            if status_value in figure_section:
                break
        else:
            errors.append("figure section must include figure source status values")

    if re.search(r"!\[[^\]]*\]\([^)]+\)", body):
        errors.append("use Obsidian image embeds ![[path]] instead of Markdown image links")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Obsidian literature note.")
    parser.add_argument("note", help="Path to the Markdown note")
    parser.add_argument("--quiet", action="store_true", help="Only set exit code")
    args = parser.parse_args()

    note_path = Path(args.note)
    if not note_path.exists():
        print(f"ERROR: file not found: {note_path}", file=sys.stderr)
        return 2

    errors = validate(note_path)
    if errors:
        if not args.quiet:
            print(f"FAIL: {note_path}")
            for error in errors:
                print(f"- {error}")
        return 1

    if not args.quiet:
        print(f"PASS: {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
