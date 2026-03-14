# PyAgent 更新说明

## 2025-03-13 更新

### ✅ 已完成的修改

#### 1. 配置接入GLM模型

**修改文件**: `config/config.yaml`

```yaml
model:
  type: "glm"  # 默认使用智谱GLM模型
  glm:
    model: "glm-4-flash"  # 速度快，有免费额度
    max_tokens: 4096
    temperature: 0.7
```

**说明**:
- 默认模型从 `claude` 改为 `glm`
- 使用 `glm-4-flash` 模型（速度快，新用户有免费额度）
- 仍可通过修改配置切换到其他模型

#### 2. 学习时长记录功能

**修改文件**:
- `src/learning/engine.py` - 添加时长记录
- `src/daily/report.py` - 添加时长格式化和展示
- `src/core/agent.py` - 传递学习统计信息
- `config/prompts/daily_report.md` - 更新日报模板

**新增功能**:
- 记录每个学习阶段的耗时（搜索、解析、提取）
- 记录总学习时长
- 在日报中展示详细用时分析

**日报新增字段**:
```markdown
## 📊 学习统计
- **学习时长**: {learning_duration}

## ⏱️ 学习用时分析
- **网络搜索**: {search_time}
- **内容解析**: {parse_time}
- **知识提取**: {extract_time}
- **总计用时**: {total_time}
```

### 📝 使用说明

#### 配置GLM模型

1. 获取API密钥: https://open.bigmodel.cn/
2. 配置环境变量:

```bash
# 编辑 .env 文件
ZHIPUAI_API_KEY=your_api_key_here
```

3. 确认配置文件 `config/config.yaml`:

```yaml
model:
  type: "glm"  # 确认是 glm
```

4. 运行:

```bash
myagent chat
```

#### 查看学习时长

执行学习后，日报会自动记录和展示时长信息：

```bash
myagent learn
myagent report  # 查看包含时长的日报
```

### 📊 示例日报

查看 `docs/DAILY_REPORT_EXAMPLE.md` 了解日报格式。

### 🔧 技术细节

**时长记录实现**:

```python
# 学习引擎记录各阶段时长
stage_times = {
    "search": time.time() - stage_start,
    "parse": time.time() - stage_start,
    "extract": time.time() - stage_start
}
total_time = time.time() - start_time
```

**时长格式化**:

```python
def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}分钟"
    else:
        return f"{int(hours)}小时{int(minutes)}分钟"
```

### 🚀 后续优化建议

1. 添加学习效率分析（每小时学习条目数）
2. 记录每日累计学习时长
3. 添加学习时长趋势图表
4. 支持设置学习时长上限

---

## 2025-03-13 更新 (补充)

#### 3. 统一BASE_URL配置支持

**问题**: 原本只有OpenAI支持自定义BASE_URL，其他模型不支持

**修改文件**:
- `config/config.yaml` - 为所有模型添加base_url配置
- `.env.example` - 添加所有模型的BASE_URL环境变量
- `src/core/config.py` - 添加所有模型BASE_URL属性
- `src/models/factory.py` - 实现BASE_URL合并逻辑
- `src/models/glm.py` - GLM模型支持自定义base_url
- `src/models/qwen.py` - Qwen模型支持自定义base_url

**新增功能**:
- 所有模型都支持自定义API端点
- 环境变量优先级高于config.yaml
- 统一的BASE_URL配置方式

**支持的BASE_URL环境变量**:
```bash
ANTHROPIC_BASE_URL    # Claude
OPENAI_BASE_URL       # OpenAI
ZHIPUAI_BASE_URL      # 智谱GLM
DASHSCOPE_BASE_URL    # 通义千问
DEEPSEEK_BASE_URL     # DeepSeek
MOONSHOT_BASE_URL     # Kimi
LOCAL_MODEL_ENDPOINT  # 本地模型
```

**配置优先级**:
```
环境变量 (.env) > config.yaml > 代码默认值
```

**使用场景**:
1. 使用代理服务访问国外API
2. 使用第三方兼容OpenAI格式的服务
3. 连接企业内部部署的模型服务
4. 开发/生产环境端点切换

**详细文档**: 查看 `docs/BASE_URL_CONFIG.md`

---

## 2025-03-14 更新

#### 4. 离线模式与避免HF Hub访问

**问题**: 嵌入模型默认从 Hugging Face Hub 下载，导致网络请求

