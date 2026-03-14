"""
知识库搜索示例

运行方式:
    python examples/knowledge_search.py
"""

import asyncio
from src.core.agent import PyAgent


async def main():
    """主函数"""
    print("🤖 初始化PyAgent...")
    agent = PyAgent()
    await agent.initialize()

    # 添加一些示例知识
    print("\n📝 添加示例知识...")

    example_knowledges = [
        {
            "content": """
Python异步编程使用async/await语法。

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "Data"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```
            """,
            "metadata": {
                "title": "Python Async Await",
                "category": "practice",
                "tags": ["async", "await", "asyncio"]
            }
        },
        {
            "content": """
Python类型提示使用typing模块。

```python
from typing import List, Optional

def process_items(items: List[str]) -> Optional[int]:
    if not items:
        return None
    return len(items)
```
            """,
            "metadata": {
                "title": "Python Type Hints",
                "category": "practice",
                "tags": ["typing", "type hints"]
            }
        }
    ]

    for knowledge in example_knowledges:
        await agent.knowledge.add(
            content=knowledge["content"],
            metadata=knowledge["metadata"]
        )
        print(f"   ✓ 添加: {knowledge['metadata']['title']}")

    # 搜索知识
    queries = ["async", "typing", "python"]

    for query in queries:
        print(f"\n🔍 搜索: '{query}'")
        results = await agent.search_knowledge(query, top_k=3)

        if results:
            for i, result in enumerate(results, 1):
                title = result.get('title', result.get('metadata', {}).get('title', '无标题'))
                content = result.get('content', '')[:100]
                print(f"   {i}. {title}")
                print(f"      {content}...")
        else:
            print("   未找到相关结果")

    await agent.close()
    print("\n👋 完成!")


if __name__ == "__main__":
    asyncio.run(main())
