# PyAgent 快速开始指南

## 安装

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 2. 安装依赖

```bash
pip install -e .
```

## 配置

### 1. 复制环境变量模板

```bash
cp .env.example .env
```

### 2. 编辑.env文件

```bash
# 至少配置一个API密钥

# 国外模型
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Claude
OPENAI_API_KEY=your_openai_api_key_here        # OpenAI GPT

# 国产模型 (推荐，有免费额度)
ZHIPUAI_API_KEY=your_zhipuai_api_key_here      # 智谱GLM
DASHSCOPE_API_KEY=your_dashscope_api_key_here  # 阿里通义千问
DEEPSEEK_API_KEY=your_deepseek_api_key_here    # DeepSeek
MOONSHOT_API_KEY=your_moonshot_api_key_here    # Kimi

# 本地模型
LOCAL_MODEL_ENDPOINT=http://localhost:11434    # Ollama
```

### 3. 初始化Agent

```bash
myagent init
```

## 使用

### 基本命令

```bash
# 查看帮助
myagent --help

# 启动交互对话
myagent chat

# 发送单条消息
myagent chat -m "如何使用Python的asyncio?"

# 手动触发学习
myagent learn

# 查看学习日报
myagent report

# 查看技能树
myagent skills

# 搜索知识库
myagent knowledge "async best practices"
```

### 守护进程

```bash
# 启动守护进程（后台定时学习）
myagent daemon start

# 查看守护进程状态
myagent daemon status

# 停止守护进程
myagent daemon stop
```

## 配置说明

编辑 `config/config.yaml` 自定义配置：

```yaml
# 模型配置
model:
  type: "glm"  # claude | openai | glm | qwen | deepseek | kimi | local
  glm:
    model: "glm-4-flash"  # 推荐：速度快，有免费额度

# 学习时间
learning:
  schedule: "02:00"  # 每天凌晨2点学习

# 知识库配置
knowledge:
  embedding_model: "all-MiniLM-L6-v2"
```

### 推荐模型配置

| 模型 | type | model值 | 特点 |
|------|------|---------|------|
| 智谱GLM | `glm` | `glm-4-flash` | 🇨🇳 免费，速度快 |
| 通义千问 | `qwen` | `qwen-turbo` | 🇨🇳 免费，能力强 |
| DeepSeek | `deepseek` | `deepseek-chat` | 🇨🇳 便宜，编程强 |
| Claude | `claude` | `claude-3-5-sonnet` | 🇺🇸 综合能力强 |
| Kimi | `kimi` | `moonshot-v1-8k` | 🇨🇳 长文本 |

## 项目结构

```
myagent/
├── config/           # 配置文件
├── data/             # 数据目录
│   ├── knowledge/    # 知识库
│   ├── vector_db/    # 向量数据库
│   ├── reports/      # 日报
│   └── logs/         # 日志
├── src/              # 源代码
└── tests/            # 测试
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
ruff check src/
```

## 常见问题

### Q: 如何切换模型？

A: 编辑 `config/config.yaml`，修改 `model.type`：
- `claude` - Claude模型 (Anthropic)
- `openai` - OpenAI GPT模型
- `glm` - 智谱GLM模型 (🇨🇳 推荐，免费额度)
- `qwen` - 阿里通义千问 (🇨🇳 推荐，免费额度)
- `deepseek` - DeepSeek模型 (🇨🇳 性价比高)
- `kimi` - 月之暗面Kimi (🇨🇳 长文本)
- `local` - 本地模型（Ollama）

### Q: 如何获取API密钥？

A:
- **智谱GLM**: https://open.bigmodel.cn/ (新用户免费额度)
- **通义千问**: https://dashscope.aliyun.com/ (新用户免费额度)
- **DeepSeek**: https://platform.deepseek.com/ (便宜)
- **Claude**: https://console.anthropic.com/
- **Kimi**: https://platform.moonshot.cn/

### Q: 学习数据存储在哪里？

A: 所有学习数据存储在 `data/` 目录：
- `data/knowledge/` - 结构化知识
- `data/vector_db/` - 向量数据库
- `data/reports/` - 学习日报

### Q: 如何清理数据重新开始？

A: 删除 `data/` 目录后重新运行 `myagent init`：

```bash
rm -rf data/
myagent init
```