**修改文件**:
- `config/config.yaml` - 添加离线模式配置选项
- `src/models/embedding.py` - 支持本地缓存和离线模式
- `src/knowledge/hybrid_store.py` - 支持禁用向量数据库
- `src/core/config.py` - 添加离线模式配置属性

**新增配置**:
```yaml
knowledge:
  use_vector_db: false    # 禁用向量数据库（完全离线）
  offline_mode: true       # 启用离线模式
  embedding_cache_dir: "./data/models/sentence_transformers"
```

**功能说明**:
- **禁用向量库**: 只使用文件存储，完全避免网络请求
- **离线模式**: 不访问任何外部服务
- **本地缓存**: 模型自动缓存到本地，首次下载后可离线使用

**使用方式**:

方式1: 完全离线（推荐）
```yaml
# config/config.yaml
knowledge:
  use_vector_db: false
  offline_mode: true
```

方式2: 使用本地缓存
```bash
# 设置环境变量
export SENTENCE_TRANSFORMERS_HOME=./data/models/sentence_transformers
```

**注意**: 禁用向量库后，搜索功能变为关键词匹配，语义搜索不可用

**详细文档**: 查看 `docs/OFFLINE_MODE.md`

---

## 2025-03-14 更新（补充）

#### 5. 学习方向优化

**问题**: 原始学习效果差，只获取到包名没有实际内容

**修改文件**:
- `config/config.yaml` - 明确学习方向和搜索查询
- `src/learning/searcher.py` - 优化内容获取，获取README和完整文章
- `src/learning/extractor.py` - 改进知识提取逻辑和验证
- `config/prompts/knowledge_extraction.md` - 优化提示词模板

**新增配置**:
```yaml
learning:
  # 明确的学习方向
  focus_areas:
    - async_programming
    - design_patterns
    - testing
    - performance
    - best_practices
    - type_hints
    - data_structures
    - algorithms

  # 优化的搜索查询
  search_queries:
    - "Python 3.12 新特性详解"
    - "Python type hints 最佳实践"
    - "FastAPI 最佳实践 完整教程"
    - "Pytest 测试技巧 高级用法"
```

**改进效果**:
| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 内容质量 | ❌ 只有包名 | ✅ 完整文章/README |
| 知识提取 | ❌ 提取失败 | ✅ 结构化提取 |
| 代码示例 | ❌ 无 | ✅ 有代码示例 |
| 技能标签 | ❌ 无效 | ✅ 有效标签 |

**详细文档**: 查看 `docs/LEARNING_OPTIMIZATION.md`

---

## 2025-03-14 更新（再次补充）

#### 6. 启用向量数据库和语义检索

**问题**: 关键词搜索过于简单，无法进行语义理解

**修改文件**:
- `config/config.yaml` - 启用 `use_vector_db: true`

**新增功能**:
- 启用 ChromaDB 向量数据库
- 支持语义检索（基于 sentence-transformers）
- 混合搜索策略：文件关键词 + 向量语义

**配置说明**:
```yaml
knowledge:
  use_vector_db: true  # 启用向量数据库
  embedding_cache_dir: "./data/models/sentence_transformers"  # 模型本地缓存
```

**语义检索效果**:
| 搜索方式 | 之前 | 现在 |
|----------|------|------|
| 搜索 "异步" | 只匹配 "异步" 关键词 | 匹配 "async/await" "协程" "并发" |
| 搜索 "性能优化" | 只匹配 "性能优化" 关键词 | 匹配 "optimization" "提速" "高效" |
| 搜索 "设计模式" | 只匹配 "设计模式" 关键词 | 匹配 "singleton" "factory" "observer" |

**混合搜索策略**:
```python
# 并行搜索文件存储和向量数据库，然后合并去重
file_results, vector_results = await asyncio.gather(
    file_store.search(query, top_k),
    vector_store.search(query, top_k)
)
```

**首次运行说明**:
- 首次运行时会自动下载 `all-MiniLM-L6-v2` 模型
- 模型会缓存到 `./data/models/sentence_transformers`
- 之后可设置 `offline_mode: true` 完全离线使用

---

## 2025-03-14 更新（第三次补充）

#### 7. 统一配置到 .env 文件

**问题**: 模型配置分散在 config.yaml 和 .env 两个文件中，管理不便

