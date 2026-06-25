#!/usr/bin/env python3
"""
论文图片下载工具 - 从出版商网站下载论文原始图片
用法: python download-paper-images.py <DOI> <output_dir>

功能:
- 支持多个主流出版商（Nature、Science、Cell等）
- 自动解析DOI获取网站链接
- 下载高清原始图片
- 生成Markdown格式的图片引用

依赖: pip install requests beautifulsoup4
"""
import os
import sys
import re
import json
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ 缺少依赖库，请安装: pip install requests beautifulsoup4")
    sys.exit(1)


# 出版商网站配置
PUBLISHERS = {
    'nature.com': {
        'name': 'Nature',
        'pattern': r'nature\.com/articles/',
        'img_selector': 'figure img, .c-article-section img',
        'caption_selector': 'figure figcaption, .c-article-section figcaption'
    },
    'science.org': {
        'name': 'Science',
        'pattern': r'science\.org/doi/',
        'img_selector': 'figure img, .article__body img',
        'caption_selector': 'figure figcaption, .article__body figcaption'
    },
    'cell.com': {
        'name': 'Cell Press',
        'pattern': r'cell\.com/',
        'img_selector': 'figure img, .article-body img',
        'caption_selector': 'figure figcaption, .article-body figcaption'
    },
    'elsevier.com': {
        'name': 'Elsevier',
        'pattern': r'elsevier\.com/',
        'img_selector': 'figure img, .article-body img',
        'caption_selector': 'figure figcaption, .article-body figcaption'
    },
    'wiley.com': {
        'name': 'Wiley',
        'pattern': r'wiley\.com/',
        'img_selector': 'figure img, .article-body img',
        'caption_selector': 'figure figcaption, .article-body figcaption'
    },
    'springer.com': {
        'name': 'Springer',
        'pattern': r'springer\.com/',
        'img_selector': 'figure img, .c-article-body img',
        'caption_selector': 'figure figcaption, .c-article-body figcaption'
    }
}


def doi_to_url(doi):
    """将DOI转换为网站URL"""
    # 移除DOI前缀
    doi = doi.strip()
    if doi.startswith('doi:'):
        doi = doi[4:].strip()
    if doi.startswith('https://doi.org/'):
        doi = doi[16:].strip()
    
    # 构建URL
    return f"https://doi.org/{doi}"


def get_publisher(url):
    """根据URL识别出版商"""
    for domain, config in PUBLISHERS.items():
        if domain in url:
            return config
    return None


