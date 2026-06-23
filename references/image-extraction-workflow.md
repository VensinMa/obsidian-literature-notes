# Image Extraction Workflow Reference

## Quick Commands

### Extract Images from PDF

```bash
# Basic extraction
python scripts/extract-images.py paper.pdf "$OBSIDIAN_VAULT_PATH/文献阅读笔记/images/PaperName_Year" --min-size 5000

# With markdown report
python scripts/extract-images.py paper.pdf "$OBSIDIAN_VAULT_PATH/文献阅读笔记/images/PaperName_Year" \
  --min-size 5000 \
  --markdown "$OBSIDIAN_VAULT_PATH/文献阅读笔记/images/PaperName_Year/images.md"
```

### Directory Structure

```
文献阅读笔记/images/PaperName_Year/
├── fig_p01_01.png      # Page 1, image 1
├── fig_p01_02.png      # Page 1, image 2
├── fig_p02_01.png      # Page 2, image 1
├── ...
├── images.md           # Auto-generated markdown references
└── report.json         # Auto-generated image info report
```

## Note Template for Images Section

```markdown
## 提取的图片

> 图片保存路径：`文献阅读笔记/images/PaperName_Year/`

### Figure 1 - 图片标题
![[images/PaperName_Year/fig_p01_01.png]]
- **说明**：图片的中文描述，解释图片内容和意义

### Figure 2 - 图片标题
![[images/PaperName_Year/fig_p02_01.png]]
- **说明**：图片的中文描述
```

## Common Pitfalls

1. **Forgetting image extraction** - ALWAYS extract images, never skip this step
2. **Wrong path format** - Use relative path `![[images/...]]` not absolute path
3. **Missing Chinese description** - Every image must have a Chinese description
4. **Wrong directory naming** - Use `论文简称_年份` format (e.g., `Helixer_2025`)
5. **Image not found in note** - Ensure image files exist before referencing them

## Example: Complete Workflow

```bash
# 1. Extract text
python -c "
import pymupdf
doc = pymupdf.open('paper.pdf')
for i in range(doc.page_count):
    print(doc[i].get_text())
"

# 2. Extract images
python scripts/extract-images.py paper.pdf \
  "D:\OneDrive\文档\Obsidian Vault\文献阅读笔记\images\PaperName_2024" \
  --min-size 5000 \
  --markdown "D:\OneDrive\文档\Obsidian Vault\文献阅读笔记\images\PaperName_2024\images.md"

# 3. Create note with all sections including images
# 4. Verify all 13 checklist items
```
