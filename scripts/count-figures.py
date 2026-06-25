#!/usr/bin/env python3
"""
图片计数工具 - 根据文档内容判断论文中图片数量
用法: python count-figures.py <pdf_file> [options]

功能:
- 识别多种图片标识格式（Fig/Figure/FIG等）
- 区分主图和附图（Extended Data Fig等）
- 生成详细的图片清单
- 验证图片提取完整性

依赖: pip install pymupdf
"""
import os
import sys
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

try:
    import pymupdf
except ImportError:
    print("❌ 缺少 pymupdf 库，请安装: pip install pymupdf")
    sys.exit(1)


# 图片标识模式
FIGURE_PATTERNS = {
    # 主图模式
    'main_fig': [
        r'Fig(?:\.|ure)?\s*(\d+)',           # Fig 1, Fig. 1, Figure 1
        r'FIG(?:\.|URE)?\s*(\d+)',           # FIG 1, FIG. 1, FIGURE 1
        r'Fig(?:\.|ure)?\.?\s*(\d+)',        # Fig.1, Figure1
        r'FIG(?:\.|URE)?\.?\s*(\d+)',        # FIG.1, FIGURE1
        r'图\s*(\d+)',                        # 图1, 图 1
        r'Figure\s*(\d+)',                    # Figure 1
        r'FIGURE\s*(\d+)',                    # FIGURE 1
    ],
    # 附图模式
    'extended_fig': [
        r'Extended\s+Data\s+Fig(?:\.|ure)?\s*(\d+)',  # Extended Data Fig 1
        r'Extended\s+Data\s+Figure\s*(\d+)',          # Extended Data Figure 1
        r'Extended\s+Fig(?:\.|ure)?\s*(\d+)',         # Extended Fig 1
        r'Ext(?:\.|ended)?\s+Fig(?:\.|ure)?\s*(\d+)', # Ext. Fig 1
        r'Supplementary\s+Fig(?:\.|ure)?\s*(\d+)',    # Supplementary Fig 1
        r'Supp(?:\.|lementary)?\s+Fig(?:\.|ure)?\s*(\d+)', # Supp. Fig 1
        r'Supplemental\s+Fig(?:\.|ure)?\s*(\d+)',     # Supplemental Fig 1
        r'附图\s*(\d+)',                               # 附图1
        r'补充图\s*(\d+)',                             # 补充图1
    ],
    # 表格模式
    'table': [
        r'Table\s*(\d+)',                     # Table 1
        r'TABLE\s*(\d+)',                     # TABLE 1
        r'Tab(?:\.|le)?\s*(\d+)',             # Tab 1, Tab. 1
        r'表\s*(\d+)',                         # 表1
    ],
    # 附表模式
    'extended_table': [
        r'Extended\s+Data\s+Table\s*(\d+)',   # Extended Data Table 1
        r'Supplementary\s+Table\s*(\d+)',     # Supplementary Table 1
        r'Supp(?:\.|lementary)?\s+Table\s*(\d+)', # Supp. Table 1
        r'附表\s*(\d+)',                       # 附表1
        r'补充表\s*(\d+)',                     # 补充表1
    ]
}

# 图片说明模式（图注）
CAPTION_PATTERNS = [
    r'Fig(?:\.|ure)?\s*\d+[\.:]\s*(.+?)(?:\n|$)',
    r'FIG(?:\.|URE)?\s*\d+[\.:]\s*(.+?)(?:\n|$)',
    r'Extended\s+Data\s+Fig(?:\.|ure)?\s*\d+[\.:]\s*(.+?)(?:\n|$)',
    r'Supplementary\s+Fig(?:\.|ure)?\s*\d+[\.:]\s*(.+?)(?:\n|$)',
]


def extract_text_from_pdf(pdf_path, pages=None):
    """从PDF提取文本"""
    doc = pymupdf.open(pdf_path)
    text_blocks = []
    
    if pages is None:
        pages = range(doc.page_count)
    
    for page_num in pages:
        page = doc[page_num]
        text = page.get_text()
        text_blocks.append({
            'page': page_num + 1,
            'text': text
        })
    
    doc.close()
    return text_blocks


def count_figures_in_text(text_blocks):
    """统计文本中的图片数量"""
    figures = {
        'main_fig': defaultdict(list),
        'extended_fig': defaultdict(list),
        'table': defaultdict(list),
        'extended_table': defaultdict(list)
    }
    
    for block in text_blocks:
        page_num = block['page']
        text = block['text']
        
        for category, patterns in FIGURE_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    fig_num = match.group(1)
                    # 记录图片出现的页码
                    if page_num not in figures[category][fig_num]:
                        figures[category][fig_num].append(page_num)
    
    return figures


