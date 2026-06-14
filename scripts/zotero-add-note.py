#!/usr/bin/env python3
"""
Zotero API - 添加笔记到文献
用法: python3 zotero-add-note.py ITEM_KEY /path/to/note.md "tag1,tag2"
"""
import sys
import os
import re
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
    config['ZOTERO_API_KEY']=***', config.get('ZOTERO_API_KEY', ''))
    return config

def md_to_zotero_html(md_text, title=None):
    if md_text.startswith('---'):
        end_idx = md_text.find('---', 3)
        if end_idx != -1:
            md_text = md_text[end_idx + 3:].strip()
    if title:
        md_text = f"# {title}\n\n{md_text}"
    html = markdown.markdown(md_text, extensions=['tables'])
    return f'<div data-schema-version="9">{html}</div>'

def add_note(item_key, note_file, tags, title=None, config=None):
    if config is None:
        config = load_config()
    
    user_id = config.get('ZOTERO_USER_ID')
    api_key = config.get('ZOTERO_API_KEY')
    
    if not user_id or not api_key:
        return False, "未配置 ZOTERO_USER_ID 或 ZOTERO_API_KEY"
    
    with open(note_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not title:
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else os.path.basename(note_file).replace('.md', '')
    
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

def main():
    if len(sys.argv) < 4:
        print("用法: python3 zotero-add-note.py ITEM_KEY /path/to/note.md 'tag1,tag2'")
        sys.exit(1)
    
    item_key = sys.argv[1]
    note_file = sys.argv[2]
    tags = sys.argv[3]
    
    if not os.path.exists(note_file):
        print(f"❌ 文件不存在: {note_file}")
        sys.exit(1)
    
    config = load_config()
    print(f"📝 正在添加笔记到 Zotero...")
    success, result = add_note(item_key, note_file, tags, config=config)
    
    if success:
        print(f"✅ 成功! Note Key: {result}")
    else:
        print(f"❌ 失败: {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()
