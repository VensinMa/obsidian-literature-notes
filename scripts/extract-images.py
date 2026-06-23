#!/usr/bin/env python3
"""
PDF 图片提取工具 - 从学术文献 PDF 中提取高质量图表
用法: python3 extract-images.py <pdf_file> <output_dir> [options]

功能:
- 智能过滤小图片（图标、背景纹理等）
- 按页码和位置排序
- 提取图注文本
- 生成 Markdown 格式的图片引用

依赖: pip install pymupdf Pillow
"""
import os
import sys
import json
import argparse
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:
    print("❌ 缺少 pymupdf 库，请安装: pip install pymupdf")
    sys.exit(1)

def extract_images_from_pdf(pdf_path, output_dir, min_size=10000, min_width=100, min_height=100):
    """
    从 PDF 中提取图片并过滤
    
    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录
        min_size: 最小像素数（宽×高）
        min_width: 最小宽度
        min_height: 最小高度
    
    Returns:
        list: 提取的图片信息列表
    """
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    
    extracted_images = []
    image_counter = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)
        
        for img_idx, img in enumerate(images):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                
                # 过滤小图片
                if pix.width * pix.height < min_size:
                    continue
                if pix.width < min_width or pix.height < min_height:
                    continue
                
                # 转换为 RGB（如果是 CMYK）
                if pix.colorspace and pix.colorspace.n > 3:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                # 保存图片
                image_counter += 1
                img_filename = f"fig_p{page_num+1:02d}_{image_counter:02d}.png"
                img_path = os.path.join(output_dir, img_filename)
                pix.save(img_path)
                
                # 获取图片在页面中的位置
                img_rect = page.get_image_rects(xref)
                position = None
                if img_rect:
                    rect = img_rect[0]
                    position = {
                        'x': rect.x0,
                        'y': rect.y0,
                        'width': rect.width,
                        'height': rect.height
                    }
                
                # 尝试提取图注（图片下方的文本）
                caption = extract_caption_near_image(page, position)
                
                image_info = {
                    'filename': img_filename,
                    'path': img_path,
                    'page': page_num + 1,
                    'index': image_counter,
                    'width': pix.width,
                    'height': pix.height,
                    'size': pix.width * pix.height,
                    'position': position,
                    'caption': caption
                }
                extracted_images.append(image_info)
                
            except Exception as e:
                print(f"⚠️  提取图片时出错 (page {page_num+1}, xref {xref}): {e}")
                continue
    
    doc.close()
    return extracted_images

def extract_caption_near_image(page, image_position):
    """
    尝试从图片下方区域提取图注文本
    
    Args:
        page: PDF 页面对象
        image_position: 图片位置信息
    
    Returns:
        str: 图注文本（如果找到）
    """
    if not image_position:
        return None
    
    # 定义图注搜索区域（图片下方 50 像素内）
    caption_rect = fitz.Rect(
        image_position['x'] - 10,
        image_position['y'] + image_position['height'],
        image_position['x'] + image_position['width'] + 10,
        image_position['y'] + image_position['height'] + 80
    )
    
    # 提取该区域的文本
    try:
        caption_text = page.get_text("text", clip=caption_rect).strip()
        if caption_text and len(caption_text) > 10:
            # 清理文本
            lines = caption_text.split('\n')
            # 过滤掉太短的行
            valid_lines = [line.strip() for line in lines if len(line.strip()) > 5]
            if valid_lines:
                return ' '.join(valid_lines[:2])  # 只取前两行
    except:
        pass
    
    return None

def generate_markdown_references(images, pdf_filename=None):
    """
    生成 Markdown 格式的图片引用
    
    Args:
        images: 图片信息列表
        pdf_filename: PDF 文件名（可选）
    
    Returns:
        str: Markdown 文本
    """
    if not images:
        return "未找到符合条件的图片。"
    
    md_lines = []
    md_lines.append("## 提取的图片\n")
    
    for img in images:
        md_lines.append(f"### 图 {img['index']} (第 {img['page']} 页)")
        md_lines.append(f"![{img['filename']}]({img['filename']})")
        md_lines.append(f"- **尺寸**: {img['width']} × {img['height']} 像素")
        if img['caption']:
            md_lines.append(f"- **图注**: {img['caption']}")
        md_lines.append("")
    
    return '\n'.join(md_lines)

def main():
    parser = argparse.ArgumentParser(
        description='从学术文献 PDF 中提取高质量图表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 extract-images.py paper.pdf ./images/
  python3 extract-images.py paper.pdf ./images/ --min-size 50000
  python3 extract-images.py paper.pdf ./images/ --json report.json
        """
    )
    
    parser.add_argument('pdf_file', help='PDF 文件路径')
    parser.add_argument('output_dir', help='图片输出目录')
    parser.add_argument('--min-size', type=int, default=10000,
                        help='最小像素数 (宽×高)，默认: 10000')
    parser.add_argument('--min-width', type=int, default=100,
                        help='最小宽度，默认: 100')
    parser.add_argument('--min-height', type=int, default=100,
                        help='最小高度，默认: 100')
    parser.add_argument('--json', type=str, default=None,
                        help='输出 JSON 格式的图片信息')
    parser.add_argument('--markdown', type=str, default=None,
                        help='输出 Markdown 格式的图片引用')
    parser.add_argument('--quiet', action='store_true',
                        help='静默模式')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_file):
        print(f"❌ 文件不存在: {args.pdf_file}")
        sys.exit(1)
    
    if not args.quiet:
        print(f"📄 正在处理: {args.pdf_file}")
        print(f"📁 输出目录: {args.output_dir}")
        print(f"🔍 过滤条件: 最小 {args.min_size} 像素, 最小尺寸 {args.min_width}×{args.min_height}")
    
    # 提取图片
    images = extract_images_from_pdf(
        args.pdf_file,
        args.output_dir,
        min_size=args.min_size,
        min_width=args.min_width,
        min_height=args.min_height
    )
    
    if not args.quiet:
        print(f"\n✅ 提取完成: {len(images)} 张图片")
        
        # 显示图片信息
        for img in images:
            caption_info = f" - {img['caption'][:50]}..." if img['caption'] else ""
            print(f"  📷 {img['filename']}: {img['width']}×{img['height']}{caption_info}")
    
    # 输出 JSON 报告
    if args.json:
        report = {
            'pdf_file': args.pdf_file,
            'output_dir': args.output_dir,
            'total_images': len(images),
            'images': images
        }
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        if not args.quiet:
            print(f"\n📊 JSON 报告已保存: {args.json}")
    
    # 输出 Markdown 引用
    if args.markdown:
        md_content = generate_markdown_references(images)
        with open(args.markdown, 'w', encoding='utf-8') as f:
            f.write(md_content)
        if not args.quiet:
            print(f"📝 Markdown 引用已保存: {args.markdown}")

if __name__ == "__main__":
    main()