def extract_captions(text_blocks, figure_type='main_fig'):
    """提取图注"""
    captions = {}
    
    for block in text_blocks:
        text = block['text']
        
        for pattern in CAPTION_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                fig_match = re.search(r'(?:Fig(?:\.|ure)?|FIG(?:\.|URE)?)\s*(\d+)', match.group(0))
                if fig_match:
                    fig_num = fig_match.group(1)
                    caption = match.group(1).strip()
                    # 取最长的图注
                    if fig_num not in captions or len(caption) > len(captions[fig_num]):
                        captions[fig_num] = caption
    
    return captions


def analyze_pdf(pdf_path, output_json=None, output_markdown=None):
    """分析PDF中的图片数量"""
    print("=" * 60)
    print("📊 论文图片计数工具")
    print("=" * 60)
    print(f"📄 文件: {pdf_path}")
    
    # 提取文本
    print("\n📖 提取文本...")
    text_blocks = extract_text_from_pdf(pdf_path)
    print(f"  ✅ 提取完成，共 {len(text_blocks)} 页")
    
    # 统计图片
    print("\n🔍 统计图片...")
    figures = count_figures_in_text(text_blocks)
    
    # 提取图注
    print("📝 提取图注...")
    main_captions = extract_captions(text_blocks, 'main_fig')
    extended_captions = extract_captions(text_blocks, 'extended_fig')
    
    # 生成报告
    report = {
        'pdf_file': pdf_path,
        'total_pages': len(text_blocks),
        'figures': {
            'main_fig': {
                'count': len(figures['main_fig']),
                'numbers': sorted(figures['main_fig'].keys(), key=lambda x: int(x)),
                'pages': {k: v for k, v in figures['main_fig'].items()}
            },
            'extended_fig': {
                'count': len(figures['extended_fig']),
                'numbers': sorted(figures['extended_fig'].keys(), key=lambda x: int(x)),
                'pages': {k: v for k, v in figures['extended_fig'].items()}
            },
            'table': {
                'count': len(figures['table']),
                'numbers': sorted(figures['table'].keys(), key=lambda x: int(x)),
                'pages': {k: v for k, v in figures['table'].items()}
            },
            'extended_table': {
                'count': len(figures['extended_table']),
                'numbers': sorted(figures['extended_table'].keys(), key=lambda x: int(x)),
                'pages': {k: v for k, v in figures['extended_table'].items()}
            }
        },
        'captions': {
            'main_fig': main_captions,
            'extended_fig': extended_captions
        }
    }
    
    # 打印统计结果
    print("\n" + "=" * 60)
    print("📊 图片统计结果")
    print("=" * 60)
    
    print(f"\n📈 主图 (Main Figures):")
    print(f"  数量: {report['figures']['main_fig']['count']}")
    if report['figures']['main_fig']['numbers']:
        print(f"  编号: {', '.join(report['figures']['main_fig']['numbers'])}")
        print(f"  页码: ", end="")
        for fig_num in report['figures']['main_fig']['numbers']:
            pages = report['figures']['main_fig']['pages'][fig_num]
            print(f"Fig {fig_num} (p.{','.join(map(str, pages))})", end="  ")
        print()
    
    print(f"\n📈 附图 (Extended Data Figures):")
    print(f"  数量: {report['figures']['extended_fig']['count']}")
    if report['figures']['extended_fig']['numbers']:
        print(f"  编号: {', '.join(report['figures']['extended_fig']['numbers'])}")
        print(f"  页码: ", end="")
        for fig_num in report['figures']['extended_fig']['numbers']:
            pages = report['figures']['extended_fig']['pages'][fig_num]
            print(f"Ext Fig {fig_num} (p.{','.join(map(str, pages))})", end="  ")
        print()
    
    print(f"\n📋 表格 (Tables):")
    print(f"  数量: {report['figures']['table']['count']}")
    if report['figures']['table']['numbers']:
        print(f"  编号: {', '.join(report['figures']['table']['numbers'])}")
    
    print(f"\n📋 附表 (Extended Data Tables):")
    print(f"  数量: {report['figures']['extended_table']['count']}")
    if report['figures']['extended_table']['numbers']:
        print(f"  编号: {', '.join(report['figures']['extended_table']['numbers'])}")
    
    print(f"\n📊 总计:")
    print(f"  图片: {report['figures']['main_fig']['count'] + report['figures']['extended_fig']['count']}")
    print(f"  表格: {report['figures']['table']['count'] + report['figures']['extended_table']['count']}")
    
    # 输出JSON报告
    if output_json:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📊 JSON报告已保存: {output_json}")
    
    # 输出Markdown报告
    if output_markdown:
        md_content = generate_markdown_report(report)
        with open(output_markdown, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"📝 Markdown报告已保存: {output_markdown}")
    
    return report


