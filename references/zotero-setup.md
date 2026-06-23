# Zotero API 配置指南

## 获取 API Key

1. 登录 Zotero 账户
2. 访问 https://www.zotero.org/settings/keys
3. 点击 "Create new private key"
4. 勾选以下权限：
   - **Allow library access** (读取文献库)
   - **Allow write access** (写入笔记)
5. 点击 "Save Key"
6. 记录显示的 **User ID** 和 **API Key**

## 配置方式

### 方式一：环境变量

在 `~/.hermes/.env` 中添加：

```bash
ZOTERO_USER_ID=你的用户ID
ZOTERO_API_KEY=你的API密钥
OBSIDIAN_VAULT_PATH=/path/to/obsidian/vault
```

### 方式二：配置文件

```bash
# 复制示例配置文件
cp scripts/zotero-config.env.example scripts/zotero-config.env

# 编辑配置文件
nano scripts/zotero-config.env
```

配置文件内容：
```bash
# Zotero API 配置
ZOTERO_USER_ID=你的用户ID
ZOTERO_API_KEY=你的API密钥

# Obsidian Vault 路径（可选）
OBSIDIAN_VAULT_PATH=/path/to/obsidian/vault
```

## 验证配置

运行以下命令验证配置是否正确：

```bash
python3 scripts/zotero-add-note.py
```

如果显示 "未配置 ZOTERO_USER_ID 或 ZOTERO_API_KEY"，请检查配置。

## API 限制

- **请求频率**：Zotero API 有请求频率限制
  - 每秒最多 1 次请求
  - 每分钟最多 60 次请求
  - 超出限制会返回 429 错误

- **存储限制**：
  - 免费账户：300 MB
  - 付费账户：6 GB+

## 常见问题

### 无法获取文献列表
- 检查 User ID 是否正确
- 确认文献已导入 Zotero

### 笔记添加失败
- 检查 API Key 权限
- 确认 Item Key 存在

### 429 Too Many Requests
- 等待 5 分钟后重试
- 减少批量处理的文献数量

## 安全提示

- **不要分享你的 API Key**
- **定期更换 API Key**
- **使用环境变量而非硬编码**
