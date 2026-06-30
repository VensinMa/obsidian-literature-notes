---
name: obsidian-literature-notes
description: Convert academic PDFs, DOI pages, or paper metadata into standardized, structured Obsidian literature notes with YAML frontmatter, Chinese summaries/translations, figure extraction, tag normalization, and optional Zotero note sync. Use when the user asks to create, standardize, validate, batch-process, or sync Obsidian/Zotero literature notes from papers or PDFs.
---

# Obsidian Literature Notes

Create a research-grade Obsidian note from an academic paper. Prioritize reproducible extraction, stable section order, complete metadata, figure traceability, and final validation.

## Core Workflow

Follow this order for every paper unless the user explicitly narrows the task.

1. Identify inputs: PDF path, DOI, paper URL, target Obsidian vault, Zotero sync preference, and any user research focus.
2. Extract metadata: title, Chinese title, authors, journal, publication date, DOI, URL, affiliations, species/system, code/data links, and keywords.
3. Extract PDF text. Prefer full text extraction with PyMuPDF or `pymupdf4llm`; preserve headings, tables, figure captions, equations, and citation markers when useful.
4. Count figures and tables before extraction:

   ```bash
   python scripts/count-figures.py paper.pdf --json count-report.json --markdown count-report.md
   ```

5. Acquire figures. Prefer publisher original images by DOI; fall back to PDF extraction.

   ```bash
   python scripts/download-paper-images.py "10.xxxx/xxxxx" "images/PaperShort_Year" --markdown images.md --json images.json
   python scripts/extract-images.py paper.pdf "images/PaperShort_Year" --min-size 5000 --markdown images.md --json images.json
   ```

6. Draft the note using `templates/note-template.md` and the required section order in `references/note-standard.md`.
7. Normalize tags using `references/tag-guidelines.md`.
8. Validate the note:

   ```bash
   python scripts/validate-note.py "阅读笔记｜YYYY-MM-DD｜中文标题｜YYYY-MM-DD.md"
   ```

9. If Zotero sync is requested, read `references/zotero-setup.md` and use:

   ```bash
   python scripts/zotero-add-note.py ITEM_KEY note.md "tag1,tag2"
   ```

## Required Output Contract

Every note must be a single Markdown file suitable for Obsidian and must include:

- YAML frontmatter with only normalized fields from `templates/frontmatter.yaml`.
- Stable section order:
  1. `## 基本信息`
  2. `## 核心摘要`
  3. `## 研究背景`
  4. `## 研究问题与目标`
  5. `## 数据与材料`
  6. `## 方法流程`
  7. `## 主要结果`
  8. `## 关键图表解读`
  9. `## 结论与意义`
  10. `## 创新点、验证与反常识发现`
  11. `## 局限性与注意事项`
  12. `## 对我的研究启发`
  13. `## 原文翻译或精读摘录`
  14. `## 参考与链接`
- Obsidian image embeds in `![[relative/path.png]]` format.
- No empty required section. Use `未在原文中明确说明` only when the paper genuinely does not provide the information.
- File name format: `阅读笔记｜YYYY-MM-DD｜中文标题｜YYYY-MM-DD.md`.

## Quality Rules

- Preserve evidence. Tie claims to paper sections, figures, tables, or quoted terms when possible.
- Do not invent missing metadata. Mark uncertain values as `待核查` and list the reason in `## 参考与链接`.
- Prefer structured tables for metadata, datasets, methods, results, figures, and limitations.
- Translate technical terms consistently. First mention should include English in parentheses, for example `泛基因组（pan-genome）`.
- Keep the user research focus visible in `## 对我的研究启发`; when no focus is provided, infer cautiously from the paper domain.
- Include figure source status for every figure: `publisher-original`, `pdf-extracted`, `not-found`, or `not-applicable`.

## Resource Map

Read these files only when relevant:

- `references/note-standard.md`: required note schema, section templates, and validation checklist.
- `references/image-extraction-workflow.md`: PDF image extraction commands and directory layout.
- `references/image-download-best-practices.md`: publisher original image download strategy.
- `references/pdf-processing.md`: text extraction options.
- `references/tag-guidelines.md`: normalized tag categories.
- `references/zotero-setup.md`: Zotero API setup and sync workflow.
- `references/delegation-pitfalls.md`: common failures when delegating note creation.

## Dependencies

Install Python dependencies from `requirements.txt`. Optional system dependencies are `poppler-utils`, `curl`, and `jq` for some legacy workflows.

On Windows, use `python` instead of `python3` if `python3` is unavailable.
