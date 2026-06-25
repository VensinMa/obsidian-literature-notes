---
name: obsidian-literature-notes
description: >
  将 PDF 学术文献转换为结构化的 Obsidian 笔记，支持 YAML Frontmatter、
  完整中文翻译、图片提取，并可无缝集成到 Zotero。
version: 1.0.0
author: vensin
tags:
  - obsidian
  - literature
  - pdf
  - zotero
  - note-taking
  - academic
  - research
platforms:
  - linux
  - macos
  - windows
requirements:
  - pymupdf
  - pymupdf4llm
  - python3
  - python3-markdown
  - requests
env_vars:
  - ZOTERO_USER_ID
  - ZOTERO_API_KEY
  - OBSIDIAN_VAULT_PATH
---

# Obsidian Literature Notes 📚

将 PDF 学术文献转换为结构化的 Obsidian 笔记，支持与 Zotero 无缝集成。

## 功能特性

- 📄 PDF 文本和图片自动提取
- 🏷️ YAML Frontmatter 自动生成
- 🌐 完整中文翻译支持
- 📚 Zotero Web API 集成
- 📦 批量处理多个 PDF
- 🎨 Markdown → HTML 自动转换

## 安装

### 方式一：Hermes Agent 安装

```bash
hermes skill install obsidian-literature-notes
```

### 方式二：手动安装

```bash
git clone https://github.com/VensinMa/obsidian-literature-notes.git
cd obsidian-literature-notes
./install.sh
```

## 配置

### 1. Zotero API 配置

获取 Zotero API Key：
1. 登录 https://www.zotero.org/settings/keys
2. 创建新的 API Key（勾选读写权限）
3. 记录 User ID 和 API Key

### 2. 环境变量

在 `~/.hermes/.env` 中添加：

```bash
ZOTERO_USER_ID=你的用户ID
ZOTERO_API_KEY=***
OBSIDIAN_VAULT_PATH=/path/to/obsidian/vault
```

或使用配置文件：

```bash
cp scripts/zotero-config.env.example scripts/zotero-config.env
nano scripts/zotero-config.env
```

## 使用方法

### ⚠️ 强制工作流程（必须严格按顺序执行）

> **重要**：每次生成文献笔记必须完成以下所有步骤，不可跳过任何步骤！

#### 步骤清单

| 步骤 | 操作 | 验证点 |
|------|------|--------|
| **1. 提取PDF文本** | 使用pymupdf读取全文 | 获取完整内容 |
| **2. 提取图片** | 运行extract-images.py | 确认图片已保存 |
| **3. 生成笔记** | 按格式模板创建 | 包含所有必填章节 |
| **4. 嵌入图片** | 在笔记中添加图片引用 | 使用`![[path]]`格式 |
| **5. 格式检查** | 对照检查清单验证 | 所有项目打勾 |

#### 步骤详解

**步骤1：提取PDF文本**
```bash
python -c "
import pymupdf
doc = pymupdf.open('paper.pdf')
for i in range(doc.page_count):
    print(doc[i].get_text())
"
```

**步骤2：提取图片（⚠️ 必须执行）**
```bash
# 创建图片目录
mkdir -p "$OBSIDIAN_VAULT_PATH/文献阅读笔记/images/论文简称_年份"

# 提取图片
python scripts/extract-images.py paper.pdf \
  "$OBSIDIAN_VAULT_PATH/文献阅读笔记/images/论文简称_年份" \
  --min-size 5000 \
  --markdown "$OBSIDIAN_VAULT_PATH/文献阅读笔记/images/论文简称_年份/images.md"
```

**步骤3-4：生成笔记并嵌入图片**

笔记末尾必须包含`## 提取的图片`章节，格式如下：
```markdown
## 提取的图片

> 图片保存路径：`文献阅读笔记/images/论文简称_年份/`

### Figure 1 - 图片标题
![[images/论文简称_年份/fig_p01_01.png]]
- **说明**：图片的中文描述

### Figure 2 - 图片标题
![[images/论文简称_年份/fig_p02_01.png]]
- **说明**：图片的中文描述
```

