# PDF 论文处理工作流

## 从 PDF 提取文本

当用户提供 PDF 文件路径时，使用以下方法提取文本：

### 方法 1：使用 pymupdf（推荐）

```python
import fitz  # pymupdf

def extract_text_from_pdf(pdf_path):
    """提取 PDF 全文"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text
```

### 方法 2：使用 pymupdf4llm（Markdown 格式）

```python
import pymupdf4llm

def extract_markdown_from_pdf(pdf_path):
    """提取 PDF 为 Markdown 格式"""
    md_text = pymupdf4llm.to_markdown(pdf_path)
    return md_text
```

## 提取图片

### 使用 pymupdf 提取图片（推荐）

```python
import fitz
import os

def extract_images_from_pdf(pdf_path, output_dir, min_size=10000):
    """
    从 PDF 中提取图片

    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录
        min_size: 最小像素数（过滤小图标）

    Returns:
        list: 图片信息列表
    """
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        for img in page.get_images(full=True):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            # 过滤小图片（图标、背景等）
            if pix.width * pix.height < min_size:
                continue

            # 保存图片
            img_path = os.path.join(output_dir, f"fig_{page_num+1}_{len(images)+1}.png")
            pix.save(img_path)
            images.append({
                'path': img_path,
                'page': page_num + 1,
                'width': pix.width,
                'height': pix.height
            })

    doc.close()
    return images
```

### 使用命令行工具

```bash
# 使用 Python 脚本（推荐）
python3 scripts/extract-images.py paper.pdf ./images/

# 带过滤选项
python3 scripts/extract-images.py paper.pdf ./images/ --min-size 50000

# 输出 JSON 报告
python3 scripts/extract-images.py paper.pdf ./images/ --json report.json

# 输出 Markdown 引用
python3 scripts/extract-images.py paper.pdf ./images/ --markdown images.md
```

## 提取关键信息

从提取的文本中识别：
1. **标题**：通常在文档开头
2. **作者**：标题下方
3. **摘要**：Abstract 部分
4. **关键词**：Keywords 部分
5. **DOI**：通常在文档开头或结尾

## 常见问题

### 路径问题
- Windows 路径使用正斜杠 `/` 或双反斜杠 `\\`
- 示例：`D:/Downloads/paper.pdf` 或 `D:\\Downloads\\paper.pdf`

### 编码问题
- 始终使用 `encoding='utf-8'` 保存提取的文本
- 处理特殊字符时可能需要额外清理

### 图片提取问题
- **小图标干扰**：使用 `--min-size` 参数过滤
- **图片质量差**：检查 PDF 中图片的原始分辨率
- **图片不完整**：某些 PDF 使用矢量图，需要特殊处理

## 工作流程

1. 使用 pymupdf 提取全文和图片
2. 保存到临时目录
3. 读取并识别关键部分
4. 按照笔记格式生成结构化内容
5. 将图片复制到笔记目录
6. 保存到 Obsidian 笔记库
