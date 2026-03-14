"""
学习和报告示例

运行方式:
    python examples/learn_and_report.py
"""

import asyncio
from src.core.agent import PyAgent


async def main():
    """主函数"""
    print("🤖 初始化PyAgent...")
    agent = PyAgent()
    await agent.initialize()

    # 执行学习
    print("\n📚 开始学习流程...")
    result = await agent.daily_learning()

    print(f"\n✓ 学习完成:")
    print(f"   搜索结果: {result.get('search_results', 0)} 条")
    print(f"   提取知识: {result.get('learnings', 0)} 条")
    print(f"   添加到库: {result.get('added', 0)} 条")

    # 查看日报
    print("\n📄 今日学习日报:")
    report = await agent.get_daily_report()
    print(report[:500] + "...")  # 显示前500字符

    # 查看技能变化
    print("\n📊 技能变化:")
    skills = agent.get_skills()
    top_skills = agent.get_skill_cloud(10)
    for name, count in top_skills:
        print(f"   {name}: {count}")

    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
