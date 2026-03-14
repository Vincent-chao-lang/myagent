"""PyAgent 差异测试框架

用于对比代码修改前后的输出差异，确保改进是正向的
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    timestamp: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    metrics: Dict[str, float]
    errors: List[str]


class DifferentialTester:
    """差异测试器"""

    def __init__(self, baseline_dir: Path = None):
        self.baseline_dir = baseline_dir or Path("./data/baselines")
        self.baseline_dir.mkdir(parents=True, exist_ok=True)

    async def run_extraction_test(self, search_results: List[Dict]) -> TestResult:
        """运行提取测试"""
        from src.core.config import config
        from src.models.factory import create_llm
        from src.learning.extractor import KnowledgeExtractor

        # 初始化
        llm = create_llm(config.model_type, config.model_config)
        extractor = KnowledgeExtractor(llm)

        # 执行提取
        learnings = []
        stage_times = {}

        import time
        start = time.time()

        for result in search_results:
            try:
                learning = await extractor.extract_knowledge(
                    result,
                    extractor._load_prompt_template()
                )
                if learning:
                    learnings.append(learning)
            except Exception as e:
                console.print(f"[red]提取失败: {e}[/red]")

        elapsed = time.time() - start

        # 计算指标
        metrics = {
            "total_learnings": len(learnings),
            "avg_content_length": sum(len(l.get("content", "")) for l in learnings) / max(len(learnings), 1),
            "with_code_example": sum(1 for l in learnings if l.get("code_example")),
            "with_tags": sum(1 for l in learnings if l.get("tags")),
            "execution_time": elapsed,
            "avg_time_per_item": elapsed / max(len(search_results), 1)
        }

        return TestResult(
            test_name="extraction_test",
            timestamp=datetime.now().isoformat(),
            inputs={"search_results_count": len(search_results)},
            outputs={"learnings": learnings},
            metrics=metrics,
            errors=[]
        )

    def save_baseline(self, result: TestResult, version: str = "current"):
        """保存基准结果"""
        baseline_file = self.baseline_dir / f"{result.test_name}_{version}.json"
        with open(baseline_file, "w") as f:
            json.dump({
                "test_name": result.test_name,
                "timestamp": result.timestamp,
                "inputs": result.inputs,
                "outputs": {
                    "learnings": result.outputs["learnings"][:3],  # 只保存前3条
                    "total_count": len(result.outputs["learnings"])
                },
                "metrics": result.metrics,
                "errors": result.errors
            }, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓ 基准已保存: {baseline_file}[/green]")

    def load_baseline(self, test_name: str, version: str = "baseline") -> Dict:
        """加载基准结果"""
        baseline_file = self.baseline_dir / f"{test_name}_{version}.json"
        if baseline_file.exists():
            with open(baseline_file, "r") as f:
                return json.load(f)
        return None

    def compare(self, current: TestResult, baseline: Dict) -> Dict:
        """对比当前结果与基准"""
        comparison = {
            "metrics_delta": {},
            "improvements": [],
            "regressions": [],
            "summary": ""
        }

        baseline_metrics = baseline.get("metrics", {})

        # 对比各项指标
        for key, current_value in current.metrics.items():
            baseline_value = baseline_metrics.get(key, 0)
            delta = current_value - baseline_value
            comparison["metrics_delta"][key] = {
                "baseline": baseline_value,
                "current": current_value,
                "delta": delta,
                "delta_percent": (delta / baseline_value * 100) if baseline_value > 0 else 0
            }

            # 判断好坏（根据指标类型）
            if key in ["total_learnings", "avg_content_length", "with_code_example", "with_tags"]:
                if delta > 0:
                    comparison["improvements"].append(f"{key}: +{delta:.2f}")
                elif delta < 0:
                    comparison["regressions"].append(f"{key}: {delta:.2f}")
            elif key in ["execution_time", "avg_time_per_item"]:
                if delta < 0:
                    comparison["improvements"].append(f"{key}: {delta:.2f}s (更快)")
                elif delta > 0:
                    comparison["regressions"].append(f"{key}: +{delta:.2f}s (更慢)")

        # 生成总结
        if not comparison["regressions"]:
            comparison["summary"] = "✅ 所有指标都有改善或保持稳定"
        else:
            comparison["summary"] = f"⚠️  发现 {len(comparison['regressions'])} 项退化"

        return comparison

    def display_comparison(self, comparison: Dict):
        """显示对比结果"""
        console.print("\n")
        console.print(Panel.fit("📊 差异测试报告"))

        # 指标对比表
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan")
        table.add_column("基准值", justify="right")
        table.add_column("当前值", justify="right")
        table.add_column("变化", justify="right")
        table.add_column("变化%", justify="right")

        for key, delta_info in comparison["metrics_delta"].items():
            baseline_val = delta_info["baseline"]
            current_val = delta_info["current"]
            delta = delta_info["delta"]
            delta_pct = delta_info["delta_percent"]

            # 格式化值
            if isinstance(current_val, float):
                baseline_str = f"{baseline_val:.2f}"
                current_str = f"{current_val:.2f}"
                delta_str = f"{delta:+.2f}"
                delta_pct_str = f"{delta_pct:+.1f}%"
            else:
                baseline_str = str(baseline_val)
                current_str = str(current_val)
                delta_str = str(delta)
                delta_pct_str = "-"

            # 颜色
            delta_color = "green" if (delta > 0 and "time" not in key) or (delta < 0 and "time" in key) else "red"

            table.add_row(
                key,
                baseline_str,
                current_str,
                f"[{delta_color}]{delta_str}[/{delta_color}]",
                delta_pct_str if delta_pct_str != "-" else ""
            )

        console.print(table)

        # 改进和退化
        if comparison["improvements"]:
            console.print("\n[green]✅ 改进:[/green]")
            for imp in comparison["improvements"]:
                console.print(f"   • {imp}")

        if comparison["regressions"]:
            console.print("\n[red]❌ 退化:[/red]")
            for reg in comparison["regressions"]:
                console.print(f"   • {reg}")

        # 总结
        console.print(f"\n{comparison['summary']}")


async def run_differential_test():
    """运行完整的差异测试"""
    from tests.fixtures.learning_fixtures import FIXED_SEARCH_RESULTS

    tester = DifferentialTester()

    console.print(Panel.fit("🧪 开始差异测试"))

    # 1. 运行当前版本
    console.print("\n[yellow]步骤 1: 运行当前版本测试...[/yellow]")
    current_result = await tester.run_extraction_test(FIXED_SEARCH_RESULTS)

    # 显示当前结果
    console.print(f"\n[cyan]当前版本结果:[/cyan]")
    console.print(f"  • 提取数量: {current_result.metrics['total_learnings']}")
    console.print(f"  • 平均内容长度: {current_result.metrics['avg_content_length']:.0f}")
    console.print(f"  • 带代码示例: {current_result.metrics['with_code_example']}")
    console.print(f"  • 带标签: {current_result.metrics['with_tags']}")
    console.print(f"  • 执行时间: {current_result.metrics['execution_time']:.2f}s")

    # 2. 加载基准
    console.print("\n[yellow]步骤 2: 加载基准结果...[/yellow]")
    baseline = tester.load_baseline("extraction_test", "baseline")

    if baseline is None:
        console.print("\n[yellow]未找到基准，将当前结果保存为基准[/yellow]")
        tester.save_baseline(current_result, "baseline")
        console.print("\n[green]✓ 基准已建立，下次运行将进行对比[/green]")
        return

    # 3. 对比
    console.print("\n[yellow]步骤 3: 对比基准与当前...[/yellow]")
    comparison = tester.compare(current_result, baseline)
    tester.display_comparison(comparison)

    # 4. 询问是否更新基准
    if comparison["improvements"] and not comparison["regressions"]:
        console.print("\n[cyan]是否将当前结果保存为新基准？[y/N][/cyan]")
        # 这里可以添加交互逻辑
        tester.save_baseline(current_result, "baseline")


if __name__ == "__main__":
    asyncio.run(run_differential_test())