**步骤5：格式检查清单**

完成笔记后，必须对照以下清单逐项检查：

- [ ] YAML Frontmatter包含所有必填字段
- [ ] `rating`使用星星格式（⭐⭐⭐⭐⭐）
- [ ] 包含"基本信息"表格
- [ ] 包含"研究背景"章节
- [ ] 包含"研究方法"章节
- [ ] 包含"研究结果"章节
- [ ] 包含"研究结论"章节
- [ ] 包含"不同寻常/反常识的发现"章节
- [ ] 包含"个人思考与延伸"章节
- [ ] 包含"提取的图片"章节
- [ ] 图片使用`![[path]]`格式嵌入
- [ ] 每张图片有中文说明
- [ ] 包含"原文翻译"章节（如有完整原文）

### 基本用法

在 Hermes Agent 中：

```
请为这个 PDF 做文献笔记：/path/to/paper.pdf
```

### 批量处理

```
请处理这些 PDF：
- /path/to/paper1.pdf
- /path/to/paper2.pdf
```

### Zotero 同步

```
请为这个 PDF 做笔记，并同步到 Zotero：/path/to/paper.pdf
```

### 图片提取

```bash
# 使用 Python 脚本提取图片（推荐）
python scripts/extract-images.py paper.pdf ./images/

# 带过滤选项（过滤小图标）
python scripts/extract-images.py paper.pdf ./images/ --min-size 50000

# 输出 JSON 报告（包含图片信息和图注）
python scripts/extract-images.py paper.pdf ./images/ --json report.json

# 输出 Markdown 格式的图片引用
python scripts/extract-images.py paper.pdf ./images/ --markdown images.md
```

**图片提取特性：**
- ✅ 智能过滤小图标和背景纹理
- ✅ 自动提取图注文本
- ✅ 按页码和位置排序
- ✅ 生成 JSON 报告和 Markdown 引用

## 笔记结构

> ⚠️ **所有章节均为必填项，不可跳过**
> ⚠️ **图片提取是必填步骤，不可跳过任何一张图**
> ⚠️ **YAML字段必须使用 date/published/rating，禁止使用 year/date_read**

生成的笔记必须包含以下章节（按顺序）：

1. **YAML Frontmatter** - 完整的元数据（详见下方格式）
2. **基本信息** - 表格形式展示核心信息
3. **原文翻译** - 摘要、引言、结果、讨论、方法
4. **提取的图片** - ⚠️ 必须包含，使用`![[path]]`格式嵌入
5. **研究背景** - 完整翻译
6. **研究方法** - 完整翻译
7. **研究结果** - 完整翻译所有子章节
8. **研究结论** - 完整翻译
9. **创新点、传统理论验证、反常识发现** - 预期-实际-意义结构
10. **个人思考** - 4个子章节，结合用户研究

---

## 📋 详细格式规范

### 一、YAML Frontmatter 格式规范

```yaml
---
title: "英文原版完整标题（引号包裹）"
title_cn: "中文翻译标题"
date: YYYY-MM-DD          # 笔记创建日期（不可用 date_read 替代）
published: YYYY-MM-DD     # 论文发表日期（不可用 year 替代）
authors:                   # 作者列表（数组格式）
  - Author One
  - Author Two
journal: 期刊名称
doi: "DOI编号"
url: "论文链接"
tags:                      # 标签列表（15-20个）
  - literature
  - 领域标签1
  - 领域标签2
  - 方法标签1
  - 物种标签
  - 工具标签
aliases:                   # 别名（便于搜索）
  - 简称1
  - 简称2
status: read               # 阅读状态：unread/reading/read
rating: ⭐⭐⭐⭐              # 评分：1-5个星星（必须使用星星格式）
---
```

