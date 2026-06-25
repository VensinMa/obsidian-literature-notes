#!/usr/bin/env python3
"""
论文图片下载工具 - 从出版商网站下载论文原始高清图片
用法: python download-paper-images.py <DOI> <output_dir>

功能:
- 支持多个主流出版商（Nature、Science、Cell、Elsevier、Wiley等）
- 自动解析DOI获取网站链接
- 查找并下载原始高清图片（Full size image）
- 生成Markdown格式的图片引用

依赖: pip install requests beautifulsoup4
"""
import os
import sys
import re
import json
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs, unquote

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ 缺少依赖库，请安装: pip install requests beautifulsoup4")
    sys.exit(1)


# 出版商网站配置 - 支持主流期刊
PUBLISHERS = {
    # ==================== Nature系列 ====================
    'nature.com': {
        'name': 'Nature',
        'journals': ['Nature', 'Nature Genetics', 'Nature Methods', 'Nature Communications', 
                     'Nature Plants', 'Nature Biotechnology', 'Nature Reviews', 'Molecular Horticulture'],
        'img_selector': 'figure img, .c-article-section img, .c-article-body img',
        'caption_selector': 'figure figcaption, .c-article-section figcaption',
        'full_size_patterns': [
            # Nature的原图URL模式：/full/ 替换 /lw685/ 或 /m685/
            r'/lw\d+/',
            r'/m\d+/',
            r'/w\d+/',
        ],
        'url_transform': lambda url: re.sub(r'/lw\d+/', '/full/', re.sub(r'/m\d+/', '/full/', re.sub(r'/w\d+/', '/full/', url)))
    },
    
    # ==================== Science系列 ====================
    'science.org': {
        'name': 'Science',
        'journals': ['Science', 'Science Advances', 'Science Bulletin', 'Science Immunology', 'Science Robotics'],
        'img_selector': 'figure img, .article__body img, .article-body img',
        'caption_selector': 'figure figcaption, .article__body figcaption',
        'full_size_patterns': [
            # Science的原图URL模式
            r'href="([^"]*?/large/[^"]*?)"',
            r'href="([^"]*?/full/[^"]*?)"',
            r'data-large="([^"]*?)"',
            r'data-src="([^"]*?)"',
        ],
        'url_transform': lambda url: re.sub(r'/(small|medium|inline)/', '/large/', url)
    },
    
    # ==================== Cell Press系列 ====================
    'cell.com': {
        'name': 'Cell Press',
        'journals': ['Cell', 'Cell Reports', 'Cell Systems', 'Cell Stem Cell', 'Cell Metabolism',
                     'Cell Chemical Biology', 'Cell Genomics', 'Cell Host & Microbe', 'Cell Reports Medicine'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # Cell的原图URL模式
            r'href="([^"]*?/gr[0-9]+\.jpg)"',
            r'href="([^"]*?/large/[^"]*?)"',
            r'data-figure-link="([^"]*?)"',
            r'data-full-size="([^"]*?)"',
        ],
        'url_transform': lambda url: re.sub(r'(_med|_sm|_sml)(\.\w+)$', r'_lrg\2', url)
    },
    
    # ==================== Elsevier系列 ====================
    'elsevier.com': {
        'name': 'Elsevier',
        'journals': ['Molecular Plant', 'iMeta', 'Trends in Plant Science', 'Phytochemistry Reviews',
                     'Plant Science', 'Planta', 'Physiologia Plantarum', 'Plant Molecular Biology',
                     'Plant Biology', 'Environmental and Experimental Botany', 'Current Opinion in Plant Biology'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # Elsevier的原图URL模式
            r'href="([^"]*?/gr[0-9]+\.jpg)"',
            r'href="([^"]*?/large/[^"]*?)"',
            r'data-figure-link="([^"]*?)"',
        ],
        'url_transform': lambda url: re.sub(r'(_med|_sm|_sml)(\.\w+)$', r'_lrg\2', url)
    },
    
    # ==================== Springer系列 ====================
    'springer.com': {
        'name': 'Springer',
        'journals': ['Journal of Advanced Research', 'New Phytologist', 'Plant Physiology',
                     'Plant Cell & Environment', 'Plant Journal', 'Plant Physiology and Biochemistry',
                     'Plant Diversity', 'Plant Cell Reports', 'Seed Biology', 'Plant Methods',
                     'Current Plant Biology', 'Molecular Plant Pathology', 'Plants-Basel'],
        'img_selector': 'figure img, .c-article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .c-article-body figcaption',
        'full_size_patterns': [
            # Springer的原图URL模式
            r'/lw\d+/',
            r'/m\d+/',
            r'/w\d+/',
        ],
        'url_transform': lambda url: re.sub(r'/lw\d+/', '/full/', re.sub(r'/m\d+/', '/full/', re.sub(r'/w\d+/', '/full/', url)))
    },
    
    # ==================== Wiley系列 ====================
    'wiley.com': {
        'name': 'Wiley',
        'journals': ['Annual Review of Plant Biology', 'Annual Review of Phytopathology',
                     'Journal of Integrative Plant Biology', 'Plant Biotechnology Journal',
                     'Journal of Experimental Botany'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # Wiley的原图URL模式
            r'href="([^"]*?/full/[^"]*?)"',
            r'data-full="([^"]*?)"',
            r'href="([^"]*?/large/[^"]*?)"',
        ],
        'url_transform': lambda url: url.replace('/medium/', '/large/').replace('/small/', '/large/')
    },
    
    # ==================== Oxford Academic系列 ====================
    'academic.oup.com': {
        'name': 'Oxford Academic',
        'journals': ['Horticulture Research', 'New Phytologist', 'Journal of Experimental Botany',
                     'Plant Physiology', 'Plant Cell'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # Oxford的原图URL模式
            r'href="([^"]*?/full/[^"]*?)"',
            r'href="([^"]*?/large/[^"]*?)"',
            r'data-full-size="([^"]*?)"',
        ],
        'url_transform': lambda url: url
    },
    
    # ==================== Frontiers系列 ====================
    'frontiersin.org': {
        'name': 'Frontiers',
        'journals': ['Frontiers in Plant Science', 'Frontiers in Genetics', 'Frontiers in Microbiology'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # Frontiers的原图URL模式
            r'href="([^"]*?/full/[^"]*?)"',
            r'data-full-size="([^"]*?)"',
            r'href="([^"]*?/large/[^"]*?)"',
        ],
        'url_transform': lambda url: url
    },
    
    # ==================== PNAS系列 ====================
    'pnas.org': {
        'name': 'PNAS',
        'journals': ['PNAS'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # PNAS的原图URL模式
            r'href="([^"]*?/full/[^"]*?)"',
            r'href="([^"]*?/large/[^"]*?)"',
            r'data-full-size="([^"]*?)"',
        ],
        'url_transform': lambda url: re.sub(r'/(small|medium|inline)/', '/large/', url)
    },
    
    # ==================== PLOS系列 ====================
    'plos.org': {
        'name': 'PLOS',
        'journals': ['PLOS ONE', 'PLOS Biology', 'PLOS Genetics', 'PLOS Pathogens', 'PLOS Medicine'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # PLOS的原图URL模式
            r'href="([^"]*?/full/[^"]*?)"',
            r'href="([^"]*?/large/[^"]*?)"',
            r'data-full-size="([^"]*?)"',
        ],
        'url_transform': lambda url: re.sub(r'size=inline', 'size=original', url)
    },
    
    # ==================== MDPI系列 ====================
    'mdpi.com': {
        'name': 'MDPI',
        'journals': ['Plants-Basel', 'Biology', 'Life', 'Genes', 'Cancers'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # MDPI的原图URL模式
            r'href="([^"]*?/full/[^"]*?)"',
            r'data-full-size="([^"]*?)"',
            r'href="([^"]*?/large/[^"]*?)"',
        ],
        'url_transform': lambda url: url
    },
    
    # ==================== BMC系列 ====================
    'biomedcentral.com': {
        'name': 'BMC',
        'journals': ['BMC Plant Biology', 'BMC Genomics', 'BMC Biology'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # BMC的原图URL模式
            r'href="([^"]*?/full/[^"]*?)"',
            r'data-full-size="([^"]*?)"',
            r'href="([^"]*?/large/[^"]*?)"',
        ],
        'url_transform': lambda url: url
    },
    
    # ==================== Plant Cell系列 ====================
    'plantcell.org': {
        'name': 'Plant Cell',
        'journals': ['Plant Cell', 'Plant Physiology'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # Plant Cell的原图URL模式
            r'href="([^"]*?/full/[^"]*?)"',
            r'href="([^"]*?/large/[^"]*?)"',
            r'data-full-size="([^"]*?)"',
        ],
        'url_transform': lambda url: url
    },
    
    # ==================== ScienceDirect系列 ====================
    'sciencedirect.com': {
        'name': 'ScienceDirect',
        'journals': ['Molecular Plant', 'iMeta', 'Trends in Plant Science'],
        'img_selector': 'figure img, .article-body img, .article__body img',
        'caption_selector': 'figure figcaption, .article-body figcaption',
        'full_size_patterns': [
            # ScienceDirect的原图URL模式
            r'href="([^"]*?/gr[0-9]+\.jpg)"',
            r'data-figure-link="([^"]*?)"',
        ],
        'url_transform': lambda url: url
    },
}

