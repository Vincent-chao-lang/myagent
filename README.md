# PyAgent - 自进化Python专家Agent

基于大模型的自主进化Python专家Agent，每天主动从网络学习新技术和最佳实践，持续增强自身能力。

---

## 🎯 定位

### 身份定位

**PyAgent** 是一个 **Python 专家**，同时兼具 **"全栈独立开发者 + 资深顾问"** 的混合体。不仅精通代码实现，更关注产品架构、业务价值、技术选型及工程化落地。

### 核心特性：🧠 自动学习与进化

PyAgent 不是静态的知识库，而是一个**会自动学习和进化的智能体**：

- **每日主动学习**：每天自动从网络搜索、获取、学习最新的 Python 技术文章和最佳实践
- **知识积累**：将学习到的知识结构化存储到知识库（文件 + 向量数据库）
- **能力进化**：随着知识库的积累，对话能力和建议质量持续提升
- **技能追踪**：自动追踪技能树变化，可视化展示成长轨迹
- **学习日报**：每天生成学习报告，记录新学到的知识和技能

### 核心能力

| 能力领域 | 说明 |
|---------|------|
| **Python 全栈** | 精通 Python 语法、特性（3.11+）、异步编程、性能优化 |
| **Web 框架** | 熟练掌握 Django、FastAPI、Flask，能从零构建高并发 Web 服务 |
| **架构与设计** | 具备系统架构设计能力，熟悉微服务、单体架构、DDD（领域驱动设计）及设计模式 |
| **工程化工具** | 精通 Docker、CI/CD、pytest、mypy、ruff、git workflow 等现代开发工具链 |
| **数据库与存储** | 精通 SQL (PostgreSQL/MySQL) 及 NoSQL (Redis/Mongo) 的设计与优化 |
| **独立开发思维** | 懂得 MVP（最小可行性产品）构建，追求开发效率与产品稳定性的平衡 |

### 思考与回答原则

1. **双重视角**
   - **开发者视角**：代码必须健壮、可维护、符合 PEP 8 规范，优先使用类型提示
   - **顾问视角**：在提供代码前，先评估技术选型、扩展性、安全性和成本

2. **结果导向**
   - 提供可直接运行的代码示例
   - 附带清晰的注释和文档字符串

3. **现代实践**
   - 优先使用 Python 3.11+ 新特性（如 `Self`, `ExceptionGroup`, `str.removeprefix` 等）
   - 推荐使用 `pydantic`, `httpx`, `structlog` 等现代库

4. **全面解答**
   - 不仅解决"怎么写代码"
   - 还要解决"怎么部署"、"怎么测试"、"怎么优化"

### 代码风格要求

- ✅ 遵循 PEP 8 规范
- ✅ 必须使用 Type Hints（类型提示）
- ✅ 使用 `dataclass` 或 `pydantic` 定义数据结构
- ✅ 异步代码必须正确处理生命周期和异常
- ✅ 关键逻辑必须写注释

---

## ⚡ 核心特性

### 🤖 多模型支持