**⚠️ YAML字段命名规范（严格遵守）：**
- **必须使用**：`date`、`published`、`rating`
- **禁止使用**：`year`（用`published`替代）、`date_read`（用`date`替代）
- **rating格式**：必须使用星星格式（⭐⭐⭐⭐⭐），不可用数字

**字段说明：**
| 字段 | 必填 | 格式要求 | 示例 |
|------|------|----------|------|
| `title` | ✅ | 英文原版标题，用双引号包裹 | `"Helixer: ab initio prediction..."` |
| `title_cn` | ✅ | 中文翻译标题，用双引号包裹 | `"Helixer：从头预测真核生物基因模型"` |
| `date` | ✅ | YYYY-MM-DD格式 | `2026-06-23` |
| `published` | ✅ | YYYY-MM-DD格式（必须精确到日） | `2025-11-24` |
| `authors` | ✅ | 数组格式，每个作者一行 | `- Felix Holst` |
| `journal` | ✅ | 期刊全称 | `Nature Methods` |
| `doi` | ✅ | 用双引号包裹 | `"10.1038/s41592-025-02939-1"` |
| `url` | ✅ | 完整URL | `"https://doi.org/..."` |
| `tags` | ✅ | 数组格式，15-20个标签 | `- 基因组学` |
| `aliases` | ✅ | 数组格式，便于搜索的简称 | `- Helixer` |
| `status` | ✅ | 固定值：unread/reading/read | `read` |
| `rating` | ✅ | 星星格式，1-5个⭐ | `⭐⭐⭐⭐` |

---

### 二、基本信息表格格式

```markdown
## 基本信息

| 项目 | 内容 |
|------|------|
| **期刊** | 期刊全称 |
| **卷期** | Volume X, Pages XX-XX |
| **发表日期** | YYYY-MM-DD |
| **DOI** | [DOI链接](https://doi.org/...) |
| **通讯作者** | 作者名 (邮箱) |
| **单位** | 第一作者单位 |
| **代码** | [GitHub链接](https://github.com/...) |
| **物种** | 研究物种名称 |
```

**格式要求：**
- 使用Markdown表格语法
- 表头加粗：`**项目**`、`**内容**`
- DOI使用超链接格式
- 如果没有代码/物种等相关信息，可省略对应行

---

### 三、研究背景格式

```markdown
## 研究背景

**研究领域的重要性：**
- 要点1
- 要点2

**现有方法/研究的局限性：**

1. **问题1**：详细说明
2. **问题2**：详细说明
3. **问题3**：详细说明

**本研究的目标：**
研究目的的简要描述。
```

**格式要求：**
- 使用加粗标题分段
- 局限性使用编号列表
- 每个要点简洁明了

---

### 四、研究方法格式

```markdown
## 研究方法

### 1. 方法名称

**具体步骤：**
1. 步骤一
2. 步骤二
3. 步骤三

**参数设置：**
| 参数 | 值 | 说明 |
|------|-----|------|
| 参数1 | 值1 | 说明1 |

### 2. 方法名称
...
```

**格式要求：**
- 每个方法使用二级标题（###）
- 方法编号递增
- 复杂方法使用表格展示参数
- 可使用代码块展示命令

---

### 五、研究结果格式

```markdown
## 研究结果

### 1. 结果标题

**主要发现：**
- 发现1
- 发现2

**数据支持：**
| 指标 | 组别A | 组别B | 显著性 |
|------|-------|-------|--------|
| 指标1 | 值1 | 值2 | P<0.05 |

**关键结论：**
简要总结该部分的核心发现。

### 2. 结果标题
...
```

**格式要求：**
- 每个结果使用二级标题（###）
- 结果编号递增
- 使用表格展示数据对比
- 每个结果有明确的结论

---

### 六、研究结论格式

```markdown
## 研究结论

1. **结论1**：详细描述
2. **结论2**：详细描述
3. **结论3**：详细描述
4. **结论4**：详细描述
5. **结论5**：详细描述
```

**格式要求：**
- 使用编号列表
- 每条结论加粗标题
- 通常3-6条核心结论

