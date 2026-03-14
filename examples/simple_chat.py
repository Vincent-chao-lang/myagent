"""
简单的PyAgent对话示例

运行方式:
    python examples/simple_chat.py
"""

import asyncio
from src.core.agent import PyAgent


async def main():
    """主函数"""
    # 创建并初始化Agent
    print("🤖 初始化PyAgent...")
    agent = PyAgent()
    await agent.initialize()

    # 示例问题
    questions = [
        "Python中asyncio和threading有什么区别？",
        "如何使用Python的类型提示？",
        "FastAPI和Flask有什么不同？"
    ]

    for question in questions:
        print(f"\n💭 问题: {question}")
        print("🤔 思考中...")

        response = await agent.chat(question)

        print(f"\n🤖 回答:\n{response}\n")
        print("-" * 50)

    # 查看当前技能
    print("\n📊 当前技能概览:")
    skills = agent.get_skills()
    print(f"   总技能数: {skills['total_skills']}")
    print(f"   总提及: {skills['total_mentions']}")

    # 关闭Agent
    await agent.close()
    print("\n👋 再见!")


if __name__ == "__main__":
    asyncio.run(main())