**修改文件**:
- `src/core/config.py` - 支持从环境变量读取所有模型配置
- `src/models/factory.py` - 简化配置合并逻辑
- `.env.example` - 更新为完整的配置示例

**新增功能**:
- 所有模型配置都可以在 .env 中设置
- 环境变量优先级高于 config.yaml
- 配置更集中，便于管理

**.env 配置示例**:
```bash
# 选择模型
MODEL_TYPE=glm

# GLM 完整配置
ZHIPUAI_API_KEY=your_key
GLM_MODEL=glm-4-flash
GLM_MAX_TOKENS=4096
GLM_TEMPERATURE=0.7
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

**配置优先级**:
```
.env 环境变量 > config.yaml
```

**支持的 .env 配置项**:
| 配置项 | 说明 |
|--------|------|
| `MODEL_TYPE` | 模型类型选择 |
| `GLM_MODEL` | GLM 模型名称 |
| `GLM_MAX_TOKENS` | 最大输出 token 数 |
| `GLM_TEMPERATURE` | 温度参数 |
| `GLM_BASE_URL` | API 端点 |
| ...其他模型同理 | |

**使用方式**:
1. 复制 `.env.example` 为 `.env`
2. 修改 `.env` 中的配置
3. 运行程序，自动从 .env 读取配置

---

## 2025-03-14 更新（第四次补充）

#### 8. config.yaml 变为可选，支持纯 .env 配置

**问题**: config.yaml 是必需的，配置分散

**修改文件**:
- `src/core/config.py` - 重写配置类，支持纯环境变量
- `.env.example` - 添加所有配置项

**新增功能**:
- **config.yaml 完全可选**
- 所有配置都支持通过 .env 设置
- 每个配置都有合理的默认值

**最小配置示例** (.env):
```bash
# 只需配置这3行即可运行
MODEL_TYPE=glm
ZHIPUAI_API_KEY=your_key
GLM_MODEL=glm-4-flash
```

**配置优先级**:
```
.env 环境变量 > config.yaml > 代码默认值
```

**支持的 .env 配置项**:
| 分类 | 配置项 | 默认值 |
|------|--------|--------|
| 模型 | `MODEL_TYPE` | `claude` |
| GLM | `GLM_MODEL` | `glm-4-flash` |
| GLM | `GLM_MAX_TOKENS` | `4096` |
| GLM | `GLM_TEMPERATURE` | `0.7` |
| GLM | `GLM_BASE_URL` | `https://open.bigmodel.cn/api/paas/v4` |
| 知识库 | `USE_VECTOR_DB` | `true` |
| 知识库 | `OFFLINE_MODE` | `false` |
| 知识库 | `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` |
| 路径 | `FILE_STORE_PATH` | `./data/knowledge` |
| 路径 | `VECTOR_DB_PATH` | `./data/vector_db` |
| 学习 | `MAX_DAILY_LEARNINGS` | `20` |
| 日报 | `REPORT_PATH` | `./data/reports` |

**使用场景**:

| 场景 | 需要的文件 |
|------|-----------|
| 完整配置 | 只需 `.env` |
| 快速开始 | 只需 `.env` |
| 复杂配置 | `.env` + `config.yaml` (可选) |

**删除 config.yaml 后**:
```bash
# 删除 config.yaml 仍然可以正常运行
rm config/config.yaml
myagent learn  # ✓ 正常工作
```

**✅ 已执行**: config.yaml 已删除，项目现在完全依赖 .env 配置。

---

## 2025-03-14 更新（第五次补充）

#### 9. 恢复精简版 config.yaml

**问题**: 删除 config.yaml 后，列表类型配置（学习源、搜索查询等）无法用环境变量表示

**修改文件**:
- `config/config.yaml` - 恢复精简版，只保留复杂配置
- `.env` - 更新说明

**配置文件分工**:
| 文件 | 用途 | 内容类型 |
|------|------|----------|
| `.env` | 主要配置 | API密钥、模型参数、路径、布尔值等 |
| `config.yaml` | 辅助配置 | 学习源列表、搜索查询、模板路径等 |

**config.yaml 内容**:
```yaml
learning:
  sources:                    # 学习源列表（无法用 .env 表示）
    - type: "github"
      query: "language:python"
    - type: "pypi"
      url: "https://pypi.org"

  search_queries:              # 搜索查询列表
    - "Python 3.12 新特性详解"
    - "FastAPI 最佳实践"

  focus_areas:                 # 学习领域
    - "async_programming"
    - "design_patterns"

daily:
  template: "config/prompts/daily_report.md"
  include_code_examples: true

cli:
  theme: "monokai"

git:
  auto_commit: true
```

