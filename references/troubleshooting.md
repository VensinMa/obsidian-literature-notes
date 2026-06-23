# 故障排除指南

## 安装问题

### pdftotext 未找到
```bash
# Ubuntu/Debian
sudo -S -p '' apt install poppler-utils

# macOS
brew install poppler
```

### python3-markdown 未找到
```bash
# Ubuntu/Debian
sudo -S -p '' apt install python3-markdown

# macOS
brew install python-markdown

# 或使用 pip
pip3 install markdown
```

## Zotero API 问题

### 401 Unauthorized
- API Key 无效或已过期
- 解决：重新创建 API Key

### 403 Forbidden
- API Key 权限不足
- 解决：确保勾选了读写权限

### 429 Too Many Requests
- 请求过于频繁
- 解决：等待 5 分钟后重试

### 404 Not Found
- Item Key 不存在
- 解决：检查文献是否已导入 Zotero

## 笔记格式问题

### 笔记在 Zotero 中格式丢失
- 原因：发送了纯 Markdown 而非 HTML
- 解决：使用最新版本脚本，会自动转换

### 笔记没有标题
- 原因：未在笔记开头添加标题
- 解决：确保笔记以 `# 标题` 开头

## 图片提取问题

### 图片提取失败
```bash
# 检查 pdftotext 是否安装
which pdfimages

# 手动提取
pdfimages -png /path/to/paper.pdf /output/dir/fig
```

### 图片质量差
- 原因：PDF 中图片分辨率低
- 解决：使用 `pdftoppm` 提取整页图片

```bash
pdftoppm -png -r 300 /path/to/paper.pdf /output/dir/page
```

## 联系支持

如遇到其他问题，请提交 Issue：
https://github.com/VensinMa/obsidian-literature-notes/issues