| 模型类型 | type值 | API密钥环境变量 | BASE_URL环境变量 | 特点 |
|---------|--------|----------------|-----------------|------|
| Claude | `claude` | `ANTHROPIC_API_KEY` | `ANTHROPIC_BASE_URL` | 顶级理解能力 |
| OpenAI GPT | `openai` | `OPENAI_API_KEY` | `OPENAI_BASE_URL` | 通用能力强 |
| 智谱GLM | `glm` | `ZHIPUAI_API_KEY` | `ZHIPUAI_BASE_URL` | **默认模型**，国内推荐 |
| 通义千问 | `qwen` | `DASHSCOPE_API_KEY` | `DASHSCOPE_BASE_URL` | 阿里出品，中文优化 |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` | `DEEPSEEK_BASE_URL` | 性价比高 |
| Kimi | `kimi` | `MOONSHOT_API_KEY` | `MOONSHOT_BASE_URL` | 长文本支持 |
| 本地模型 | `local` | - | `LOCAL_MODEL_ENDPOINT` | 完全离线 |

### 📚 混合知识存储

```
data/
├── knowledge/          # 文件存储 (结构化知识)
│   ├── patterns/       # 设计模式
│   ├── architectures/  # 架构模板
│   └── best_practices/ # 最佳实践
└── vector_db/          # ChromaDB 向量数据库 (语义检索)
```

### 🌐 主动学习系统

- 每天定时自动从网络搜索Python新技术
- 源头：Python官方博客、GitHub热门项目、技术社区
- 提取：新特性、最佳实践、代码示例、架构模式
- 记录：学习时长、阶段耗时统计

### 📊 日报生成

每天生成学习日报，包含：
- 学习主题和核心知识
- 代码示例和链接
- 技能变化追踪
- 学习耗时统计

### 🧠 技能→行为转化 ⭐ **核心创新**

将学到的技能自动转化为Agent的行为策略：

| 学到的技能 | 转化的行为 | 触发条件 |
|-----------|-----------|---------|
| type-hints | enforce_type_hints | 代码示例自动添加类型提示 |
| async/await | prefer_async | I/O操作推荐异步方案 |
| pytest | prefer_pytest | 测试时推荐pytest框架 |
| FastAPI | recommend_fastapi | Web开发推荐FastAPI |
| Django | recommend_django | 大型Web项目推荐Django |
| Flask | recommend_flask | 轻量级Web推荐Flask |

**置信度计算**：`min(mentions / 20, 1.0)` - 20次学习达到满置信度

### 🔄 反馈驱动进化

基于用户反馈自动改进：
- 收集用户评分 (1-5星)
- 分析低分原因 (内容太简略、没有代码、不相关等)
- 自动调整提取策略和提示词风格
- 记录进化历史

### 🧪 差异测试

- 使用固定测试集评估代码变化影响
- 对比当前版本与基准版本
- 确保改进不会降低质量

---

## 🚀 快速开始

### 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
```

### 初始化

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env，填入API密钥
vim .env

# 初始化Agent
myagent init
```

### 使用

```bash
# 启动守护进程（后台定时学习）
myagent daemon start

# 手动触发学习
myagent learn

# 查看学习日报
myagent report

# 查看技能树
myagent skills

# 查看激活的行为策略 ⭐
myagent policies

# 搜索知识库
myagent knowledge "async best practices"

# 交互对话
myagent chat
```

---

## 📁 项目结构

```
myagent/
├── src/                         # 源代码
│   ├── core/                    # 核心层
│   │   ├── agent.py             # Agent主类
│   │   ├── config.py            # 配置管理 (.env优先)
│   │   └── daemon.py            # 守护进程
│   ├── models/                  # 模型层
│   │   └── factory.py           # 统一LLM接口
│   ├── knowledge/               # 知识层
│   │   ├── hybrid_store.py      # 混合存储 (文件+向量)
│   │   └── retrieval.py         # 检索引擎
│   ├── learning/                # 学习层
│   │   ├── searcher.py          # 网络搜索
│   │   ├── parser.py            # 内容解析
│   │   └── extractor.py         # 知识提取
│   ├── skills/                  # 进化层 ⭐
│   │   └── application.py       # 技能→行为转化
│   ├── feedback/                # 反馈收集
│   │   └── collector.py         # 反馈统计
│   ├── evolution/               # 进化引擎
│   │   └── engine.py            # 反馈驱动进化
│   ├── improvement/             # 自评估改进
│   │   └── engine.py            # 主动自我改进
│   ├── daily/                   # 日报系统
│   │   ├── report.py            # 日报生成
│   │   └── skills.py            # 技能追踪
│   └── cli/                     # 交互层
│       ├── commands.py          # CLI命令
│       └── interactive.py       # 交互模式
├── config/                      # 配置文件
│   ├── config.yaml              # 复杂配置（列表类型）
│   └── prompts/                 # 提示词模板
├── data/                        # 数据目录
│   ├── knowledge/               # 知识文件
│   ├── vector_db/               # 向量数据库
│   ├── reports/                 # 学习日报
│   ├── skill_applications/      # 行为策略配置
│   ├── feedbacks/               # 用户反馈
│   ├── evolution/               # 进化历史
│   └── logs/                    # 日志文件
└── tests/                       # 测试
    └── fixtures/                # 固定测试集
