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

## 问题5：原文翻译不完整（最常见、最严重的问题）

子代理可能以各种方式偷懒翻译：

### 典型偷懒模式

1. **概括替代**：用"本章主要介绍了微嫁接的优势"替代完整段落翻译
2. **节选翻译**：每个章节只翻译首尾段，中间段落跳过
3. **合并段落**：原文5段合并为1段中文
4. **前重后轻**：Introduction翻译详细，Results/Discussion越来越简略
5. **跳过章节**：遗漏 Methods、Acknowledgments 等章节
6. **要点罗列**：用bullet list替代段落翻译

### 预防措施

在委派prompt中必须包含以下强制指令：

```
【翻译强制规范】
- 逐段逐句翻译全文，不可概括、节选、合并或跳过任何段落
- 翻译必须占笔记总篇幅60%以上
- 综述文章翻译通常需要15,000-25,000字
- 禁止使用"本章介绍了..."等概括性语句替代翻译
- 必须翻译所有章节，包括Methods和Acknowledgments
- 完成后自检：每个章节的段落数是否与原文一致？
```

### 验证方法

```python
# 检查翻译篇幅占比
lines = open(note_file).readlines()
total = len(lines)
trans_start = next(i for i, l in enumerate(lines) if '原文翻译' in l or '原文逐段' in l)
trans_end = next((i for i, l in enumerate(lines[trans_start+1:], trans_start+1) if l.startswith('## ')), total)
trans_lines = trans_end - trans_start
ratio = trans_lines / total
if ratio < 0.5:
    print(f"⚠️ 翻译占比仅{ratio:.0%}，可能不完整")
```

## 问题6：YAML字段命名不一致

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
