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

生成的笔记包含：

1. **YAML Frontmatter** - 元数据（标题、作者、DOI、Tags）
2. **文献信息** - 基本信息表格
3. **研究背景** - 完整翻译
4. **研究方法** - 完整翻译
5. **研究结果** - 完整翻译所有子章节
6. **研究结论** - 完整翻译
7. **不同寻常/反常识的发现**
8. **个人思考与延伸**
9. **图片及图注** - 提取的图片和翻译的图注
10. **原文翻译** - 摘要、引言、结果、讨论

## 文件命名规范

```
阅读笔记｜YYYY-MM-DD｜中文标题｜YYYY-MM-DD.md
```

示例：
```
阅读笔记｜2024-01-15｜泛基因组分析揭示橡树物种气候适应｜2024-01-10.md
```

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