---

### 七、创新点、传统理论验证、反常识发现格式

```markdown
## 创新点、传统理论验证、反常识发现

### [选择以下1-2个子章节，根据文章具体内容]

### 创新点

1. **创新点1标题**
   - 内容：详细描述
   - 意义：这一创新的重要性

### 传统理论验证

1. **验证内容1**
   - 理论：传统理论描述
   - 证据：本文提供的证据
   - 结论：验证结果

### 反常识发现

1. **发现1标题**
   - 预期：通常预期的情况
   - 实际：实际观察到的情况
   - 意义：这一发现的重要性
```

**格式要求：**
- ⚠️ **不是每篇文章都需要三个部分，根据文章具体内容选择其中1-2个子章节**
- 选择依据：
  - **创新点**：文章提出了新方法、新理论、新技术
  - **传统理论验证**：文章验证或推翻了某个传统理论
  - **反常识发现**：文章发现了与常识相悖的结果
- 使用编号列表
- 每个发现包含：预期、实际、意义
- 突出创新性和反直觉的发现

---

### 八、个人思考格式

```markdown
## 个人思考

### 对[研究领域]的启示

1. **启示1**：详细描述
2. **启示2**：详细描述

### 对[用户研究领域]的关联

1. **关联1**：与用户研究的联系
2. **关联2**：可借鉴的方法

### 技术方法的启发

1. **方法1**：可复用的技术
2. **方法2**：改进方向

### 潜在改进方向

1. **方向1**：未来研究方向
2. **方向2**：技术改进点
```

**格式要求：**
- 分4个子章节
- 结合用户研究背景（生物信息学/基因组学/转座子注释）
- 提供具体可操作的见解

---

### 九、提取的图片格式

```markdown
## 提取的图片

> 图片保存路径：`文献阅读笔记/images/论文简称_年份/`

### Figure 1 - 图片标题
![[images/论文简称_年份/fig_p01_01.png]]
- **说明**：图片的中文描述，包括图中展示的内容、关键信息和意义

### Figure 2 - 图片标题
![[images/论文简称_年份/fig_p02_01.png]]
- **说明**：图片的中文描述
```

**格式要求：**
- ⚠️ 必须包含此章节
- 图片使用Obsidian内部链接格式：`![[相对路径]]`
- 每张图片必须有中文说明
- 说明应包含：图片内容、关键信息、研究意义
- 图片标题使用原文Figure编号

---

### 十、原文翻译格式

```markdown
## 原文翻译

### 摘要

[完整的中文翻译]

### 引言

[完整的中文翻译]

### 结果

[完整的中文翻译，保留所有子标题和段落]

### 讨论

[完整的中文翻译]

### 方法

[完整的中文翻译]
```

**格式要求：**
- ⚠️ **必须保留完整段落语句翻译，不得节选或精简概括**
- ⚠️ **无论原文多长，均需完整翻译所有内容**
- 按原文结构分章节翻译
- 保留原文的层级结构和段落划分
- 专业术语首次出现时标注英文

---

## 📝 完整笔记模板

