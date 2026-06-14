# Zotero 配置指南

## 获取 API Key

### 步骤 1：登录 Zotero
访问 https://www.zotero.org 并登录

### 步骤 2：创建 API Key
1. 访问 https://www.zotero.org/settings/keys
2. 点击 **"Create new private key"**
3. 填写说明（如 "Obsidian Literature Notes"）
4. 勾选权限：
   - ✅ Allow library access
   - ✅ Allow write access
5. 点击 **"Save Key"**
6. 记录 **User ID** 和 **API Key**

### 步骤 3：配置环境变量
编辑配置文件：
```bash
nano ~/.hermes/skills/obsidian-literature-notes/scripts/zotero-config.env
```

添加：
```bash
export ZOTERO_USER_ID="你的用户ID"
export ZOTERO_API_KEY="你的APIKey"
```

## 验证配置

```bash
# 加载配置
source ~/.hermes/skills/obsidian-literature-notes/scripts/zotero-config.env

# 测试 API
curl -s "https://api.zotero.org/users/$ZOTERO_USER_ID/items?limit=1" \
  -H "Zotero-API-Key: $ZOTERO_API_KEY" | jq '.[0].data.key'
```

## 常见问题

### 401 错误
API Key 无效或已过期，请重新创建。

### 403 错误
API Key 权限不足，请确保勾选了读写权限。

### 429 错误
请求过于频繁，等待 5 分钟后重试。