```

---

## ⚙️ 配置说明

### 主配置文件 (.env) - 优先

```bash
# ========== 模型选择 ==========
MODEL_TYPE=glm                 # claude | openai | glm | qwen | deepseek | kimi | local

# ========== GLM 配置（默认模型）==========
ZHIPUAI_API_KEY=your_key
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
GLM_MODEL=glm-4.7              # 默认模型
GLM_MAX_TOKENS=4096
GLM_TEMPERATURE=0.7

# ========== OpenAI 配置 ==========
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo

# ========== Claude 配置 ==========
ANTHROPIC_API_KEY=your_key
ANTHROPIC_BASE_URL=https://api.anthropic.com

# ========== 知识库配置 ==========
USE_VECTOR_DB=true             # 是否使用向量数据库
OFFLINE_MODE=false             # 离线模式（避免访问HuggingFace）
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ========== 学习配置 ==========
LEARNING_SCHEDULE=02:00        # 每天学习时间
MAX_DAILY_LEARNINGS=50         # 最大每日学习条数

# ========== 其他配置 ==========
LOG_LEVEL=INFO
```

### 辅助配置文件 (config.yaml)

```yaml
# 学习源配置（列表类型，无法放在.env中）
learning:
  sources:
    - type: "github"
      name: "Trending Python"
      query: "language:python"
    - type: "pypi"
      name: "PyPI New Packages"

  search_queries:
    - "Python 3.12 新特性详解"
    - "FastAPI 最佳实践"
    - "异步编程最佳实践"

  focus_areas:
    - "async_programming"
    - "type_hints"
    - "testing"

daily:
  template: "config/prompts/daily_report.md"
  include_code_examples: true
```

### 模型获取

| 模型 | 注册地址 | 特点 |
|------|---------|------|
| Claude | https://console.anthropic.com/ | 顶级理解能力 |
| OpenAI | https://platform.openai.com/ | 通用能力强 |
| 智谱GLM | https://open.bigmodel.cn/ | **新用户免费额度** |
| 通义千问 | https://dashscope.aliyun.com/ | 新用户免费额度 |
| DeepSeek | https://platform.deepseek.com/ | 性价比高 |
| Kimi | https://platform.moonshot.cn/ | 长文本支持 |

---

## 🛠️ CLI命令

```bash
# ========== 基础命令 ==========
myagent init           # 初始化Agent
myagent chat           # 交互对话
myagent chat -m "问题" # 单条消息模式

# ========== 学习相关 ==========
myagent learn          # 手动触发学习
myagent report         # 查看学习日报
myagent report -d 2024-03-14  # 查看指定日期日报
myagent skills         # 显示技能树
myagent knowledge "查询"  # 搜索知识库

# ========== 进化相关 ⭐ ==========
myagent policies       # 查看激活的行为策略
myagent feedback       # 查看反馈统计
myagent evolve         # 触发进化循环
myagent self_improve   # 触发自评估改进
myagent test           # 运行差异测试
myagent test --update-baseline  # 更新基准

# ========== 守护进程 ==========
myagent daemon start   # 启动守护进程
myagent daemon stop    # 停止守护进程
myagent daemon status  # 查看状态