```markdown
---
title: "英文原版完整标题"
title_cn: "中文翻译标题"
date: 2026-06-23
published: 2024-01-15
authors:
  - Author One
  - Author Two
journal: 期刊名称
doi: "DOI编号"
url: "论文链接"
tags:
  - literature
  - 标签1
  - 标签2
  - ...
aliases:
  - 简称1
  - 简称2
status: read
rating: ⭐⭐⭐⭐
---

# 中文翻译标题

## 基本信息

| 项目 | 内容 |
|------|------|
| **期刊** | 期刊全称 |
| **卷期** | Volume X, Pages XX-XX |
| **发表日期** | YYYY-MM-DD |
| **DOI** | [DOI链接](https://doi.org/...) |
| **通讯作者** | 作者名 (邮箱) |
| **单位** | 第一作者单位 |

---

## 原文翻译

### 摘要

[中文翻译]

### 引言

[中文翻译]

### 结果

[中文翻译]

### 讨论

[中文翻译]

### 方法

[中文翻译]

---

## 提取的图片

> 图片保存路径：`文献阅读笔记/images/论文简称_年份/`

### Figure 1 - 图片标题
![[images/论文简称_年份/fig_p01_01.png]]
- **说明**：图片的中文描述

---

## 研究背景

**研究领域的重要性：**
- 要点1
- 要点2

**现有方法/研究的局限性：**

1. **问题1**：详细说明
2. **问题2**：详细说明

**本研究的目标：**
研究目的简述。

---

## 研究方法

### 1. 方法名称

**具体步骤：**
1. 步骤一
2. 步骤二

---

## 研究结果

### 1. 结果标题

**主要发现：**
- 发现1
- 发现2

---

## 研究结论

1. **结论1**：详细描述
2. **结论2**：详细描述

---

## 创新点、传统理论验证、反常识发现

### 创新点

1. **创新点1**
   - 内容：详细描述
   - 意义：重要性

### 传统理论验证

1. **验证内容**
   - 理论：传统理论
   - 证据：本文证据
   - 结论：验证结果

### 反常识发现

1. **发现1**
   - 预期：通常情况
   - 实际：实际情况
   - 意义：重要性

---

## 个人思考

### 对[研究领域]的启示

1. **启示1**：详细描述

### 对[用户研究领域]的关联

1. **关联1**：与用户研究的联系

### 技术方法的启发

1. **方法1**：可复用的技术

### 潜在改进方向

1. **方向1**：未来研究方向
```

---

## 格式检查清单

完成笔记后，必须对照以下清单逐项检查：

**YAML Frontmatter：**
- [ ] 包含所有必填字段（title, title_cn, date, published, authors, journal, doi, url, tags, aliases, status, rating）
- [ ] `date`格式为YYYY-MM-DD
- [ ] `published`格式为YYYY-MM-DD（必须精确到日）
- [ ] `rating`使用星星格式（⭐⭐⭐⭐⭐）
- [ ] 标签数量15-20个

**文件命名：**
- [ ] 格式：阅读笔记｜添加日期YYYY-MM-DD｜中文题目｜发表日期YYYY-MM-DD.md

**笔记内容（按顺序）：**
- [ ] 1. YAML Frontmatter
- [ ] 2. 基本信息表格
- [ ] 3. 原文翻译（完整翻译，不得节选）
- [ ] 4. 提取的图片
- [ ] 5. 研究背景
- [ ] 6. 研究方法
- [ ] 7. 研究结果
- [ ] 8. 研究结论
- [ ] 9. 创新点、传统理论验证、反常识发现（选择1-2个子章节）
- [ ] 10. 个人思考

**图片：**
- [ ] 图片使用`![[path]]`格式嵌入
- [ ] 每张图片有中文说明
- [ ] 图片路径正确
- [ ] 包含"基本信息"表格
- [ ] 包含"研究背景"章节
- [ ] 包含"研究方法"章节
- [ ] 包含"研究结果"章节
- [ ] 包含"研究结论"章节
- [ ] 包含"不同寻常/反常识的发现"章节
- [ ] 包含"个人思考与延伸"章节
- [ ] 包含"提取的图片"章节
- [ ] 包含"原文翻译"章节

**图片：**
- [ ] 图片使用`![[path]]`格式嵌入
- [ ] 每张图片有中文说明
- [ ] 图片路径正确

## 文件命名规范

### 笔记文件

**格式规范**：`阅读笔记｜添加日期YYYY-MM-DD｜中文题目｜发表日期YYYY-MM-DD.md`

| 位置 | 内容 | 说明 |
|------|------|------|
| 第1段 | 阅读笔记 | 固定前缀 |
| 第2段 | 添加日期 | 笔记创建日期，YYYY-MM-DD格式 |
| 第3段 | 中文题目 | 论文中文标题 |
| 第4段 | 发表日期 | 论文发表日期，YYYY-MM-DD格式 |

