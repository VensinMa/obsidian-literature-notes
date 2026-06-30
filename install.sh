#!/bin/bash
# Obsidian Literature Notes - 安装脚本
# https://github.com/VensinMa/obsidian-literature-notes

set -e

echo "📚 Obsidian Literature Notes 安装程序"
echo "========================================"

# 检测操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac
echo "🖥️  操作系统: ${MACHINE}"

# 检查依赖
echo ""
echo "🔍 检查依赖..."

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ 未找到 $1"
        return 1
    else
        echo "✅ $1 已安装"
        return 0
    fi
}

MISSING_DEPS=0

check_command python3 || MISSING_DEPS=1
check_command curl || MISSING_DEPS=1
check_command jq || MISSING_DEPS=1

# 检查 pdftotext
if ! command -v pdftotext &> /dev/null; then
    echo "❌ 未找到 pdftotext (poppler-utils)"
    echo ""
    echo "请安装 poppler-utils:"
    if [ "${MACHINE}" = "Mac" ]; then
        echo "  brew install poppler"
    else
        echo "  sudo apt install poppler-utils"
    fi
    MISSING_DEPS=1
else
    echo "✅ pdftotext 已安装"
fi

# 检查 Python 包
if ! python3 -c "import markdown" 2>/dev/null; then
    echo "❌ 未找到 markdown"
    echo ""
    echo "请安装 markdown:"
    if [ "${MACHINE}" = "Mac" ]; then
        echo "  pip install -r requirements.txt"
    else
        echo "  pip install -r requirements.txt"
    fi
    MISSING_DEPS=1
else
    echo "✅ markdown 已安装"
fi

if ! python3 -c "import fitz, requests, bs4" 2>/dev/null; then
    echo "❌ 未找到 Python 依赖: pymupdf requests beautifulsoup4"
    echo "  pip install -r requirements.txt"
    MISSING_DEPS=1
else
    echo "✅ PDF/网络下载依赖已安装"
fi

if [ ${MISSING_DEPS} -eq 1 ]; then
    echo ""
    echo "❌ 缺少依赖，请先安装上述依赖后重试"
    exit 1
fi

# 安装 skill
echo ""
echo "📦 安装 Skill..."

HERMES_SKILL_DIR="${HOME}/.hermes/skills/obsidian-literature-notes"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -d "${HERMES_SKILL_DIR}" ]; then
    echo "⚠️  已存在旧版本，正在更新..."
    rm -rf "${HERMES_SKILL_DIR}"
fi

mkdir -p "${HERMES_SKILL_DIR}"
cp -r "${SCRIPT_DIR}"/* "${HERMES_SKILL_DIR}/"

echo "✅ Skill 已安装到: ${HERMES_SKILL_DIR}"

# 创建配置文件
echo ""
echo "⚙️  配置 Zotero API..."

CONFIG_FILE="${HERMES_SKILL_DIR}/scripts/zotero-config.env"
CONFIG_EXAMPLE="${HERMES_SKILL_DIR}/scripts/zotero-config.env.example"

if [ ! -f "${CONFIG_FILE}" ]; then
    cp "${CONFIG_EXAMPLE}" "${CONFIG_FILE}"
    echo "📝 配置文件已创建: ${CONFIG_FILE}"
    echo ""
    echo "请编辑配置文件，添加你的 Zotero API 信息："
    echo "  nano ${CONFIG_FILE}"
else
    echo "✅ 配置文件已存在"
fi

# 设置执行权限
chmod +x "${HERMES_SKILL_DIR}/scripts/"*.py
chmod +x "${HERMES_SKILL_DIR}/scripts/"*.sh

echo ""
echo "========================================"
echo "🎉 安装完成！"
echo ""
echo "📚 下一步："
echo "1. 编辑配置文件: nano ${CONFIG_FILE}"
echo "2. 在 Hermes Agent 中使用: 请为这个 PDF 做标准化 Obsidian 文献笔记"
echo ""
echo "📖 文档: https://github.com/VensinMa/obsidian-literature-notes"
echo "========================================"