def download_image(url, output_path, timeout=30):
    """下载单张图片"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"⚠️  下载失败 {url}: {e}")
        return False


def extract_images_from_nature(article_url, output_dir):
    """从Nature系列网站提取图片"""
    images = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(article_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有图片
        figures = soup.find_all('figure')
        
        for i, figure in enumerate(figures):
            img = figure.find('img')
            if not img:
                continue
            
            # 获取图片URL
            img_url = img.get('src') or img.get('data-src')
            if not img_url:
                continue
            
            # 转换为绝对URL
            img_url = urljoin(article_url, img_url)
            
            # 获取图注
            caption = figure.find('figcaption')
            caption_text = caption.get_text(strip=True) if caption else ''
            
            images.append({
                'url': img_url,
                'caption': caption_text,
                'index': i + 1
            })
        
        return images
    except Exception as e:
        print(f"❌ 解析页面失败: {e}")
        return []


def extract_images_from_doi(doi, output_dir):
    """根据DOI提取图片"""
    # 解析DOI获取URL
    doi_url = doi_to_url(doi)
    print(f"📄 DOI: {doi}")
    print(f"🔗 URL: {doi_url}")
    
    # 获取实际URL（跟随重定向）
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(doi_url, headers=headers, timeout=10, allow_redirects=True)
        actual_url = response.url
        print(f"🌐 实际URL: {actual_url}")
    except Exception as e:
        print(f"❌ 无法解析DOI: {e}")
        return []
    
    # 识别出版商
    publisher = get_publisher(actual_url)
    if not publisher:
        print(f"⚠️  不支持的出版商，将使用通用方法")
        publisher = {'name': 'Unknown', 'pattern': '', 'img_selector': 'figure img', 'caption_selector': 'figure figcaption'}
    
    print(f"📚 出版商: {publisher['name']}")
    
    # 根据出版商选择提取方法
    if 'nature.com' in actual_url:
        images = extract_images_from_nature(actual_url, output_dir)
    else:
        # 通用提取方法
        images = extract_images_generic(actual_url, output_dir, publisher)
    
    return images


def extract_images_generic(article_url, output_dir, publisher):
    """通用图片提取方法"""
    images = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(article_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有图片
        img_selector = publisher.get('img_selector', 'figure img')
        caption_selector = publisher.get('caption_selector', 'figure figcaption')
        
        figures = soup.select('figure')
        
        for i, figure in enumerate(figures):
            img = figure.find('img')
            if not img:
                continue
            
            # 获取图片URL
            img_url = img.get('src') or img.get('data-src')
            if not img_url:
                continue
            
            # 转换为绝对URL
            img_url = urljoin(article_url, img_url)
            
            # 获取图注
            caption = figure.find('figcaption')
            caption_text = caption.get_text(strip=True) if caption else ''
            
            images.append({
                'url': img_url,
                'caption': caption_text,
                'index': i + 1
            })
        
        return images
    except Exception as e:
        print(f"❌ 解析页面失败: {e}")
        return []


def download_images(images, output_dir, prefix='fig'):
    """下载所有图片"""
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded = []
    for img in images:
        # 生成文件名
        filename = f"{prefix}_{img['index']:02d}.png"
        output_path = os.path.join(output_dir, filename)
        
        print(f"📥 下载图片 {img['index']}: {img['url'][:80]}...")
        
        if download_image(img['url'], output_path):
            downloaded.append({
                'filename': filename,
                'path': output_path,
                'caption': img['caption'],
                'index': img['index']
            })
            print(f"  ✅ 保存到: {filename}")
        else:
            print(f"  ❌ 下载失败")
    
    return downloaded


def generate_markdown(images, output_dir, pdf_filename=None):
    """生成Markdown格式的图片引用"""
    md_lines = []
    md_lines.append("## 提取的图片\n")
    md_lines.append(f"> 图片保存路径：`{os.path.basename(output_dir)}/`\n")
    
    for img in images:
        md_lines.append(f"### Figure {img['index']} - {img['caption'][:50] if img['caption'] else '图片'}")
        md_lines.append(f"![{img['filename']}]({img['filename']})")
        md_lines.append(f"- **说明**：{img['caption'] if img['caption'] else '待补充说明'}")
        md_lines.append("")
    
    return '\n'.join(md_lines)


def main():
    parser = argparse.ArgumentParser(
        description='从出版商网站下载论文原始图片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python download-paper-images.py 10.1038/s41588-026-02641-8 ./images/
  python download-paper-images.py https://doi.org/10.1038/s41588-026-02641-8 ./images/
        """
    )
    
    parser.add_argument('doi', help='论文DOI或DOI链接')
    parser.add_argument('output_dir', help='图片输出目录')
    parser.add_argument('--prefix', default='fig', help='图片文件名前缀，默认: fig')
    parser.add_argument('--markdown', type=str, default=None, help='输出Markdown格式的图片引用')
    parser.add_argument('--json', type=str, default=None, help='输出JSON格式的图片信息')
    parser.add_argument('--quiet', action='store_true', help='静默模式')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("=" * 60)
        print("📥 论文图片下载工具")
        print("=" * 60)
    
    # 提取图片
    images = extract_images_from_doi(args.doi, args.output_dir)
    
    if not images:
        print("❌ 未找到图片，将尝试从PDF提取")
        sys.exit(1)
    
    if not args.quiet:
        print(f"\n✅ 找到 {len(images)} 张图片")
    
    # 下载图片
    downloaded = download_images(images, args.output_dir, args.prefix)
    
    if not args.quiet:
        print(f"\n✅ 成功下载 {len(downloaded)} 张图片")
    
    # 输出JSON报告
    if args.json:
        report = {
            'doi': args.doi,
            'output_dir': args.output_dir,
            'total_images': len(downloaded),
            'images': downloaded
        }
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        if not args.quiet:
            print(f"\n📊 JSON报告已保存: {args.json}")
    
    # 输出Markdown引用
    if args.markdown:
        md_content = generate_markdown(downloaded, args.output_dir)
        with open(args.markdown, 'w', encoding='utf-8') as f:
            f.write(md_content)
        if not args.quiet:
            print(f"📝 Markdown引用已保存: {args.markdown}")
    
    if not args.quiet:
        print("\n" + "=" * 60)
        print("✅ 图片下载完成！")
        print("=" * 60)


if __name__ == "__main__":
    main()