示例：
```
阅读笔记｜2024-01-15｜泛基因组分析揭示橡树物种气候适应｜2024-01-10.md
阅读笔记｜2026-06-23｜移动mRNA检测通用流程及低温胁迫下异种嫁接优势研究｜2020-03-15.md
```

### 图片目录

```
文献阅读笔记/images/论文简称_年份/
├── fig_p01_01.png
├── fig_p01_02.png
├── fig_p02_01.png
├── ...
├── images.md          # 自动生成的图片引用
└── report.json        # 自动生成的图片信息报告
```

**命名规则**：
- 图片目录：`images/论文简称_年份/`（如 `images/Helixer_2025/`）
- 图片文件：`fig_p页码_序号.png`（如 `fig_p01_01.png`）
- 笔记中引用：使用相对路径 `![[images/论文简称_年份/fig_p01_01.png]]`

## Zotero 集成

### 自动同步

笔记会自动同步到 Zotero：
- Obsidian：Markdown 格式（可编辑）
- Zotero：HTML 格式（集成在文献中）

### 手动添加

```bash
# 单个笔记
python3 scripts/zotero-add-note.py ITEM_KEY /path/to/note.md "tags"

# 批量添加
python3 scripts/zotero-batch-add.py
```

## Tag 规范

按层级组织：
- 文档类型：`literature`, `review`, `preprint`
- 研究领域：`基因组学`, `群体遗传学`
- 技术方法：`泛基因组`, `T2T组装`
- 物种：`人类`, `水稻`, `苹果`
- 专有名词：`EDTA`, `RepeatMasker`

## 故障排除

> 📖 **详细参考**：[image-extraction-workflow.md](references/image-extraction-workflow.md) 包含图片提取的完整工作流和常见问题

### Windows 上 python3 命令不可用
Windows 上 `python3` 可能不存在，使用 `python` 代替：
```bash
python scripts/extract-images.py paper.pdf ./images/
```

### Zotero API 429 错误
请求过于频繁，等待 5 分钟后重试。

### 图片提取失败
安装 pymupdf：
```bash
pip install pymupdf
```

如果遇到问题，检查：
1. PDF 是否为扫描版（需要 OCR）
2. 图片是否为矢量图（无法直接提取）
3. 使用 `--min-size` 参数调整过滤阈值

### 笔记格式问题
确保使用最新版本，脚本会自动转换 Markdown 为 HTML。

## 许可证

MIT License

## 链接

- GitHub: https://github.com/VensinMa/obsidian-literature-notes
- Releases: https://github.com/VensinMa/obsidian-literature-notes/releases
- Issues: https://github.com/VensinMa/obsidian-literature-notes/issues

## 版本管理

### 版本号规范

使用语义化版本号：`v主版本.次版本.修订号`

| 版本类型 | 说明 | 示例 |
|----------|------|------|
| 主版本 | 重大结构变更 | v2.0.0 |
| 次版本 | 新增功能或章节 | v1.1.0 |
| 修订号 | 格式修复或小改动 | v1.0.1 |

### 创建Release流程

每次更新skill后，需执行以下步骤：

1. **提交代码**
```bash
git add -A
git commit -m "更新说明"
```

2. **创建版本标签**
```bash
git tag -a v1.1.0 -m "版本说明"
git push origin v1.1.0
```

3. **创建压缩包**
```bash
git archive --format=zip --prefix=obsidian-literature-notes-v1.1.0/ -o obsidian-literature-notes-v1.1.0.zip v1.1.0
git archive --format=tar.gz --prefix=obsidian-literature-notes-v1.1.0/ -o obsidian-literature-notes-v1.1.0.tar.gz v1.1.0
```

4. **创建GitHub Release**
   - 访问 https://github.com/VensinMa/obsidian-literature-notes/releases/new
   - 选择标签版本
   - 填写Release标题和说明
   - 上传zip和tar.gz压缩包
   - 点击"Publish release"
