# 线上 LLM 模型服务器使用指南

## 🚀 快速开始

### 1. 配置 API Key

**方法 1: 环境变量（推荐）**
```bash
# Windows PowerShell
$env:LLM_API_KEY="your-api-key"
$env:LLM_PROVIDER="openai"
$env:LLM_MODEL="gpt-3.5-turbo"

# Linux/Mac
export LLM_API_KEY="your-api-key"
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-3.5-turbo"
```

**方法 2: 配置文件**
```bash
# 复制示例配置文件
cp api_config.json.example api_config.json

# 编辑配置文件，填入你的 API Key
```

### 2. 启动服务器

```bash
python src/online_model_server.py
```

### 3. 测试服务器

```bash
# 健康检查
curl http://localhost:5000/health

# 生成响应
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你好，请介绍一下自己"}'
```

### 4. 启动浮动 UI

```bash
# 在新终端窗口
python src/floating_ui.py
```

## 🌐 支持的 API 提供商

### OpenAI
```json
{
  "provider": "openai",
  "api_key": "sk-...",
  "model": "gpt-3.5-turbo",
  "base_url": "https://api.openai.com/v1"
}
```

### Anthropic Claude
```json
{
  "provider": "anthropic",
  "api_key": "sk-ant-...",
  "model": "claude-3-sonnet-20240229",
  "base_url": "https://api.anthropic.com/v1"
}
```

### Google Gemini
```json
{
  "provider": "google",
  "api_key": "your-gemini-api-key",
  "model": "gemini-pro",
  "base_url": "https://generativelanguage.googleapis.com/v1beta"
}
```

### 通义千问
```json
{
  "provider": "qwen",
  "api_key": "your-qwen-api-key",
  "model": "qwen-turbo",
  "base_url": "https://dashscope.aliyuncs.com/api/v1"
}
```

### 文心一言
```json
{
  "provider": "wenxin",
  "api_key": "your-wenxin-access-token",
  "model": "ernie-bot",
  "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop"
}
```

## 📡 API 端点

### 健康检查
```
GET /health
```

### 生成响应
```
POST /generate
Content-Type: application/json

{
  "prompt": "你的问题",
  "max_new_tokens": 1000,
  "temperature": 0.7,
  "top_p": 0.9
}
```

### 流式生成
```
POST /generate_stream
Content-Type: application/json

{
  "prompt": "你的问题",
  "max_new_tokens": 1000,
  "temperature": 0.7,
  "top_p": 0.9
}
```

### 清除历史
```
POST /clear_history
```

### 获取统计
```
GET /stats
```

### 获取配置
```
GET /config
```

### 更新配置
```
POST /config
Content-Type: application/json

{
  "provider": "openai",
  "model": "gpt-4",
  "temperature": 0.8
}
```

## 🔧 高级配置

### 自定义 API 端点
```json
{
  "provider": "custom",
  "api_key": "your-api-key",
  "base_url": "https://your-custom-api.com/v1",
  "model": "your-model"
}
```

### 环境变量完整列表
- `LLM_PROVIDER`: API 提供商 (openai, anthropic, google, qwen, wenxin, custom)
- `LLM_API_KEY`: API 密钥
- `LLM_BASE_URL`: API 基础 URL（可选）
- `LLM_MODEL`: 模型名称

## 🎯 优势

✅ **无需本地 GPU**: 不需要强大的显卡
✅ **无需下载模型**: 不需要几十 GB 的存储空间
✅ **快速启动**: 几秒钟内就能开始使用
✅ **多提供商支持**: 可以轻松切换不同的 LLM 服务
✅ **流式输出**: 支持实时流式响应
✅ **完全兼容**: 与原有的浮动 UI 和记忆工具完全兼容

## 🔗 与记忆工具集成

线上 LLM 服务器与记忆工具完美集成：

1. **启动记忆 API 服务器**:
   ```bash
   python run_memory_api.py
   ```

2. **启动线上 LLM 服务器**:
   ```bash
   python src/online_model_server.py
   ```

3. **启动浮动 UI**:
   ```bash
   python src/floating_ui.py
   ```

现在你可以享受完整的 AI 助手体验，包括：
- 🤖 强大的线上 LLM 对话
- 🧠 智能记忆存储和检索
- 🪟 现代化的聊天界面
- 📊 实时统计和监控

## 🛠️ 故障排除

### 常见问题

**Q: API Key 无效**
A: 检查 API Key 是否正确，是否有足够的额度

**Q: 连接超时**
A: 检查网络连接，或尝试使用代理

**Q: 模型不存在**
A: 检查模型名称是否正确，不同提供商的模型名称不同

**Q: 流式输出不工作**
A: 某些 API 提供商可能不支持流式输出，会回退到普通模式

### 调试模式

启动时添加详细日志：
```bash
python src/online_model_server.py --debug
```

## 📝 示例用法

### Python 客户端
```python
import requests

# 生成响应
response = requests.post('http://localhost:5000/generate', json={
    'prompt': '解释一下量子计算',
    'max_new_tokens': 500,
    'temperature': 0.7
})

print(response.json()['response'])
```

### cURL 示例
```bash
# 简单对话
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你好"}'

# 流式对话
curl -X POST http://localhost:5000/generate_stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "写一首诗"}'
```

## 🎉 开始使用

现在你可以：
1. 配置你的 API Key
2. 启动线上模型服务器
3. 享受强大的 AI 对话体验！

无需等待模型下载，无需担心 GPU 内存，几秒钟就能开始使用！