**配置优先级**:
```
.env 环境变量 > config.yaml > 代码默认值
```

---

## 2025-03-14 更新（第六次补充）

#### 10. 明确项目定位和代码规范

**修改文件**:
- `README.md` - 添加项目定位、核心能力、代码风格要求

**新增内容**:
- 项目定位：Python 专家 + 全栈独立开发者 + 资深顾问
- 核心能力：Python 全栈、Web框架、架构设计、工程化工具、数据库
- 思考原则：双重视角（开发者+顾问）、结果导向、现代实践
- 代码风格：PEP 8、Type Hints、dataclass/pydantic、异步生命周期管理

**README 新增"定位"部分**:
| 模块 | 内容 |
|------|------|
| 身份定位 | Python 专家 + 全栈独立开发者 + 资深顾问 |
| 核心能力 | Python 全栈、Web框架、架构设计、工程化工具、数据库 |
| 思考原则 | 双重视角、结果导向、现代实践、全面解答 |
| 代码风格 | PEP 8、Type Hints、dataclass/pydantic、异步生命周期 |

---

## 2025-03-14 更新（第七次补充）

#### 11. 添加差异测试框架

**问题**：学习产出不固定，无法对比代码修改前后的效果

**解决方案**：建立可复现的评估体系

**新增文件**:
- `tests/fixtures/learning_fixtures.py` - 固定测试集
- `tests/differential_test.py` - 差异测试框架

**功能说明**:
```bash
# 运行差异测试
myagent test

# 更新基准
myagent test --update-baseline
```

**测试流程**:
1. 使用固定测试集（模拟网络搜索结果）
2. 运行当前版本，提取知识
3. 与保存的基准结果对比
4. 显示改进/退化的指标
5. 判断修改是否正向

**对比指标**:
- 提取数量
- 平均内容长度
- 带代码示例数量
- 带标签数量
- 执行时间

**作用**:
- ✅ 修改代码后可以验证效果
- ✅ 建立"好"的标准
- ✅ 防止代码退化
- ✅ 持续改进有依据

---

## 2025-03-14 更新（第八次补充）

#### 12. 实现主动自我改进循环

**问题**：差异测试由用户手动执行，Agent 无法主动改进自己

**解决方案**：实现主动自我改进引擎

**新增文件**:
- `src/improvement/engine.py` - 自我改进引擎
- `src/improvement/__init__.py` - 模块初始化

**核心功能**:

1. **自动自我评估**
   - 每次学习后自动运行差异测试
   - 对比当前性能与历史基准
   - 分析性能退化或改进

2. **自动生成改进动作**
   - 提取数量下降 → 调整提示词
   - 内容质量下降 → 调整质量阈值
   - 代码示例减少 → 强调代码提取
   - 速度变慢 → 切换更便宜的模型

3. **自动应用改进**
   - 自动修改提示词文件
   - 自动调整配置参数
   - 应用后重新评估验证

**工作流程**:
```
学习完成
    ↓
自我评估（对比基准）
    ↓
发现性能问题？
    ↓ Yes
生成改进动作
    ↓
应用改进
    ↓
重新评估
    ↓
改进有效？
    ↓ Yes
保存改进记录
```

**新增命令**:
```bash
# 手动触发自我评估和改进
myagent self_improve
```

**自动触发**:
- 每次学习完成后自动运行
- 守护进程模式下自动执行
- 后台持续自我优化

**改进历史**:
- 保存在 `data/improvements/improvement_history.json`
- 记录每次改进的时间、动作、效果

**核心特性**:
- ✅ Agent 主动评估自己的性能
- ✅ 自动发现问题
- ✅ 自动生成改进方案
- ✅ 自动应用改进
- ✅ 自动验证改进效果
- ✅ 持续自我进化

---

## 2025-03-14 更新（最终版）

#### 13. 基于用户反馈的进化系统

**核心理念**：主动学习 + 用户反馈 = 持续进化

**新增文件**:
- `src/feedback/collector.py` - 用户反馈收集器
- `src/evolution/engine.py` - 基于反馈的进化引擎

**工作流程**:
```
主动学习 → 对话回答 → 用户反馈 → 分析反馈 → 自我进化 → 循环
```

