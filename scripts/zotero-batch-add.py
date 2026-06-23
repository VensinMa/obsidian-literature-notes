#!/usr/bin/env python3
"""
批量添加笔记到 Zotero
用法: python3 zotero-batch-add.py [--config config.json]
"""
import sys
import os
import re
import json
import time
import markdown
import requests

def load_config():
    config = {}
    config_file = os.path.join(os.path.dirname(__file__), 'zotero-config.env')
    if os.path.exists(config_file):
        with open(config_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    value = value.strip().strip('"').strip("'")
                    config[key] = value
    config['ZOTERO_USER_ID'] = os.environ.get('ZOTERO_USER_ID', config.get('ZOTERO_USER_ID', ''))
    config['ZOTERO_API_KEY'] = os.environ.get('ZOTERO_API_KEY', config.get('ZOTERO_API_KEY', ''))
    return config

def md_to_zotero_html(md_text, title):
    if md_text.startswith('---'):
        end_idx = md_text.find('---', 3)
        if end_idx != -1:
            md_text = md_text[end_idx + 3:].strip()
    full_md = f"# {title}\n\n{md_text}"
    html = markdown.markdown(full_md, extensions=['tables'])
    return f'<div data-schema-version="9">{html}</div>'

def add_note(item_key, note_file, tags, title, config):
    user_id = config.get('ZOTERO_USER_ID')
    api_key = config.get('ZOTERO_API_KEY')
    
    with open(note_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    note_html = md_to_zotero_html(content, title)
    tag_list = [{"tag": t.strip()} for t in tags.split(',') if t.strip()]
    data = [{"itemType": "note", "parentItem": item_key, "note": note_html, "tags": tag_list, "relations": {}}]
    
    resp = requests.post(
        f"https://api.zotero.org/users/{user_id}/items",
        headers={"Content-Type": "application/json", "Zotero-API-Key": api_key},
        json=data
    )
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get('success') and len(result['success']) > 0:
            return True, result['success']['0']
    return False, f"HTTP {resp.status_code}"

def find_item_key(title, config):
    user_id = config.get('ZOTERO_USER_ID')
    api_key = config.get('ZOTERO_API_KEY')
    
    resp = requests.get(
        f"https://api.zotero.org/users/{user_id}/items",
        headers={"Zotero-API-Key": api_key},
        params={"q": title, "limit": 5, "itemType": "journalArticle || preprint"}
    )
    
    if resp.status_code == 200:
        items = resp.json()
        for item in items:
            if item.get('data', {}).get('title', '').lower().startswith(title.lower()[:30]):
                return item['data']['key']
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description='批量添加笔记到 Zotero')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--papers', help='文献列表 JSON 文件')
    args = parser.parse_args()
    
    config = load_config()
    
    # 默认文献列表（可从 JSON 文件加载）
    papers = [
        {"name": "示例文献", "title": "Paper Title", "file": "/path/to/note.md", "tags": "reading-note"}
    ]
    
    if args.papers and os.path.exists(args.papers):
        with open(args.papers) as f:
            papers = json.load(f)
    
    print(f"📝 批量添加笔记到 Zotero")
    print("=" * 50)
    
    success = 0
    for i, p in enumerate(papers, 1):
        print(f"\n📄 [{i}/{len(papers)}] {p['name']}...")
        
        if not os.path.exists(p['file']):
            print(f"   ❌ 文件不存在: {p['file']}")
            continue
        
        # 查找 Item Key
        item_key = p.get('key') or find_item_key(p['title'], config)
        if not item_key:
            print(f"   ❌ 未找到文献: {p['title']}")
            continue
        
        if i > 1:
            time.sleep(3)
        
        ok, result = add_note(item_key, p['file'], p['tags'], p['title'], config)
        if ok:
            print(f"   ✅ 成功! Note Key: {result}")
            success += 1
        else:
            print(f"   ❌ 失败: {result}")
    
    print(f"\n📊 完成: {success}/{len(papers)} 成功")

if __name__ == "__main__":
    main()
