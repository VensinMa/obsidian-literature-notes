# Obsidian Literature Notes 📚

一个强大的 Herm..._notes` 工具，用于将 PDF 学术文献转换为结构化的 Obsidian 笔记，并支持与 Zotero 无缝集成。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-blue.svg)](https://hermes-agent.nousresearch.com)

## ✨ 特性

- 📄 **PDF → Obsidian 笔记**：自动提取文本、图片，生成结构化笔记
- 🏷️ **YAML Frontmatter**：自动生成标题、作者、DOI、Tags 等元数据
- 🌐 **完整中文翻译**：支持摘要、引言、结果、讨论的完整翻译
- 🖼️ **图片提取**：自动从 PDF 提取图片并保存
- 📚 **Zotero 集成**：通过 Web API 直接添加笔记到 Zotero
- 📦 **批量处理**：支持同时处理多个 PDF 文件
- 🎨 **格式保持**：Markdown → HTML 自动转换，保持格式完整

## 🚀 快速开始

### 方式一：Hermes Agent Skill 安装（推荐）

```bash
# 在 Hermes Agent 中运行
hermes skill install obsidian-literature-notes
```

### 方式二：手动安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/obsidian-literature-notes.git
cd obsidian-literature-notes

# 运行安装脚本
chmod +x install.sh
./install.sh
```

### 方式三：直接复制 Skill

```bash
# 复制 skill 到 Hermes Agent
cp -r . ~/.hermes/skills/obsidian-literature-notes/
```

## ⚙️ 配置

### 1. Zotero API 配置

获取 Zotero API Key：
1. 登录 https://www.zotero.org
2. 访问 https://www.zotero.org/settings/keys
3. 创建新的 API Key（勾选读写权限）
4. 记录 User ID 和 API Key

### 2. 环境变量配置

创建配置文件：

```bash
# 编辑配置文件
nano ~/.hermes/skills/obsidian-literature-notes/scripts/zotero-config.env
```

添加以下内容：

```bash
export ZOTERO_USER_ID="你的用户ID"
export ZOTERO_API_KEY="你的API密钥"
export ZOTERO_API="https://api.zotero.org/users/$ZOTERO_USER_ID"
export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"
export OBSIDIAN_LITERATURE_PATH="$OBSIDIAN_VAULT_PATH/文献阅读笔记"
```

### 3. Obsidian Vault 配置

在 `~/.hermes/.env` 中添加：

```bash
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
```

## 📖 使用方法

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
- /path/to/paper3.pdf
```

### 指定 Zotero 同步

```
请为这个 PDF 做笔记，并同步到 Zotero：/path/to/paper.pdf
```

## 📁 笔记结构

生成的笔记包含以下部分：

```markdown
---
title: "英文原标题"
title_cn: "中文翻译标题"
date: 2024-01-15
published: 2024-01-10
authors: [...]
journal: "Journal Name"
doi: "https://doi.org/..."
tags: [literature, 基因组学, ...]
---

# 中文标题

## 文献信息
| 项目 | 内容 |
|------|------|
| 标题 | ... |
| 期刊 | ... |

## 研究背景
...

## 研究方法
...

## 研究结果
...

## 研究结论
...

## 不同寻常/反常识的发现
...

## 个人思考与延伸
...

## 图片及图注
![图 1. 中文图题](figures/paper/fig-001.png)

## 原文翻译
### 摘要
...
### 引言
...
### 结果
...
### 讨论
...
```

## 🏷️ Tag 规范

Tags 按以下层级组织：

| 类别 | 示例 |
|------|------|
| 文档类型 | `literature`, `review`, `preprint` |
| 研究领域 | `基因组学`, `群体遗传学`, `进化生物学` |
| 技术方法 | `泛基因组`, `T2T组装`, `k-mer` |
| 特征元素 | `TE`, `转座子`, `着丝粒`, `卫星DNA` |
| 物种 | `人类`, `水稻`, `苹果`, `橡树` |
| 应用 | `注释工具`, `变异检测`, `抗病性` |
| 专有名词 | `EDTA`, `RepeatMasker`, `BRAKER` |

详见 [Tag Guidelines](references/tag-guidelines.md)

## 📚 Zotero 集成

### 自动同步

配置完成后，笔记会自动同步到 Zotero：

1. **Obsidian 笔记**：Markdown 格式，可编辑
2. **Zotero 笔记**：HTML 格式，集成在文献中
3. **Zotero 附件**：备份副本

### 手动添加

```bash
# 添加单个笔记
python3 scripts/zotero-add-note.py ITEM_KEY /path/to/note.md "tags"

# 批量添加
python3 scripts/zotero-batch-add.py
```

详见 [Zotero Setup Guide](references/zotero-setup.md)

## 🔧 故障排除

### 常见问题

**Q: Zotero API 返回 429 错误**
A: 请求过于频繁，等待 5 分钟后重试。

**Q: 笔记格式在 Zotero 中显示不正确**
A: 确保使用 HTML 格式，脚本会自动转换。

**Q: 图片提取失败**
A: 安装 poppler-utils：`sudo apt install poppler-utils`

详见 [Troubleshooting Guide](references/troubleshooting.md)

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Hermes Agent](https://hermes-agent.nousresearch.com) - AI 助手框架
- [Obsidian](https://obsidian.md) - 笔记应用
- [Zotero](https://www.zotero.org) - 文献管理工具

## 📧 联系方式

- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/obsidian-literature-notes/issues)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
