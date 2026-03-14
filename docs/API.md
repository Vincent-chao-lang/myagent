# PyAgent API 文档

## Python API

### 基本使用

```python
import asyncio
from src.core.agent import PyAgent
from src.core.config import Config

async def main():
    # 创建Agent实例
    agent = PyAgent()
    await agent.initialize()

    # 对话
    response = await agent.chat("如何使用Python的asyncio?")
    print(response)

    # 搜索知识库
    results = await agent.search_knowledge("async", top_k=5)

    # 获取技能
    skills = agent.get_skills()

    # 关闭Agent
    await agent.close()

asyncio.run(main())
```

### 配置自定义

```python
from src.core.config import Config

# 使用自定义配置文件
config = Config("/path/to/custom_config.yaml")

agent = PyAgent(config_obj=config)
```

### 知识库操作

```python
# 添加知识
await agent.knowledge.add(
    content="Python async/await allows concurrent code",
    metadata={
        "title": "Async Programming",
        "category": "practice",
        "tags": ["async", "python"]
    }
)

# 搜索知识
results = await agent.knowledge.search("async programming")
```

### 学习控制

```python
# 手动触发学习
result = await agent.daily_learning()
print(f"学习了 {result['learnings']} 条知识")

# 获取日报
report = await agent.get_daily_report()
print(report)
```

## CLI API

所有CLI命令都可以通过编程方式调用：

```python
from src.cli.commands import cli
from click.testing import CliRunner

runner = CliRunner()

# 执行命令
result = runner.invoke(cli, ['chat', '-m', 'Hello'])
print(result.output)
```

## 扩展

### 自定义学习源

编辑 `config/config.yaml`：

```yaml
learning:
  sources:
    - type: "rss"
      name: "My Blog"
      url: "https://example.com/rss.xml"
```

### 自定义提示词

编辑 `config/prompts/` 下的模板文件：
- `system.md` - 系统提示词
- `knowledge_extraction.md` - 知识提取提示词
- `daily_report.md` - 日报模板
