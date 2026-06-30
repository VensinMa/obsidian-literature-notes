# Obsidian Literature Notes

Agent skill for turning academic PDFs, DOI pages, or paper metadata into standardized Obsidian literature notes with structured YAML frontmatter, Chinese summaries/translations, figure extraction, tag normalization, validation, and optional Zotero sync.

## Install

```bash
git clone https://github.com/VensinMa/obsidian-literature-notes.git
cd obsidian-literature-notes
pip install -r requirements.txt
./install.sh
```

For manual installation, copy this folder to:

```bash
~/.hermes/skills/obsidian-literature-notes/
```

For Codex-style local skill use, copy it to your Codex skills directory and keep the folder name `obsidian-literature-notes`.

## Quick Use

Ask the agent:

```text
请为这个 PDF 做标准化 Obsidian 文献笔记：/path/to/paper.pdf
```

Useful commands:

```bash
python scripts/count-figures.py paper.pdf --json count-report.json --markdown count-report.md
python scripts/download-paper-images.py "10.xxxx/xxxxx" images/PaperShort_Year --markdown images.md --json images.json
python scripts/extract-images.py paper.pdf images/PaperShort_Year --min-size 5000 --markdown images.md --json images.json
python scripts/validate-note.py "阅读笔记｜YYYY-MM-DD｜中文标题｜YYYY-MM-DD.md"
```

## Note Standard

The required note structure is defined in:

- `SKILL.md`: agent workflow and routing
- `references/note-standard.md`: full note schema and validation checklist
- `templates/note-template.md`: reusable note template
- `templates/frontmatter.yaml`: normalized YAML frontmatter

## Zotero

Create `scripts/zotero-config.env` from the example file and set:

```bash
export ZOTERO_USER_ID="your-user-id"
export ZOTERO_API_KEY="your-api-key"
export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"
```

Then sync a note:

```bash
python scripts/zotero-add-note.py ITEM_KEY note.md "literature,genomics"
```

## License

MIT