# 域名到出版商的映射
DOMAIN_TO_PUBLISHER = {}
for pub_id, pub_info in PUBLISHERS.items():
    DOMAIN_TO_PUBLISHER[pub_id] = pub_id
    # 也映射子域名
    for journal in pub_info.get('journals', []):
        # 可以添加特定期刊的域名映射
        pass


def doi_to_url(doi):
    """将DOI转换为网站URL"""
    doi = doi.strip()
    if doi.startswith('doi:'):
        doi = doi[4:].strip()
    if doi.startswith('https://doi.org/'):
        doi = doi[16:].strip()
    return f"https://doi.org/{doi}"


def get_publisher(url):
    """根据URL识别出版商"""
    for domain, config in PUBLISHERS.items():
        if domain in url:
            return config
    return None


def get_full_size_url(img_url, page_url, publisher):
    """尝试获取原始高清图片URL"""
    full_size_urls = []
    
    # 使用出版商特定的URL转换
    if publisher and 'url_transform' in publisher:
        try:
            transformed_url = publisher['url_transform'](img_url)
            if transformed_url != img_url:
                full_size_urls.append(transformed_url)
        except Exception as e:
            pass
    
    # 通用处理：查找页面中的"Full size image"链接
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(page_url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有图片元素
        figures = soup.find_all('figure')
        for figure in figures:
            img = figure.find('img')
            if not img:
                continue
            
            # 获取图片URL
            fig_img_url = img.get('src') or img.get('data-src')
            if not fig_img_url:
                continue
            
            fig_img_url = urljoin(page_url, fig_img_url)
            
            # 如果URL匹配或相似
            if img_url in fig_img_url or fig_img_url in img_url:
                # 查找"Full size image"链接
                links = figure.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    
                    # 检查链接文本
                    if any(keyword in text for keyword in ['full size', 'original', 'high-res', '下载', 'download']):
                        full_url = urljoin(page_url, href)
                        full_size_urls.append(full_url)
                    
                    # 检查链接class
                    link_class = link.get('class', [])
                    if any(keyword in ' '.join(link_class).lower() for keyword in ['full', 'original', 'download']):
                        full_url = urljoin(page_url, href)
                        full_size_urls.append(full_url)
                
                # 查找data属性
                for attr_name, attr_value in img.attrs.items():
                    if 'full' in attr_name.lower() or 'original' in attr_name.lower():
                        if attr_value and attr_value.startswith('http'):
                            full_size_urls.append(attr_value)
                        elif attr_value:
                            full_size_urls.append(urljoin(page_url, attr_value))
        
        # 使用出版商特定的模式查找
        if publisher and 'full_size_patterns' in publisher:
            for pattern in publisher['full_size_patterns']:
                if pattern.startswith('href=') or pattern.startswith('data-'):
                    # 正则表达式模式
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    for match in matches:
                        full_url = urljoin(page_url, match)
                        if full_url not in full_size_urls:
                            full_size_urls.append(full_url)
    
    except Exception as e:
        print(f"  ⚠️  查找原图链接时出错: {e}")
    
    return full_size_urls


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
        
        # 检查文件大小
        file_size = os.path.getsize(output_path)
        if file_size < 1000:  # 小于1KB可能是错误
            print(f"  ⚠️  文件太小 ({file_size} bytes)，可能是错误页面")
            return False
        
        return True
    except Exception as e:
        print(f"  ⚠️  下载失败 {url}: {e}")
        return False


def extract_images_generic(article_url, output_dir, publisher):
    """通用图片提取方法，优先下载原图"""
    images = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(article_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 使用出版商特定的选择器
        img_selector = publisher.get('img_selector', 'figure img') if publisher else 'figure img'
        
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
            
            # 查找原图链接
            full_size_urls = get_full_size_url(img_url, article_url, publisher)
            
            images.append({
                'thumbnail_url': img_url,
                'full_size_urls': full_size_urls,
                'caption': caption_text,
                'index': i + 1
            })
        
        return images
    except Exception as e:
        print(f"❌ 解析页面失败: {e}")
        return []


def download_images(images, output_dir, prefix='fig'):
    """下载所有图片，优先下载原图"""
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded = []
    for img in images:
        # 生成文件名
        filename = f"{prefix}_{img['index']:02d}.png"
        output_path = os.path.join(output_dir, filename)
        
        print(f"\n📥 下载图片 {img['index']}:")
        print(f"  📝 图注: {img['caption'][:60]}...")
        
        # 尝试下载原图
        success = False
        download_url = img['thumbnail_url']
        is_original = False
        
        # 优先尝试原图链接
        if img['full_size_urls']:
            print(f"  🔍 尝试下载原图...")
            for full_url in img['full_size_urls']:
                print(f"    尝试: {full_url[:80]}...")
                if download_image(full_url, output_path):
                    success = True
                    download_url = full_url
                    is_original = True
                    print(f"  ✅ 原图下载成功")
                    break
        
        # 如果原图下载失败，使用缩略图
        if not success:
            print(f"  📥 使用缩略图...")
            if download_image(img['thumbnail_url'], output_path):
                success = True
                download_url = img['thumbnail_url']
                print(f"  ✅ 缩略图下载成功")
        
        if success:
            # 获取文件大小
            file_size = os.path.getsize(output_path)
            size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
            
            downloaded.append({
                'filename': filename,
                'path': output_path,
                'caption': img['caption'],
                'index': img['index'],
                'download_url': download_url,
                'file_size': file_size,
                'is_original': is_original
            })
            print(f"  📁 保存到: {filename} ({size_str})")
        else:
            print(f"  ❌ 下载失败")
    
    return downloaded


def main():
    parser = argparse.ArgumentParser(
        description='从出版商网站下载论文原始高清图片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的出版商：
  - Nature系列 (nature.com)
  - Science系列 (science.org)
  - Cell Press系列 (cell.com)
  - Elsevier系列 (elsevier.com)
  - Springer系列 (springer.com)
  - Wiley系列 (wiley.com)
  - Oxford Academic (academic.oup.com)
  - Frontiers系列 (frontiersin.org)
  - PNAS (pnas.org)
  - PLOS系列 (plos.org)
  - MDPI系列 (mdpi.com)
  - BMC系列 (biomedcentral.com)
  - Plant Cell (plantcell.org)
  - ScienceDirect (sciencedirect.com)

示例:
  python download-paper-images.py 10.1038/s41588-026-02641-8 ./images/
  python download-paper-images.py https://doi.org/10.1126/science.adq5216 ./images/
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
        print("📥 论文图片下载工具（原图优先）")
        print("=" * 60)
    
    # 解析DOI获取URL
    doi_url = doi_to_url(args.doi)
    print(f"📄 DOI: {args.doi}")
    print(f"🔗 URL: {doi_url}")
    
    # 获取实际URL
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(doi_url, headers=headers, timeout=10, allow_redirects=True)
        actual_url = response.url
        print(f"🌐 实际URL: {actual_url}")
    except Exception as e:
        print(f"❌ 无法解析DOI: {e}")
        sys.exit(1)
    
    # 识别出版商
    publisher = get_publisher(actual_url)
    if not publisher:
        print(f"⚠️  不支持的出版商，将使用通用方法")
        publisher = {'name': 'Unknown'}
    
    print(f"📚 出版商: {publisher['name']}")
    
    # 提取图片
    images = extract_images_generic(actual_url, args.output_dir, publisher)
    
    if not images:
        print("❌ 未找到图片")
        sys.exit(1)
    
    if not args.quiet:
        print(f"\n✅ 找到 {len(images)} 张图片")
    
    # 下载图片
    downloaded = download_images(images, args.output_dir, args.prefix)
    
    if not args.quiet:
        print(f"\n✅ 成功下载 {len(downloaded)} 张图片")
        
        # 统计原图和缩略图
        original_count = sum(1 for d in downloaded if d['is_original'])
        thumbnail_count = len(downloaded) - original_count
        print(f"  📊 原图: {original_count} 张，缩略图: {thumbnail_count} 张")
    
    # 输出JSON报告
    if args.json:
        report = {
            'doi': args.doi,
            'url': actual_url,
            'publisher': publisher['name'],
            'output_dir': args.output_dir,
            'total_images': len(downloaded),
            'original_count': sum(1 for d in downloaded if d['is_original']),
            'thumbnail_count': sum(1 for d in downloaded if not d['is_original']),
            'images': downloaded
        }
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        if not args.quiet:
            print(f"\n📊 JSON报告已保存: {args.json}")
    
    # 输出Markdown引用
    if args.markdown:
        md_lines = []
        md_lines.append("## 提取的图片\n")
        md_lines.append(f"> 图片保存路径：`{os.path.basename(args.output_dir)}/`\n")
        
        for img in downloaded:
            size_str = f"{img['file_size'] / 1024:.1f} KB" if img['file_size'] < 1024 * 1024 else f"{img['file_size'] / (1024 * 1024):.1f} MB"
            img_type = "原图" if img['is_original'] else "缩略图"
            
            md_lines.append(f"### Figure {img['index']} - {img['caption'][:50] if img['caption'] else '图片'}")
            md_lines.append(f"![{img['filename']}]({img['filename']})")
            md_lines.append(f"- **说明**：{img['caption'] if img['caption'] else '待补充说明'}")
            md_lines.append(f"- **类型**：{img_type} ({size_str})")
            md_lines.append("")
        
        with open(args.markdown, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        if not args.quiet:
            print(f"📝 Markdown引用已保存: {args.markdown}")
    
    if not args.quiet:
        print("\n" + "=" * 60)
        print("✅ 图片下载完成！")
        print("=" * 60)


if __name__ == "__main__":
    main()
