"""学习流程固定测试集

用于确保代码修改后可以进行差异对比
"""

# 固定的测试输入（模拟网络搜索结果）
FIXED_SEARCH_RESULTS = [
    {
        "url": "https://docs.python.org/3/whatsnew/3.11.html",
        "title": "Python 3.11 新特性",
        "content": """
# Python 3.11 新特性

## 1. 异常组和 except* 语法

Python 3.11 引入了 ExceptionGroup 和 except* 语法，可以同时处理多个异常。

```python
try:
    raise ExceptionGroup("multiple", [
        ValueError("value error"),
        TypeError("type error")
    ])
except* ValueError as e:
    print(f"Caught ValueError: {e}")
except* TypeError as e:
    print(f"Caught TypeError: {e}")
```

## 2. Self 类型

Python 3.11 添加了 Self 类型，用于表示返回类型是类本身。

```python
from typing import Self

class Node:
    def set_next(self, node: 'Node') -> Self:
        self.next = node
        return self
```

## 3. 性能提升

Python 3.11 比之前版本快 60% 左右，主要得益于：
- 更快的解释器启动
- 优化的字节码执行
- 改进的垃圾回收
""",
        "source": "Python Official Docs"
    },
    {
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "title": "FastAPI 教程",
        "content": """
# FastAPI 最佳实践

## 依赖注入

FastAPI 内置了强大的依赖注入系统：

```python
from fastapi import Depends, FastAPI

app = FastAPI()

async def get_db():
    # 数据库连接
    pass

@app.get("/users/")
async def read_users(db = Depends(get_db)):
    return db.query("SELECT * FROM users")
```

## 类型验证

自动请求验证：

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

@app.post("/users/")
async def create_user(user: User):
    return {"message": f"Created user {user.name}"}
```
""",
        "source": "FastAPI Docs"
    },
    {
        "url": "https://realpython.com/python-async-io/",
        "title": "Python Async IO 深度解析",
        "content": """
# Python Async IO 深度解析

## asyncio 基础

asyncio 是 Python 的异步 I/O 库：

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)  # 模拟 I/O
    return "data"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

## 并发执行

使用 asyncio.gather 并发执行多个协程：

```python
async def main():
    results = await asyncio.gather(
        fetch_data(),
        fetch_data(),
        fetch_data()
    )
    print(results)
```
""",
        "source": "Real Python"
    }
]

# 期望的提取结果（作为基准）
FIXED_EXPECTED_EXTRACTIONS = [
    {
        "title": "Python 3.11 异常组和 except* 语法",
        "category": "feature",
        "content": "Python 3.11 引入了 ExceptionGroup 和 except* 语法，可以同时处理多个异常。",
        "code_example": "try:\n    raise ExceptionGroup(...)\nexcept* ValueError as e:\n    ...",
        "tags": ["python-3.11", "exception", "async"]
    },
    {
        "title": "FastAPI 依赖注入模式",
        "category": "best_practice",
        "content": "FastAPI 内置了强大的依赖注入系统，使用 Depends() 实现依赖注入。",
        "code_example": "async def read_users(db = Depends(get_db)):\n    return db.query(...)",
        "tags": ["fastapi", "dependency-injection", "web"]
    },
    {
        "title": "asyncio 并发执行",
        "category": "feature",
        "content": "使用 asyncio.gather 可以并发执行多个协程，提高 I/O 密集型任务的性能。",
        "code_example": "results = await asyncio.gather(fetch1(), fetch2(), fetch3())",
        "tags": ["async", "asyncio", "concurrency"]
    }
]
