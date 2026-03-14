# API端点 (BASE_URL) 配置说明

## 概述

PyAgent 支持为所有模型配置自定义的 API 端点 (BASE_URL)。这在以下场景中非常有用：

1. **使用代理服务** - 通过代理访问国外API
2. **第三方兼容API** - 使用兼容OpenAI格式的服务
3. **企业内部部署** - 连接企业内部部署的模型服务
4. **模型服务迁移** - 服务地址变更时的快速切换

## 配置优先级

BASE_URL 配置的优先级（从高到低）：

```
环境变量 (.env) > config.yaml > 代码默认值
```

## 支持的模型

| 模型 | 环境变量 | config.yaml配置键 | 默认值 |
|------|----------|------------------|--------|
| Claude | `ANTHROPIC_BASE_URL` | `claude.base_url` | `https://api.anthropic.com` |
| OpenAI | `OPENAI_BASE_URL` | `openai.base_url` | `https://api.openai.com/v1` |
| GLM | `ZHIPUAI_BASE_URL` | `glm.base_url` | `https://open.bigmodel.cn/api/paas/v4` |
| Qwen | `DASHSCOPE_BASE_URL` | `qwen.base_url` | `https://dashscope.aliyuncs.com/...` |
| DeepSeek | `DEEPSEEK_BASE_URL` | `deepseek.base_url` | `https://api.deepseek.com/v1` |
| Kimi | `MOONSHOT_BASE_URL` | `kimi.base_url` | `https://api.moonshot.cn/v1` |
| Local | `LOCAL_MODEL_ENDPOINT` | `local.endpoint` | `http://localhost:11434` |

## 配置方式

### 方式1: 通过环境变量 (推荐)

编辑 `.env` 文件：

```bash
# OpenAI 使用代理
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://your-proxy.com/v1

# GLM 自定义端点
ZHIPUAI_API_KEY=xxxxx.xxxxx
ZHIPUAI_BASE_URL=https://custom-endpoint.com/api/paas/v4
```

### 方式2: 通过 config.yaml

编辑 `config/config.yaml`：

```yaml
model:
  type: "openai"
  openai:
    model: "gpt-4-turbo"
    base_url: "https://your-proxy.com/v1"  # 自定义端点
```

### 方式3: 混合配置

你可以在 `config.yaml` 中配置默认值，然后在 `.env` 中覆盖：

```yaml
# config.yaml - 默认配置
openai:
  base_url: "https://api.openai.com/v1"
```

```bash
# .env - 开发环境覆盖
OPENAI_BASE_URL=https://dev-proxy.com/v1
```

## 使用场景示例

### 场景1: 使用代理访问 OpenAI

```bash
# .env
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://api.openai-proxy.com/v1
```

### 场景2: 使用第三方兼容API

某些第三方服务兼容 OpenAI API 格式：

```bash
# 使用 DeepSeek 的 OpenAI 兼容端点
OPENAI_API_KEY=sk-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
```

### 场景3: 企业内部部署

```bash
# .env
ZHIPUAI_API_KEY=internal-key
ZHIPUAI_BASE_URL=https://llm.internal.company.com/api/paas/v4
```

```yaml
# 或者直接在 config.yaml 配置
glm:
  model: "glm-4-flash"
  base_url: "https://llm.internal.company.com/api/paas/v4"
```

### 场景4: 测试环境切换

```bash
# .env.development
DASHSCOPE_API_KEY=dev-key
DASHSCOPE_BASE_URL=https://dashscope-dev.aliyuncs.com/...
```

```bash
# .env.production
DASHSCOPE_API_KEY=prod-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/...
```

## 国产模型端点说明

### 智谱GLM

```bash
# 公有云默认端点
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# 私有化部署端点
ZHIPUAI_BASE_URL=https://your-glm-server.com/api/paas/v4
```

### 通义千问

```bash
# 公有云默认端点
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation

# 注意：通义千问的端点较长，包含完整路径
```

### DeepSeek

```bash
# 官方端点
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# DeepSeek 兼容 OpenAI 格式，也可用 OPENAI_BASE_URL 配置
```

### Kimi

```bash
# 官方端点
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
```

## 故障排除

### 问题1: 连接超时

```bash
# 检查端点是否正确
curl https://your-base-url/v1/models

# 如果使用代理，确保代理可用
curl -x https://your-proxy.com https://api.openai.com/v1/models
```

### 问题2: 认证失败

确保 API 密钥与端点匹配：

```bash
# ❌ 错误：混用不同服务的密钥和端点
OPENAI_API_KEY=sk-deepseek-key
OPENAI_BASE_URL=https://api.openai.com/v1  # 不匹配

# ✅ 正确：密钥和端点匹配
DEEPSEEK_API_KEY=sk-deepseek-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 问题3: 配置未生效

检查配置优先级，环境变量会覆盖 config.yaml：

```bash
# 检查当前环境变量
echo $OPENAI_BASE_URL

# 临时清除环境变量
unset OPENAI_BASE_URL
```

## 最佳实践

1. **开发环境**: 使用环境变量，便于快速切换
2. **生产环境**: 在 config.yaml 中固定配置，避免环境变量干扰
3. **敏感信息**: 将 BASE_URL 和 API 密钥一起存储在环境变量中
4. **文档记录**: 在项目文档中记录自定义端点的用途和访问方式

## 相关文件

- `.env.example` - 环境变量模板
- `config/config.yaml` - 主配置文件
- `src/core/config.py` - 配置加载逻辑
- `src/models/factory.py` - 模型创建工厂