# ========== 反馈评分 ==========
myagent rate <learning_id> --rating 5 --useful
```

---

## 🧬 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                         PyAgent                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   用户对话   │  │  定时学习    │  │   主动进化           │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         ▼                ▼                     ▼             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Agent Core                           ││
│  │  - 检索相关知识  - 构建提示  - 调用LLM  - 应用策略      ││
│  └─────────────────────────────────────────────────────────┘│
│         │                │                     │             │
│         ▼                ▼                     ▼             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 混合知识库   │  │ 学习引擎     │  │   进化引擎           │  │
│  │ ├文件存储   │  │ ├网络搜索   │  │ ├技能→行为转化      │  │
│  │ └向量检索   │  │ ├知识提取   │  │ ├反馈驱动进化       │  │
│  └─────────────┘  │ └技能追踪   │  │ └自评估改进         │  │
│                   └─────────────┘  └─────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    LLM 工厂                              │  │
│  │  Claude | OpenAI | GLM | Qwen | DeepSeek | Kimi | Local │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 创新点

### 1. 技能行为化
不只是记录技能，而是转化为实际行为：
- 学到 "type-hints" → 代码示例自动添加类型提示
- 学到 "async" → I/O操作推荐异步方案
- 置信度驱动：学习次数越多，策略越强

### 2. 双重进化机制
- **反馈驱动**：用户评分触发自动改进
- **自我评估**：主动检测性能并优化

### 3. 可追溯学习
- Git提交每次学习
- 记录进化历史
- 支持回滚和对比

### 4. 差异测试保证
- 固定测试集评估
- 确保进化不降低质量

### 5. 离线优先
- 支持离线模式
- 本地缓存嵌入向量
- 避免频繁访问外部服务

---

## 📓 实践收获：自适应Agent的边界

经过项目实践，我们发现**自适应Agent**面临根本性挑战。以下是关于Agent进化模式的观察：

### 两种进化模式

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   类型A：长期非连续                    类型B：连续非短期      │
│   (PyAgent类)                         (OpenClaw类)          │
│                                                              │
│   时间轴：  ─────────────────────────►       ───────►       │
│            └─┘  └─┘  └─┘                    ┌─┐┌─┐┌─┐       │
│              ↓    ↓    ↓                    ││││││         │
│            改进点稀疏                      连续改进           │
│            (反馈难得)                      (即时反馈)         │
│                                                              │
│   进化曲线：    ┌──┐    ┌─              进化曲线：           │
│                │   │   │                 ╱                  │
│             ───┘   └───┘───            ╱                   │
│                                          ╱                   │
│           阶梯式上升（长期）             快速饱和（短期）     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 核心差异

| 维度 | 长期非连续 | 连续非长期 |
|------|-----------|-----------|
| **典型场景** | 对话、推荐、创作 | 工具、游戏、编译器 |
| **反馈** | 稀疏、延迟 | 密集、即时 |
| **验证** | 困难（主观） | 容易（客观） |
| **进化曲线** | 阶梯式、长期向上 | 快速上升、早期饱和 |
| **天花板** | 很高或没有 | 较低（问题本身有界） |
| **适合自适应** | ❌ 困难 | ✅ 容易 |

### 为什么？

**连续非长期（OpenClaw等工具型）**：
- 修改 → 测试 → 结果（秒级）
- 100次迭代 = 100次有效反馈
- 每次反馈都是明确的对/错
- **容易形成快速进化循环**

**长期非连续（PyAgent等对话型）**：
- 改进 → 等待用户使用 → 可能没反馈
- 100次改进 → 可能只有5个反馈
- 反馈内容是"感觉不好用"（主观模糊）
- **难以形成有效循环**

### 结论

> **自适应Agent目前只在"连续反馈、可验证"的场景下可行**

这就是为什么：
- ✅ 游戏AI、编译器优化、工具类 可以自适应
- ❌ 对话Agent、推荐系统、创作助手 难自适应

**PyAgent的定位调整**：现阶段更适合"辅助进化"（人类驱动 + Agent辅助），而非"完全自适应"。保留可验证的改进机制（代码质量、去重、测试覆盖率），对主观质量部分接受人工反馈驱动。

---

## 🔧 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
ruff check src/

# 类型检查
mypy src/
```

---

## 📄 License

MIT
