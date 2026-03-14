# PyAgent 项目总结

## 项目概述

PyAgent 是一个自进化的 Python 专家 Agent 系统，能够每天主动从网络学习新技术和最佳实践，并持续增强自身能力。

## 项目结构

```
myagent/
├── config/                  # 配置文件
│   ├── config.yaml          # 主配置
│   └── prompts/             # 提示词模板
├── docs/                    # 文档
│   ├── GETTING_STARTED.md   # 快速开始指南
│   └── API.md               # API文档
├── examples/                # 示例代码
│   ├── simple_chat.py       # 简单对话示例
│   ├── learn_and_report.py  # 学习和报告示例
│   └── knowledge_search.py  # 知识搜索示例
├── src/                     # 源代码
│   ├── cli/                 # CLI界面
│   ├── core/                # 核心模块
│   ├── daily/               # 日报系统
│   ├── knowledge/           # 知识管理
│   ├── learning/            # 学习引擎
│   ├── models/              # LLM抽象层
│   └── main.py              # 入口文件
├── tests/                   # 测试
├── data/                    # 数据目录（运行时创建）
├── pyproject.toml           # 项目配置
├── requirements.txt         # 依赖列表
└── README.md                # 项目说明
```

## 核心功能模块

### 1. 模型抽象层 (src/models/)
- **BaseLLM**: LLM基类接口
- **ClaudeLLM**: Claude模型实现
- **OpenAILLM**: OpenAI模型实现
- **LocalLLM**: 本地模型实现(Ollama)
- **SentenceTransformerEmbedding**: 嵌入模型

### 2. 知识管理系统 (src/knowledge/)
- **FileStore**: 文件存储（结构化知识）
- **VectorStore**: 向量数据库（非结构化知识）
- **HybridKnowledgeStore**: 混合存储
- **RetrievalEngine**: 检索引擎

### 3. 学习引擎 (src/learning/)
- **WebSearcher**: 网络搜索
- **ContentParser**: 内容解析
- **KnowledgeExtractor**: 知识提取
- **LearningEngine**: 学习引擎主类

### 4. 日报系统 (src/daily/)
- **DailyReportGenerator**: 日报生成器
- **SkillTracker**: 技能追踪器

### 5. CLI界面 (src/cli/)
- **commands.py**: 命令处理
- **interactive.py**: 交互模式

### 6. 核心模块 (src/core/)
- **agent.py**: PyAgent主类
- **config.py**: 配置管理
- **daemon.py**: 守护进程

## CLI命令

```bash
myagent init          # 初始化Agent
myagent chat          # 交互对话
myagent chat -m "..." # 单条消息
myagent learn         # 手动学习
myagent report        # 查看日报
myagent skills        # 查看技能树
myagent knowledge "..." # 搜索知识库
myagent daemon start  # 启动守护进程
myagent daemon stop   # 停止守护进程
myagent daemon status # 查看状态
```

## 依赖项

主要依赖：
- **LLM SDKs**: anthropic, openai
- **向量数据库**: chromadb, sentence-transformers
- **Web抓取**: beautifulsoup4, aiohttp, feedparser
- **CLI**: rich, click, prompt_toolkit
- **配置**: pyyaml, python-dotenv
- **调度**: apscheduler
- **Git**: gitpython

## 知识库结构

```
data/knowledge/
├── patterns/          # 设计模式
├── architectures/     # 架构模式
├── best_practices/    # 最佳实践
├── python_features/   # Python特性
└── general/           # 通用知识
```

## 配置说明

主配置文件 `config/config.yaml`：
- **model**: 模型配置（Claude/OpenAI/本地）
- **knowledge**: 知识库配置
- **learning**: 学习源和调度配置
- **daily**: 日报配置
- **cli**: CLI界面配置
- **daemon**: 守护进程配置

## 扩展性

### 添加新的LLM支持
1. 在 `src/models/` 创建新文件
2. 继承 `BaseLLM` 类
3. 在 `factory.py` 中注册

### 添加新的学习源
1. 编辑 `config/config.yaml`
2. 在 `learning.sources` 添加配置
3. 在 `searcher.py` 实现抓取逻辑

### 自定义提示词
编辑 `config/prompts/` 下的模板文件

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_models.py
pytest tests/test_knowledge.py
pytest tests/test_integration.py
```

## 开发工具

```bash
# 代码格式化
black src/

# 代码检查
ruff check src/

# 类型检查
mypy src/
```

## 许可证

MIT License
