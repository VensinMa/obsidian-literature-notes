# Obsidian Literature Note Standard

Use this standard when creating or validating literature notes. The goal is a note that is searchable, comparable across papers, and useful for later research synthesis.

## Frontmatter Schema

Use the fields below in this order.

```yaml
---
title: "Original English title"
title_cn: "中文标题"
date: YYYY-MM-DD
published: YYYY-MM-DD
authors:
  - Author One
  - Author Two
journal: "Journal or repository name"
doi: "10.xxxx/xxxxx"
url: "https://..."
tags:
  - literature
  - 研究领域
  - 技术方法
aliases:
  - Paper short name
status: read
rating: ⭐⭐⭐⭐
paper_type: research-article
research_domain:
  - genomics
species:
  - "Species name or 未涉及"
methods:
  - "Method name"
data_type:
  - "sequencing / phenotype / image / simulation / text"
code_url: "未提供"
data_url: "未提供"
zotero_key: "未同步"
---
```

Rules:
- `date` is the note creation date.
- `published` must be a full date when available. If only year is known, use `YYYY-01-01` and state uncertainty in `## 参考与链接`.
- `status` must be one of `unread`, `reading`, `read`, `revisit`.
- `rating` must use 1-5 star characters, not a number.
- Prefer `未提供`, `未涉及`, or `待核查` over blank values.

## Required Section Order

### 基本信息

Use a two-column table. Include at least title, Chinese title, journal, publication date, DOI, first author, corresponding author, institution, paper type, species/system, code link, data link, and figure acquisition status.

### 核心摘要

Use exactly four bullets:
- **一句话概括**:
- **核心问题**:
- **主要发现**:
- **为什么重要**:

### 研究背景

Explain the field context, prior limitations, and why this paper is needed. Prefer 2-4 short paragraphs or a compact table.

### 研究问题与目标

Use a table:

| 层级 | 内容 | 原文依据 |
|---|---|---|
| 总目标 | ... | Abstract/Introduction |
| 问题1 | ... | ... |
| 问题2 | ... | ... |

### 数据与材料

Use a table:

| 数据/材料 | 规模 | 来源 | 用途 | 备注 |
|---|---:|---|---|---|
| ... | ... | ... | ... | ... |

### 方法流程

Represent the workflow as ordered steps. Include tools, parameters, thresholds, models, and versions when reported.

| 步骤 | 方法/工具 | 输入 | 输出 | 关键参数 |
|---:|---|---|---|---|
| 1 | ... | ... | ... | ... |

### 主要结果

Group results by the paper's logical result sections. Each result block should include:
- **发现**:
- **证据**:
- **解释**:
- **关联图表**:

### 关键图表解读

Every major figure/table should have a row.

| 图表 | 来源状态 | 文件/链接 | 展示内容 | 关键结论 | 笔记中引用 |
|---|---|---|---|---|---|
| Fig. 1 | publisher-original | `images/.../fig1.png` | ... | ... | `![[images/.../fig1.png]]` |

Use source status values:
- `publisher-original`
- `pdf-extracted`
- `not-found`
- `not-applicable`

### 结论与意义

List 3-6 conclusions. For each conclusion, state the practical or theoretical meaning.

### 创新点、验证与反常识发现

Choose only relevant subsections:
- `### 创新点`
- `### 传统理论验证或修正`
- `### 反常识发现`

Each item should include `内容`, `证据`, and `意义`.

### 局限性与注意事项

Use a table:

| 类型 | 局限或风险 | 对解读的影响 | 后续验证 |
|---|---|---|---|
| 数据 | ... | ... | ... |

### 对我的研究启发

Make this actionable. Include transferable methods, reusable datasets, possible experiments, and caution points. If the user's research focus is unknown, state the inferred focus.

### 原文翻译或精读摘录

For full translation requests, preserve the paper's heading hierarchy and translate all content. For summary requests, include important original terms and concise Chinese explanations.

### 参考与链接

Include DOI, paper URL, code/data links, image download sources, extraction reports, Zotero key, and unresolved metadata uncertainties.

## Final Validation Checklist

- Frontmatter parses as YAML.
- Required frontmatter fields exist and are not blank.
- Required sections appear once and in the correct order.
- `date` and `published` use `YYYY-MM-DD`.
- `rating` uses star characters.
- Tags include `literature` and at least two domain/method/species tags.
- Figures are counted before extraction.
- Every listed figure has a source status.
- Obsidian embeds use `![[relative/path]]`.
- Required tables are present.
- No placeholder such as `{{title}}`, `待填写`, or `TODO` remains.
