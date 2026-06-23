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

生成的笔记必须包含以下章节（按顺序）：

1. **YAML Frontmatter** - 完整的元数据（详见下方格式）
2. **基本信息** - 表格形式展示核心信息
3. **研究背景** - 完整翻译
4. **研究方法** - 完整翻译
5. **研究结果** - 完整翻译所有子章节
6. **研究结论** - 完整翻译
7. **不同寻常/反常识的发现**
8. **个人思考与延伸**
9. **提取的图片** - ⚠️ 必须包含，使用`![[path]]`格式嵌入
10. **原文翻译** - 摘要、引言、结果、讨论

### YAML Frontmatter 格式规范

```yaml
---
title: "英文原版完整标题（引号包裹）"
title_cn: "中文翻译标题"
date: YYYY-MM-DD          # 笔记创建日期
published: YYYY-MM-DD     # 论文发表日期
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
rating: ⭐⭐⭐⭐              # 评分：1-5个星星
---
```

**字段说明：**
| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 英文原版标题 |
| `title_cn` | ✅ | 中文翻译标题 |
| `date` | ✅ | 笔记创建日期 |
| `published` | ✅ | 论文发表日期 |
| `authors` | ✅ | 作者列表（数组） |
| `journal` | ✅ | 期刊名称 |
| `doi` | ✅ | DOI 编号 |
| `url` | ✅ | 论文链接 |
| `tags` | ✅ | 标签列表（至少15个） |
| `aliases` | ✅ | 别名列表 |
| `status` | ✅ | 阅读状态 |
| `rating` | ✅ | 评分（⭐⭐⭐⭐⭐） |

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
- Issues: https://github.com/VensinMa/obsidian-literature-notes/issues