def generate_markdown_report(report):
    """生成Markdown格式的报告"""
    md_lines = []
    md_lines.append("# 图片统计报告\n")
    md_lines.append(f"**文件**: `{report['pdf_file']}`\n")
    md_lines.append(f"**总页数**: {report['total_pages']}\n")
    
    md_lines.append("## 主图 (Main Figures)\n")
    md_lines.append(f"**数量**: {report['figures']['main_fig']['count']}\n")
    
    if report['figures']['main_fig']['numbers']:
        md_lines.append("| 编号 | 页码 | 图注 |")
        md_lines.append("|------|------|------|")
        for fig_num in report['figures']['main_fig']['numbers']:
            pages = report['figures']['main_fig']['pages'][fig_num]
            caption = report['captions']['main_fig'].get(fig_num, '待补充')
            md_lines.append(f"| Fig {fig_num} | {', '.join(map(str, pages))} | {caption[:50]}... |")
    
    md_lines.append("\n## 附图 (Extended Data Figures)\n")
    md_lines.append(f"**数量**: {report['figures']['extended_fig']['count']}\n")
    
    if report['figures']['extended_fig']['numbers']:
        md_lines.append("| 编号 | 页码 | 图注 |")
        md_lines.append("|------|------|------|")
        for fig_num in report['figures']['extended_fig']['numbers']:
            pages = report['figures']['extended_fig']['pages'][fig_num]
            caption = report['captions']['extended_fig'].get(fig_num, '待补充')
            md_lines.append(f"| Ext Fig {fig_num} | {', '.join(map(str, pages))} | {caption[:50]}... |")
    
    md_lines.append("\n## 表格 (Tables)\n")
    md_lines.append(f"**数量**: {report['figures']['table']['count']}\n")
    
    if report['figures']['table']['numbers']:
        md_lines.append("| 编号 | 页码 |")
        md_lines.append("|------|------|")
        for fig_num in report['figures']['table']['numbers']:
            pages = report['figures']['table']['pages'][fig_num]
            md_lines.append(f"| Table {fig_num} | {', '.join(map(str, pages))} |")
    
    md_lines.append("\n## 附表 (Extended Data Tables)\n")
    md_lines.append(f"**数量**: {report['figures']['extended_table']['count']}\n")
    
    if report['figures']['extended_table']['numbers']:
        md_lines.append("| 编号 | 页码 |")
        md_lines.append("|------|------|")
        for fig_num in report['figures']['extended_table']['numbers']:
            pages = report['figures']['extended_table']['pages'][fig_num]
            md_lines.append(f"| Ext Table {fig_num} | {', '.join(map(str, pages))} |")
    
    md_lines.append("\n## 统计汇总\n")
    md_lines.append(f"- **主图**: {report['figures']['main_fig']['count']} 张")
    md_lines.append(f"- **附图**: {report['figures']['extended_fig']['count']} 张")
    md_lines.append(f"- **表格**: {report['figures']['table']['count']} 个")
    md_lines.append(f"- **附表**: {report['figures']['extended_table']['count']} 个")
    md_lines.append(f"- **总计**: {report['figures']['main_fig']['count'] + report['figures']['extended_fig']['count']} 张图片, {report['figures']['table']['count'] + report['figures']['extended_table']['count']} 个表格")
    
    return '\n'.join(md_lines)


def main():
    parser = argparse.ArgumentParser(
        description='根据文档内容判断论文中图片数量',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python count-figures.py paper.pdf
  python count-figures.py paper.pdf --json report.json --markdown report.md
        """
    )
    
    parser.add_argument('pdf_file', help='PDF文件路径')
    parser.add_argument('--json', type=str, default=None, help='输出JSON格式的报告')
    parser.add_argument('--markdown', type=str, default=None, help='输出Markdown格式的报告')
    parser.add_argument('--quiet', action='store_true', help='静默模式')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_file):
        print(f"❌ 文件不存在: {args.pdf_file}")
        sys.exit(1)
    
    # 分析PDF
    report = analyze_pdf(args.pdf_file, args.json, args.markdown)
    
    if not args.quiet:
        print("\n" + "=" * 60)
        print("✅ 图片计数完成！")
        print("=" * 60)


if __name__ == "__main__":
    main()
