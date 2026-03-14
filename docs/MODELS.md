# PyAgent 模型配置指南

## 支持的模型列表

PyAgent 目前支持以下大语言模型：

### 国外模型

| 模型 | type值 | 特点 | 获取API |
|------|--------|------|---------|
| Claude | `claude` | 综合能力强，长文本 | [console.anthropic.com](https://console.anthropic.com/) |
| GPT-4 | `openai` | 能力强，生态丰富 | [platform.openai.com](https://platform.openai.com/) |

### 国产模型 (推荐)

| 模型 | type值 | 推荐模型 | 特点 | 获取API |
|------|--------|----------|------|----------|
| 智谱GLM | `glm` | `glm-4-flash` | 🆓免费，速度快 | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| 通义千问 | `qwen` | `qwen-turbo` | 🆓免费，能力强 | [dashscope.aliyun.com](https://dashscope.aliyun.com/) |
| DeepSeek | `deepseek` | `deepseek-chat` | 💰便宜，编程强 | [platform.deepseek.com](https://platform.deepseek.com/) |
| Kimi | `kimi` | `moonshot-v1-8k` | 📝长文本 | [platform.moonshot.cn](https://platform.moonshot.cn/) |

### 本地模型

| 模型 | type值 | 特点 | 部署方式 |
|------|--------|------|----------|
| Ollama | `local` | 免费，隐私 | [ollama.ai](https://ollama.ai/) |

## 快速配置

### 1. 使用智谱GLM (推荐新手)

```bash
# 1. 注册获取API密钥: https://open.bigmodel.cn/
# 2. 配置.env文件
echo "ZHIPUAI_API_KEY=your_api_key_here" >> .env

# 3. 配置config.yaml
# model:
#   type: "glm"
#   glm:
#     model: "glm-4-flash"

# 4. 运行
myagent chat
```

### 2. 使用通义千问

```bash
# 1. 注册获取API密钥: https://dashscope.aliyun.com/
# 2. 配置.env文件
echo "DASHSCOPE_API_KEY=your_api_key_here" >> .env

# 3. 配置config.yaml
# model:
#   type: "qwen"
#   qwen:
#     model: "qwen-turbo"
```

### 3. 使用DeepSeek (性价比高)

```bash
# 1. 注册获取API密钥: https://platform.deepseek.com/
# 2. 配置.env文件
echo "DEEPSEEK_API_KEY=your_api_key_here" >> .env

# 3. 配置config.yaml
# model:
#   type: "deepseek"
#   deepseek:
#     model: "deepseek-chat"
```

### 4. 使用本地模型 (Ollama)

```bash
# 1. 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. 拉取模型
ollama pull codellama
ollama pull qwen2

# 3. 启动服务
ollama serve

# 4. 配置config.yaml
# model:
#   type: "local"
#   local:
#     endpoint: "http://localhost:11434"
#     model: "qwen2"
```

## 模型对比

### 性能对比

| 模型 | 编程能力 | 中文能力 | 长文本 | 价格 |
|------|----------|----------|--------|------|
| GLM-4-Flash | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 免费 |
| Qwen-Turbo | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 |
| DeepSeek-Chat | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 便宜 |
| Claude 3.5 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 较贵 |
| GPT-4 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 较贵 |

### 使用场景推荐

**学习Python基础**
- 推荐: GLM-4-Flash (免费，速度快)

**代码审查/调试**
- 推荐: DeepSeek-Chat (编程能力强，便宜)

**长文档分析**
- 推荐: Kimi (128k上下文) 或 Claude (200k上下文)

**离线使用**
- 推荐: 本地Ollama

## 配置文件说明

### config.yaml 完整配置

```yaml
model:
  type: "glm"  # 选择模型类型

  # 各模型具体配置
  claude:
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 4096
    temperature: 0.7

  openai:
    model: "gpt-4-turbo"
    max_tokens: 4096
    temperature: 0.7

  glm:
    model: "glm-4-flash"      # 推荐：快，免费
    # model: "glm-4-plus"     # 更强
    # model: "glm-4-air"      # 便宜
    max_tokens: 4096
    temperature: 0.7

  qwen:
    model: "qwen-turbo"       # 推荐：快，免费
    # model: "qwen-plus"      # 更强
    # model: "qwen-max"       # 最强
    max_tokens: 4096
    temperature: 0.7

  deepseek:
    model: "deepseek-chat"    # 通用对话
    # model: "deepseek-coder" # 代码专用
    max_tokens: 4096
    temperature: 0.7

  kimi:
    model: "moonshot-v1-8k"   # 8k上下文
    # model: "moonshot-v1-32k"  # 32k上下文
    # model: "moonshot-v1-128k" # 128k上下文
    max_tokens: 4096
    temperature: 0.7

  local:
    endpoint: "http://localhost:11434"
    model: "codellama"        # 或 qwen2, llama3
    max_tokens: 2048
```

### 环境变量配置

```bash
# .env 文件

# Claude
ANTHROPIC_API_KEY=sk-ant-xxxxx

# OpenAI / DeepSeek / Kimi (兼容OpenAI格式)
OPENAI_API_KEY=sk-xxxxx

# 智谱GLM
ZHIPUAI_API_KEY=xxxxx.xxxxx

# 通义千问
DASHSCOPE_API_KEY=sk-xxxxx

# DeepSeek (独立配置)
DEEPSEEK_API_KEY=sk-xxxxx

# Kimi (独立配置)
MOONSHOT_API_KEY=sk-xxxxx

# 本地模型
LOCAL_MODEL_ENDPOINT=http://localhost:11434
```

## 切换模型

### 方法1: 修改配置文件

```bash
# 编辑 config/config.yaml
vim config/config.yaml

# 修改 model.type 为目标模型
# 保存后重新运行
myagent chat
```

### 方法2: 通过环境变量

```bash
# 临时切换模型
MODEL_TYPE=qwen myagent chat
```

## 故障排除

### API密钥错误

```bash
# 检查.env文件是否配置
cat .env | grep API_KEY

# 确认API密钥格式正确
# 智谱: xxxxx.xxxxx
# 其他: sk-xxxxx
```

### 网络连接问题

```bash
# 国产模型通常在中国大陆，网络更稳定
# 如果使用国外模型，可能需要代理

# 设置代理
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

### 模型响应慢

```bash
# 推荐使用以下模型获得更快响应:
# - glm-4-flash (智谱)
# - qwen-turbo (通义)
# - deepseek-chat (深度求索)
```

## 费用说明

| 模型 | 免费额度 | 价格 |
|------|----------|------|
| GLM-4-Flash | 25M tokens | ¥0 |
| GLM-4-Plus | 新用户免费 | ¥0.05/1k tokens |
| Qwen-Turbo | 新用户免费 | ¥0 |
| DeepSeek-Chat | 新用户免费 | ¥0.001/1k tokens |
| Claude 3.5 | 无 | $0.003/1k tokens |
| GPT-4 | 无 | $0.01/1k tokens |

> 💡 **建议**: 新用户推荐使用智谱GLM或通义千问，有免费额度且速度快。

## 本地模型 (Ollama)

### 支持的模型

```bash
# 编程相关
ollama pull codellama        # Code Llama
ollama pull deepseek-coder   # DeepSeekCoder

# 通用模型
ollama pull qwen2            # Qwen2
ollama pull llama3           # Llama 3
ollama pull mistral          # Mistral

# 运行
ollama run qwen2
```

### 配置本地模型

```yaml
# config/config.yaml
model:
  type: "local"
  local:
    endpoint: "http://localhost:11434"
    model: "qwen2"  # 或其他已下载的模型
    max_tokens: 2048
```

### 优点

- ✅ 完全免费
- ✅ 数据隐私
- ✅ 无需网络

### 缺点

- ❌ 需要较好的硬件
- ❌ 模型能力通常不如API版本
