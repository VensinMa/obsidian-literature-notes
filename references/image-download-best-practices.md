# 图片下载最佳实践

## 原图优先策略

### 问题背景
从出版商网站直接下载的图片通常是缩略图（如Nature的/lw685/、/m685/等），分辨率较低。需要通过特殊方式获取原始高清图片。

### 解决方案

#### 1. URL模式替换
Nature/Springer系列的图片URL通常包含尺寸标识，可以通过替换获取原图：

```
缩略图: https://media.springernature.com/lw685/springer-static/image/art%3A...
原图:   https://media.springernature.com/full/springer-static/image/art%3A...
```

**替换规则：**
- `/lw685/` → `/full/`
- `/m685/` → `/full/`
- `/lw[0-9]+/` → `/full/`
- `/m[0-9]+/` → `/full/`

#### 2. 页面链接查找
在论文页面中查找"Full size image"或类似链接：

**常见链接文本：**
- "Full size image"
- "Original"
- "High-resolution"
- "Download"
- "下载"

**常见链接class：**
- `full-size`
- `original`
- `download`

#### 3. 数据属性查找
检查图片元素的data属性：

```html
<img src="thumbnail.jpg" 
     data-full-size="original.jpg"
     data-full="original.jpg"
     data-original="original.jpg">
```

### 出版商特定策略

| 出版商 | 域名 | 原图获取方式 |
|--------|------|--------------|
| Nature | nature.com | URL替换 + 页面链接 |
| Science | science.org | 页面链接 |
| Cell Press | cell.com | 页面链接 |
| Elsevier | elsevier.com | URL模式 |
| Wiley | wiley.com | 页面链接 |
| Springer | springer.com | URL替换 + 页面链接 |

### 验证方法

下载后检查文件大小：
- 原图通常 > 100 KB
- 缩略图通常 < 50 KB
- 错误页面通常 < 1 KB

### 脚本使用

```bash
# 基本用法
python scripts/download-paper-images.py "DOI" "output_dir"

# 完整用法
python scripts/download-paper-images.py "10.1038/s41588-026-02641-8" \
  "./images/" \
  --json "report.json" \
  --markdown "images.md"
```

### 输出报告

JSON报告包含：
```json
{
  "doi": "...",
  "url": "...",
  "publisher": "Nature",
  "total_images": 5,
  "original_count": 5,
  "thumbnail_count": 0,
  "images": [
    {
      "filename": "fig_01.png",
      "is_original": true,
      "file_size": 231424,
      "download_url": "..."
    }
  ]
}
```

### 故障排除

**问题1：下载的图片太小**
- 检查是否为错误页面（< 1KB）
- 尝试其他URL模式

**问题2：无法找到原图链接**
- 检查页面JavaScript是否动态加载
- 尝试不同的选择器模式

**问题3：网络连接问题**
- 检查代理设置
- 增加超时时间

## 更新日志

- 2026-06-25: 初始版本，支持Nature/Springer原图下载