**用户反馈方式**:

1. **对话中反馈**（推荐）
```bash
myagent chat
# 对话结束后会询问："这个回答对您有帮助吗？(1-5星)"
```

2. **手动评分**
```bash
myagent rate <learning_id> --rating 5 --useful
```

3. **查看统计**
```bash
myagent feedback
# 显示：
# - 总反馈数
# - 平均评分
# - 有用率
# - 主要问题
```

**进化触发条件**:
- 平均评分 < 3.5
- 有用率 < 60%
- 同一问题出现 3 次以上

**进化动作**:
- 提示词风格调整（balanced → detailed → concise → practical）
- 内容阈值调整
- 代码要求调整
- 去重逻辑启用

**手动触发进化**:
```bash
myagent evolve
# 分析7天内的反馈
# 决定是否需要进化
# 自动应用改进
```

**进化历史**:
- 保存在 `data/evolution/evolution_history.json`
- 记录每次进化的时间、触发原因、应用动作

**核心理念**:
> 用户持续使用 = 有价值  
> 用户离开 = 需要改进

**特点**:
- ✅ 不追求绝对标准，只追求相对改进
- ✅ 完全基于用户反馈，用户说好就是好
- ✅ 渐进式进化，允许波动和试错
- ✅ 长期追踪，看趋势而不是单次表现
- ✅ 简单有效，不依赖复杂的评估体系
---

## 2025-03-14 更新（最终版补充）

#### 14. 技能 → 行为 转化系统

**核心理念**：学到的技能不仅仅用于检索，更用于改进自己的行为

**问题**：之前 Agent 只是记录技能，没有主动使用学到的技能

**解决方案**：技能 → 策略 → 行为 的转化机制

**新增文件**:
- `src/skills/application.py` - 技能应用引擎

**工作流程**:
```
学习新知识
    ↓
提取技能标签 (如: type-hints, async, pytest)
    ↓
更新技能统计
    ↓
技能 → 策略映射
    ↓
更新行为策略
    ↓
应用到对话/代码生成
```

**技能 → 行为 映射**:
| 学到的技能 | 转化的行为策略 |
|----------|----------------|
| type-hints, typing | enforce_type_hints: 强调使用类型提示 |
| async, asyncio | prefer_async: I/O操作优先推荐异步 |
| pytest, testing | prefer_pytest: 测试推荐使用pytest |
| FastAPI | recommend_fastapi: 框架推荐FastAPI |
| performance | add_performance_tips: 添加性能优化建议 |

**策略配置**:
```json
{
  "enforce_type_hints": {
    "enabled": true,
    "confidence": 0.85,    // 基于学习次数计算
    "last_updated": "2026-03-14"
  },
  "prefer_async": {
    "enabled": true,
    "io_threshold": 0.3   // I/O占比超过30%时推荐异步
  },
  "recommend_fastapi": {
    "enabled": true,
    "confidence": 0.75,   // 置信度 >= 70% 才启用
    "last_updated": "2026-03-14"
  }
}
```

**应用场景**:

1. **对话时自动推荐**
```
用户: "怎么写一个高并发的API？"
Agent: [推荐使用 FastAPI + asyncio]
       [根据学习到的技能自动推荐]
```

2. **代码生成时应用最佳实践**
```
用户: "帮我写一个处理文件的函数"
Agent: [生成的代码会自动添加类型提示]
       [根据 enforce_type_hints 策略]
```

3. **主动提醒**
```
用户: "这段代码性能不好"
Agent: "💡 考虑使用 asyncio 进行异步I/O操作"
      [根据 prefer_async 策略]
```

**置信度计算**:
```
置信度 = min(学习次数 / 20, 1.0)

- 5次学习 → 25% 置信度 → 不启用
- 10次学习 → 50% 置信度 → 可启用
- 20次学习 → 100% 置信度 → 强烈启用
```

**进化效果**:
```
第1周: 学习到 3 次 "type-hints"
     → 置信度 15% → 不启用策略

第5周: 学习到 12 次 "type-hints"
     → 置信度 60% → 启用策略
     → 回复中开始强调类型提示

第10周: 学习到 25 次 "type-hints"
      → 置信度 100% → 强制启用
      → 所有代码示例都添加类型提示
```

**查看当前策略**:
```bash
myagent policies
# 显示当前激活的行为策略
```
