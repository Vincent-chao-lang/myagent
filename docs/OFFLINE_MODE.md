# 离线模式与网络请求说明

## 问题说明

当您运行 PyAgent 时看到以下警告：
```
Warning: You are sending unauthenticated requests to the HF Hub.
```

这是因为嵌入模型（用于文本向量化）默认从 Hugging Face Hub 下载。

## 解决方案

### 方案1: 禁用向量数据库（推荐，完全离线）

编辑 `config/config.yaml`：

```yaml
knowledge:
  use_vector_db: false  # 禁用向量数据库
  offline_mode: true     # 启用离线模式
```

这样只会使用文件存储，不会访问任何网络服务。

### 方案2: 使用本地模型缓存

嵌入模型会自动缓存到本地，首次下载后即可离线使用：

```yaml
knowledge:
  embedding_cache_dir: "./data/models/sentence_transformers"  # 本地缓存目录
  use_vector_db: true   # 仍使用向量库
```

首次运行时会下载模型（约100MB），之后即可离线使用。

### 方案3: 设置环境变量

设置环境变量指定缓存目录：

```bash
export SENTENCE_TRANSFORMERS_HOME=./data/models/sentence_transformers
export HF_HUB_OFFLINE=1
```

## 配置对比

| 配置 | 网络请求 | 功能 | 推荐场景 |
|------|----------|------|----------|
| `use_vector_db: false` | ❌ 无 | 文件存储+关键词搜索 | 完全离线 |
| `offline_mode: true` | ❌ 无 | 仅文件存储 | 纯本地环境 |
| 默认配置 | ✅ 首次下载 | 文件+向量+语义搜索 | 功能完整 |

## 完整离线配置示例

```yaml
# config/config.yaml
knowledge:
  file_store_path: "./data/knowledge"
  vector_db_path: "./data/vector_db"
  embedding_model: "all-MiniLM-L6-v2"
  use_vector_db: false  # 禁用向量数据库
  offline_mode: true     # 离线模式
```

## 注意事项

- **禁用向量库后**：搜索功能变为关键词匹配，语义搜索不可用
- **建议**：首次运行时保持默认配置，让模型下载到本地缓存，之后切换到离线模式

## 验证配置

```bash
# 检查当前配置
myagent init

# 查看日志，确认模式
grep "离线模式" ./data/logs/agent.log
```
