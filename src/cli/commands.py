"""CLI命令处理"""

import asyncio
import json
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from loguru import logger

from ..core.agent import PyAgent
from ..core.config import config
from ..core.daemon import start_daemon, stop_daemon, daemon_status


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="PyAgent")
def cli():
    """PyAgent - 自进化Python专家Agent"""
    pass


@cli.command()
def init():
    """初始化Agent"""
    console.print(Panel.fit("🤖 [bold blue]PyAgent[/bold blue] 初始化中..."))

    # 创建目录结构
    directories = [
        config.file_store_path,
        config.vector_db_path,
        config.report_path,
        Path("./data/logs"),
        Path("./data/knowledge/patterns"),
        Path("./data/knowledge/architectures"),
        Path("./data/knowledge/best_practices"),
        Path("./data/knowledge/python_features"),
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("创建目录结构...", total=len(directories))

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            progress.update(task, advance=1)

    console.print("✓ 创建项目结构")
    console.print("✓ 初始化配置完成")

    console.print(
        Panel.fit(
            """🎉 [bold green]初始化完成！[/bold green]

接下来：
  1. 编辑 [cyan].env[/cyan] 文件配置API密钥
  2. 运行 [cyan]myagent daemon start[/cyan] 启动守护进程
  3. 运行 [cyan]myagent chat[/cyan] 开始对话""",
            title="提示"
        )
    )


@cli.command()
@click.option("--message", "-m", help="单条消息模式")
def chat(message: Optional[str]):
    """交互对话"""
    asyncio.run(_chat(message))


async def _chat(message: Optional[str]):
    """异步聊天实现"""
    agent = PyAgent()
    await agent.initialize()

    if message:
        # 单条消息模式
        console.print(f"\n💭 [bold cyan]You:[/bold cyan] {message}")

        with console.status("🤔 思考中..."):
            response = await agent.chat(message)

        console.print(f"\n🤖 [bold green]PyAgent:[/bold green]\n{response}\n")
    else:
        # 交互模式
        from .interactive import InteractiveSession
        session = InteractiveSession(agent)
        await session.run()

    await agent.close()


@cli.command()
def learn():
    """手动触发学习"""
    asyncio.run(_learn())


async def _learn():
    """异步学习实现"""
    console.print(Panel.fit("📚 [bold yellow]开始学习流程...[/bold yellow]"))

    agent = PyAgent()
    await agent.initialize()

    try:
        with console.status("🌐 搜索网络资源..."):
            result = await agent.daily_learning()

        console.print(f"\n✓ 搜索完成: {result.get('search_results', 0)} 条结果")
        console.print(f"✓ 提取知识: {result.get('learnings', 0)} 条")
        console.print(f"✓ 添加到知识库: {result.get('added', 0)} 条")

        if "report_path" in result:
            console.print(f"\n📄 日报已保存: {result['report_path']}")

    except Exception as e:
        console.print(f"\n❌ [red]学习失败: {e}[/red]")

    await agent.close()


@cli.command()
@click.option("--date", "-d", help="日期 (YYYY-MM-DD)")
def report(date: Optional[str]):
    """查看学习日报"""
    asyncio.run(_report(date))


async def _report(date: Optional[str]):
    """异步日报实现"""
    from datetime import datetime

    target_date = None
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            console.print("❌ 日期格式错误，请使用 YYYY-MM-DD")
            return

    agent = PyAgent()
    await agent.initialize()

    report_content = await agent.get_daily_report(target_date)

    if target_date:
        console.print(f"\n# 📄 {target_date.strftime('%Y-%m-%d')} 学习日报\n")

    if report_content and "没有找到" not in report_content:
        markdown = Markdown(report_content)
        console.print(markdown)
    else:
        console.print("📭 该日期没有学习记录")

    await agent.close()


@cli.command()
def skills():
    """显示技能树"""
    asyncio.run(_skills())


async def _skills():
    """异步技能显示实现"""
    agent = PyAgent()
    await agent.initialize()

    skill_map = agent.get_skills()

    # 概览
    console.print(f"\n📊 技能概览")
    console.print(f"   总技能数: {skill_map['total_skills']}")
    console.print(f"   总提及: {skill_map['total_mentions']}\n")

    # 分类技能表
    for category, skills in skill_map.get('categories', {}).items():
        console.print(f"\n📁 [bold cyan]{category.title()}[/bold cyan]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("技能", style="green")
        table.add_column("热度", justify="right")
        table.add_column("最后练习", justify="right")

        for skill in skills[:10]:  # 每个类别显示前10个
            last_practiced = skill.get('last_practiced', '未记录')[:10]
            table.add_row(skill['name'], str(skill['mentions']), last_practiced)

        console.print(table)

    # 标签云
    console.print("\n🎯 [bold]技能标签云[/bold]")

    tag_cloud = agent.get_skill_cloud(30)
    for name, count in tag_cloud:
        # 根据热度添加符号
        heat = "🔥" * min(count // 5 + 1, 5)
        console.print(f"{name} {heat}", end=" ")

    console.print("\n")

    await agent.close()


@cli.command()
@click.argument("query")
@click.option("--top-k", "-k", default=5, help="返回结果数量")
def knowledge(query: str, top_k: int):
    """搜索知识库"""
    asyncio.run(_knowledge(query, top_k))


async def _knowledge(query: str, top_k: int):
    """异步知识搜索实现"""
    agent = PyAgent()
    await agent.initialize()

    results = await agent.search_knowledge(query, top_k)

    if not results:
        console.print(f"📭 没有找到关于 '[yellow]{query}[/yellow]' 的知识")
    else:
        console.print(f"\n🔍 搜索结果: '[cyan]{query}[/cyan]' (找到 {len(results)} 条)\n")

        for i, result in enumerate(results, 1):
            title = result.get('title', result.get('metadata', {}).get('title', '无标题'))
            content = result.get('content', '')[:200]
            category = result.get('category', result.get('metadata', {}).get('category', ''))

            console.print(f"{i}. [bold green]{title}[/bold green]")
            if category:
                console.print(f"   📁 类别: {category}")
            console.print(f"   📝 {content}...")
            console.print()

    await agent.close()


@cli.group()
def daemon():
    """守护进程管理"""
    pass


@daemon.command()
def start():
    """启动守护进程"""
    status = daemon_status()

    if status.get("running"):
        console.print("⚠️  守护进程已在运行")
        return

    console.print("🚀 启动守护进程...")
    console.print("💡 提示: 使用 [cyan]myagent daemon stop[/cyan] 停止守护进程")
    console.print("💡 提示: 使用 [cyan]myagent daemon status[/cyan] 查看状态")
    console.print("💡 提示: 日志文件: [cyan]./data/logs/daemon.log[/cyan]")

    start_daemon()


@daemon.command()
def stop():
    """停止守护进程"""
    if stop_daemon():
        console.print("✅ 守护进程已停止")
    else:
        console.print("❌ 守护进程未运行或停止失败")


@daemon.command()
def status():
    """查看守护进程状态"""
    status_info = daemon_status()

    if status_info.get("running"):
        console.print(f"✅ 守护进程运行中")
        console.print(f"   PID: {status_info.get('pid', 'N/A')}")
        console.print(f"   PID文件: {status_info.get('pid_file', 'N/A')}")
    else:
        console.print("⭕ 守护进程未运行")


@cli.command()
def schedule():
    """配置定时任务"""
    schedule_time = config.learning_schedule
    console.print(f"\n⏰ 定时学习时间: [cyan]{schedule_time}[/cyan]")
    console.print(f"💡 编辑 [cyan]config/config.yaml[/cyan] 修改调度时间")


@cli.command()
@click.option("--update-baseline", is_flag=True, help="将当前结果保存为新的基准")
def test(update_baseline: bool = False):
    """运行差异测试"""
    asyncio.run(_run_differential_test(update_baseline))


@cli.command()
def self_improve():
    """触发自我评估和改进"""
    asyncio.run(_run_self_improvement())


async def _run_self_improvement():
    """运行自我改进"""
    from ..improvement.engine import SelfImprovementEngine

    agent = PyAgent()
    await agent.initialize()

    console.print(Panel.fit("🧠 [bold yellow]自我评估与改进[/bold yellow]"))
    console.print("Agent 将主动评估自己的性能，并进行必要的改进\n")

    improvement_engine = SelfImprovementEngine(agent)
    result = await improvement_engine.run_self_improvement_cycle()

    # 显示结果
    console.print(f"\n[bold]状态:[/bold] {result.get('status')}")
    console.print(f"[bold]消息:[/bold] {result.get('message')}")

    if "metrics" in result:
        console.print("\n[cyan]当前指标:[/cyan]")
        for key, value in result["metrics"].items():
            console.print(f"  • {key}: {value}")

    if "suggested_actions" in result:
        console.print(f"\n[cyan]建议的改进 ({len(result['suggested_actions'])}项):[/cyan]")
        for i, action in enumerate(result["suggested_actions"], 1):
            console.print(f"  {i}. [yellow]{action.action_type}[/yellow] → {action.target}")
            console.print(f"     预期效果: {action.expected_impact}")

    if "actions" in result:
        console.print(f"\n[green]✓ 已应用的改进 ({len(result['actions'])}项):[/green]")
        for i, action in enumerate(result["actions"], 1):
            console.print(f"  {i}. {action.get('action_type')} → {action.get('target')}")

    await agent.close()


async def _run_differential_test(update_baseline: bool):
    """运行差异测试"""
    from tests.differential_test import DifferentialTester, run_differential_test
    from tests.fixtures.learning_fixtures import FIXED_SEARCH_RESULTS

    tester = DifferentialTester()

    console.print(Panel.fit("🧪 [bold yellow]差异测试[/bold yellow]"))
    console.print("使用固定测试集对比当前版本与基准")

    # 运行测试
    current_result = await tester.run_extraction_test(FIXED_SEARCH_RESULTS)

    # 显示当前结果
    console.print(f"\n[cyan]当前版本结果:[/cyan]")
    for key, value in current_result.metrics.items():
        console.print(f"  • {key}: {value}")

    # 处理基准
    if update_baseline:
        tester.save_baseline(current_result, "baseline")
        console.print("\n[green]✓ 基准已更新[/green]")
        return

    # 对比基准
    baseline = tester.load_baseline("extraction_test", "baseline")

    if baseline is None:
        console.print("\n[yellow]未找到基准，将当前结果保存为基准[/yellow]")
        console.print("[dim]提示: 使用 --update-baseline 选项手动更新基准[/dim]")
        return

    # 显示对比
    comparison = tester.compare(current_result, baseline)
    tester.display_comparison(comparison)


@cli.command()
def feedback():
    """查看反馈统计"""
    asyncio.run(_show_feedback_stats())


async def _show_feedback_stats():
    """显示反馈统计"""
    from ..feedback.collector import FeedbackCollector

    collector = FeedbackCollector()
    stats = collector.get_feedback_stats(days=30)

    console.print(Panel.fit("📊 [bold cyan]用户反馈统计[/bold cyan]"))

    if stats["total"] == 0:
        console.print("\n[yellow]暂无反馈数据[/yellow]")
        console.print("\n[dim]提示: 用户可以通过对话时给出反馈来帮助Agent进化[/dim]")
        return

    # 显示统计
    console.print(f"\n[cyan]最近30天统计:[/cyan]")
    console.print(f"  总反馈数: [bold]{stats['total']}[/bold]")
    console.print(f"  平均评分: [bold]{stats['avg_rating']:.1f}[/bold]/5 ⭐")
    console.print(f"  有用率: [bold]{stats['useful_rate']*100:.1f}%[/bold]")

    if stats["main_problems"]:
        console.print(f"\n[red]主要问题:[/red]")
        for problem, count in stats["main_problems"]:
            console.print(f"  • {problem}: {count}次")

    # 评级
    avg_rating = stats["avg_rating"]
    if avg_rating >= 4.5:
        grade = "A (优秀)"
        color = "green"
    elif avg_rating >= 4.0:
        grade = "B (良好)"
        color = "blue"
    elif avg_rating >= 3.5:
        grade = "C (及格)"
        color = "yellow"
    else:
        grade = "D (需改进)"
        color = "red"

    console.print(f"\n评级: [{color}]{grade}[/{color}]")


@cli.command()
@click.argument("learning_id")
@click.option("--rating", type=int, required=True, help="评分 1-5")
@click.option("--useful", is_flag=True, help="是否有用")
@click.option("--problem", help="问题描述")
def rate(learning_id: str, rating: int, useful: bool, problem: Optional[str] = None):
    """对知识进行评分"""
    asyncio.run(_submit_feedback(learning_id, rating, useful, problem))


async def _submit_feedback(learning_id: str, rating: int, useful: bool, problem: Optional[str]):
    """提交反馈"""
    from ..feedback.collector import FeedbackCollector, Feedback

    if not 1 <= rating <= 5:
        console.print("[red]评分必须在 1-5 之间[/red]")
        return

    collector = FeedbackCollector()

    feedback = Feedback(
        id=f"{learning_id}_{datetime.now().timestamp()}",
        timestamp=datetime.now().isoformat(),
        learning_id=learning_id,
        rating=rating,
        useful=useful,
        problem=problem,
        user_comment=None
    )

    collector.save_feedback(feedback)

    console.print(f"\n[green]✓ 反馈已提交[/green]")
    console.print(f"  知识ID: {learning_id}")
    console.print(f"  评分: {rating}⭐")
    console.print(f"  有用: {'是' if useful else '否'}")
    if problem:
        console.print(f"  问题: {problem}")


@cli.command()
def evolve():
    """触发进化循环"""
    asyncio.run(_run_evolution())


async def _run_evolution():
    """运行进化循环"""
    from ..evolution.engine import FeedbackDrivenEvolution

    agent = PyAgent()
    await agent.initialize()

    console.print(Panel.fit("🧬 [bold yellow]进化循环[/bold yellow]"))
    console.print("基于用户反馈主动进化\n")

    engine = FeedbackDrivenEvolution(agent)
    result = await engine.run_evolution_cycle()

    # 显示结果
    console.print(f"\n[bold]状态:[/bold] {result.get('status')}")
    console.print(f"[bold]消息:[/bold] {result.get('message')}")

    if "stats" in result:
        stats = result["stats"]
        console.print(f"\n[cyan]当前反馈情况:[/cyan]")
        console.print(f"  总反馈: {stats['total']}")
        console.print(f"  平均评分: {stats['avg_rating']:.1f}/5")
        console.print(f"  有用率: {stats['useful_rate']*100:.1f}%")

    if "actions" in result and result["actions"]:
        console.print(f"\n[green]✓ 进化动作:[/green]")
        for i, action in enumerate(result["actions"], 1):
            console.print(f"  {i}. {action.get('type')} - {action.get('suggestion')}")

    await agent.close()


@cli.command()
def policies():
    """查看当前激活的行为策略"""
    asyncio.run(_show_policies())


async def _show_policies():
    """显示行为策略"""
    from ..skills.application import SkillApplicationEngine

    agent = PyAgent()
    await agent.initialize()

    console.print(Panel.fit("🧠 [bold cyan]行为策略[/bold cyan]"))
    console.print("基于学习到的技能自动生成的行为策略\n")

    engine = SkillApplicationEngine(agent)
    active = engine.get_active_policies()

    console.print(f"[cyan]策略概况:[/cyan]")
    console.print(f"  总策略数: {active['total_policies']}")
    console.print(f"  激活策略: {active['active_policies']}")

    if active['active_policies'] > 0:
        console.print(f"\n[cyan]激活的策略:[/cyan]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("策略", style="green")
        table.add_column("置信度", justify="right")
        table.add_column("最后更新", justify="right")

        for policy_key, policy_info in active['active'].items():
            confidence = policy_info.get('confidence', 0)
            confidence_str = f"{confidence*100:.0f}%"
            last_updated = policy_info.get('last_updated', '未记录')
            if last_updated:
                last_updated = last_updated[:10]  # 只显示日期
            table.add_row(policy_key, confidence_str, last_updated)

        console.print(table)

        console.print(f"\n[dim]提示: 策略会根据学习内容自动激活和调整[/dim]")
    else:
        console.print(f"\n[yellow]暂无激活的策略[/yellow]")
        console.print(f"[dim]提示: 随着学习积累，策略会自动激活[/dim]")

    await agent.close()


def main():
    """CLI入口"""
    cli()


if __name__ == "__main__":
    main()
