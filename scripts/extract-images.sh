#!/bin/bash
# 从 PDF 提取图片
# 用法: ./extract-images.sh /path/to/paper.pdf /path/to/output/

if [ $# -lt 2 ]; then
    echo "用法: $0 <pdf_file> <output_dir>"
    exit 1
fi

PDF_FILE="$1"
OUTPUT_DIR="$2"

mkdir -p "$OUTPUT_DIR"

echo "🖼️ 正在提取图片..."
pdfimages -png "$PDF_FILE" "$OUTPUT_DIR/fig"

IMAGE_COUNT=$(ls -1 "$OUTPUT_DIR"/*.png 2>/dev/null | wc -l)
echo "✅ 提取完成: $IMAGE_COUNT 张图片"
