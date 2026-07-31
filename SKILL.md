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
  13. `## 原文逐段完整翻译`
  14. `## 参考与链接`
- Obsidian image embeds in `![[relative/path.png]]` format.
- No empty required section. Use `未在原文中明确说明` only when the paper genuinely does not provide the information.
- File name format: `阅读笔记｜YYYY-MM-DD｜中文标题｜YYYY-MM-DD.md`.
- **原文翻译是笔记最核心的部分，必须占笔记总篇幅的60%以上。** 翻译必须逐段逐句完整进行，禁止任何形式的偷懒。详见下方「原文翻译强制规范」。

## Quality Rules

- Preserve evidence. Tie claims to paper sections, figures, tables, or quoted terms when possible.
- Do not invent missing metadata. Mark uncertain values as `待核查` and list the reason in `## 参考与链接`.
- Prefer structured tables for metadata, datasets, methods, results, figures, and limitations.
- Translate technical terms consistently. First mention should include English in parentheses, for example `泛基因组（pan-genome）`.
- Keep the user research focus visible in `## 对我的研究启发`; when no focus is provided, infer cautiously from the paper domain.
- Include figure source status for every figure: `publisher-original`, `pdf-extracted`, `not-found`, or `not-applicable`.
- In `## 原文逐段完整翻译`, preserve the original article's heading hierarchy and paragraph order. Translate every paragraph of the main article body, including abstract, introduction, results, discussion, methods/STAR methods, data/code availability, acknowledgments, and author contributions when present. References and supplemental figure/table legends may be summarized unless the user explicitly requests full supplemental translation.

## 原文翻译强制规范

翻译是文献笔记中最重要的部分。用户创建笔记的核心目的之一就是获得完整中文翻译。以下规范必须严格执行，不可协商。

### 翻译完整性要求

- **逐段翻译**：原文的每一个段落都必须独立翻译为一个中文段落，禁止合并多个段落。
- **逐节翻译**：原文的每一个章节（Abstract, Introduction, Methods, Results, Discussion, Acknowledgments 等）都必须翻译，不可跳过任何章节。
- **保留层级**：保留原文的标题层级结构，用 `###`/`####`/`#####` 对应原文的 Section/Subsection/Subsubsection。
- **综述类文章**：综述文章通常较长（10-20页），翻译量大是正常的。不允许因为文章长而缩减翻译内容。
- **图表说明**：Figure legends / Table legends 也必须翻译，放在对应章节内。
- **引用保留**：保留原文中的文献引用标记（如 `(Smith et al., 2024)`），不翻译引用编号。

### 禁止的偷懒行为（Anti-patterns）

以下是明确禁止的行为，如果出现任何一种，说明翻译不合格：

1. ❌ **概括替代翻译**：用"本章介绍了XXX的主要发现"替代完整翻译
2. ❌ **节选翻译**：只翻译每个章节的第一段或最后一段
3. ❌ **合并段落**：将原文3段合并为1段中文
4. ❌ **跳过章节**：遗漏 Methods、Acknowledgments、Author Contributions 等"次要"章节
5. ❌ **要点罗列**：用 bullet point 列表替代段落翻译
6. ❌ **注释替代**：用"此处省略N段"、"以下内容类似"等标记跳过内容
7. ❌ **前重后轻**：Introduction 翻译很详细，Results/Discussion 越来越简略
8. ❌ **只译结论不译过程**：只翻译最终发现，跳过实验过程描述

### 翻译自检清单

完成翻译后，必须逐项检查：

- [ ] Abstract 完整翻译（通常150-300词 → 对应中文段落）
- [ ] Introduction 所有段落已翻译（综述文章通常3-8段）
- [ ] Methods / 技术比较 章节完整翻译
- [ ] Results / 应用章节完整翻译，每个子章节都有
- [ ] Discussion / 展望章节完整翻译
- [ ] Acknowledgments 已翻译
- [ ] 翻译篇幅占笔记总篇幅 ≥ 60%
- [ ] 无上述8种偷懒行为

### 长文章处理策略

对于综述文章（>10页）或长研究文章：

- **不要缩减翻译**：文章越长，翻译量越大，这是正常的
- **分段委派**：如果单次委派无法完成全文翻译，可以先翻译前半部分，再翻译后半部分
- **字数参考**：一篇15页的英文综述，完整翻译通常需要 15,000-25,000 中文字
- **章节标题双语**：每个章节标题用 `### 英文标题（中文翻译）` 格式，方便对照

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
