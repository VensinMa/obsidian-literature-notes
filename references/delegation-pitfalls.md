# 委派子代理制作文献笔记的常见问题

## 问题1：YAML字段命名不一致

子代理可能生成以下错误字段：
- `year: 2024` → 应为 `published: 2024`
- `date_read: 2026-06-23` → 应为 `date: 2026-06-23`

**预防措施**：在委派prompt中明确指定字段名称。

**修复方法**：
```python
import re
content = re.sub(r'year:\s*\d{4}', f'published: {pub_year}', content)
content = re.sub(r'date_read:\s*(\d{4}-\d{2}-\d{2})', r'date: \1', content)
```

## 问题2：图片提取被跳过

子代理可能只提取文本而忘记提取图片。

**预防措施**：在prompt中将图片提取列为第一步，并指定输出目录。

## 问题3：评分格式错误

子代理可能使用数字评分 `rating: 4` 而非星星格式 `rating: ⭐⭐⭐⭐`。

**预防措施**：在prompt中明确指定星星格式。

## 问题4：文件名格式错误

子代理可能生成不符合规范的文件名。

**规范格式**：`阅读笔记｜YYYY-MM-DD｜中文标题｜YYYY-MM-DD.md`

## 验证脚本

批量验证所有笔记文件的格式：
```bash
cd "D:\OneDrive\文档\Obsidian Vault\文献阅读笔记"
for f in 阅读笔记｜*.md; do
    echo "=== $f ==="
    # 检查文件名格式（4个部分）
    parts=$(echo "$f" | awk -F'｜' '{print NF}')
    # 检查YAML字段
    has_date=$(grep -c "^date:" "$f")
    has_published=$(grep -c "^published:" "$f")
    has_rating=$(grep -c "⭐" "$f")
    # 输出结果
    [ "$parts" -eq 4 ] && echo "✅ 文件名格式" || echo "❌ 文件名格式"
    [ "$has_date" -gt 0 ] && echo "✅ date字段" || echo "❌ date字段"
    [ "$has_published" -gt 0 ] && echo "✅ published字段" || echo "❌ published字段"
    [ "$has_rating" -gt 0 ] && echo "✅ rating字段" || echo "❌ rating字段"
done
```
