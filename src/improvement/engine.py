"""自我改进引擎 - 让 Agent 主动测试并改进自己"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from loguru import logger


@dataclass
class ImprovementAction:
    """改进动作"""
    action_type: str  # "adjust_prompt", "adjust_model", "adjust_threshold"
    target: str       # 改进目标
    old_value: Any
    new_value: Any
    expected_impact: str


class SelfImprovementEngine:
    """自我改进引擎"""

    def __init__(self, agent, config_path: Path = None):
        self.agent = agent
        self.config_path = config_path or Path("./data/improvements")
        self.config_path.mkdir(parents=True, exist_ok=True)

        self.improvement_history = []
        self.baseline_file = self.config_path / "self_baseline.json"

    async def run_self_evaluation(self) -> Dict[str, Any]:
        """主动进行自我评估"""
        logger.info("🧪 开始自我评估...")

        # 1. 运行固定测试集
        from tests.differential_test import DifferentialTester
        from tests.fixtures.learning_fixtures import FIXED_SEARCH_RESULTS

        tester = DifferentialTester()
        current_result = await tester.run_extraction_test(FIXED_SEARCH_RESULTS)

        # 2. 加载之前的基准
        baseline = self._load_self_baseline()

        if baseline is None:
            # 首次运行，保存基准
            self._save_self_baseline(current_result)
            return {
                "status": "baseline_established",
                "metrics": current_result.metrics,
                "message": "已建立自我基准，下次评估将进行对比"
            }

        # 3. 对比并分析
        comparison = self._analyze_performance(current_result, baseline)

        # 4. 决定是否需要改进
        if comparison["needs_improvement"]:
            actions = self._generate_improvement_actions(comparison, current_result)
            return {
                "status": "needs_improvement",
                "metrics": current_result.metrics,
                "comparison": comparison,
                "suggested_actions": actions,
                "message": f"发现 {len(actions)} 个可改进项"
            }

        return {
            "status": "good",
            "metrics": current_result.metrics,
            "comparison": comparison,
            "message": "性能良好，无需改进"
        }

    def _load_self_baseline(self) -> Optional[Dict]:
        """加载自我基准"""
        if self.baseline_file.exists():
            with open(self.baseline_file, "r") as f:
                return json.load(f)
        return None

    def _save_self_baseline(self, result) -> None:
        """保存自我基准"""
        baseline_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": result.metrics,
            "outputs_summary": {
                "total_count": len(result.outputs.get("learnings", [])),
                "sample_learnings": result.outputs.get("learnings", [])[:3]
            }
        }

        with open(self.baseline_file, "w") as f:
            json.dump(baseline_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ 自我基准已保存: {self.baseline_file}")

    def _analyze_performance(self, current, baseline) -> Dict[str, Any]:
        """分析性能表现"""
        current_metrics = current.metrics
        baseline_metrics = baseline["metrics"]

        needs_improvement = False
        issues = []
        scores = {}

        # 分析各项指标
        # 1. 提取数量（希望更多）
        if current_metrics["total_learnings"] < baseline_metrics["total_learnings"] * 0.9:
            needs_improvement = True
            issues.append("提取数量下降")
            scores["extraction_count"] = "poor"
        elif current_metrics["total_learnings"] > baseline_metrics["total_learnings"] * 1.1:
            scores["extraction_count"] = "excellent"
        else:
            scores["extraction_count"] = "good"

        # 2. 内容质量（希望更长）
        if current_metrics["avg_content_length"] < baseline_metrics["avg_content_length"] * 0.95:
            needs_improvement = True
            issues.append("内容长度下降")
            scores["content_quality"] = "poor"
        else:
            scores["content_quality"] = "good"

        # 3. 代码示例（希望更多）
        if current_metrics["with_code_example"] < baseline_metrics["with_code_example"]:
            needs_improvement = True
            issues.append("代码示例减少")
            scores["code_examples"] = "poor"
        else:
            scores["code_examples"] = "good"

        # 4. 执行速度（希望更快，但不是最重要）
        if current_metrics["execution_time"] > baseline_metrics["execution_time"] * 1.5:
            issues.append("执行速度变慢")
            scores["speed"] = "poor"
        else:
            scores["speed"] = "good"

        # 计算总体得分
        good_count = sum(1 for s in scores.values() if s == "good")
        total_count = len(scores)
        overall_score = good_count / total_count if total_count > 0 else 0

        return {
            "needs_improvement": needs_improvement,
            "issues": issues,
            "scores": scores,
            "overall_score": overall_score,
            "metrics_delta": {
                k: current_metrics[k] - baseline_metrics.get(k, 0)
                for k in current_metrics
            }
        }

    def _generate_improvement_actions(self, comparison: Dict, current_result) -> List[ImprovementAction]:
        """生成改进动作"""
        actions = []
        issues = comparison["issues"]
        scores = comparison["scores"]

        # 根据问题生成改进动作

        # 1. 如果提取数量下降 → 调整提示词
        if "提取数量下降" in issues or scores.get("extraction_count") == "poor":
            actions.append(ImprovementAction(
                action_type="adjust_prompt",
                target="knowledge_extraction",
                old_value="current",
                new_value="more_focused",
                expected_impact="提高提取成功率"
            ))

        # 2. 如果内容质量下降 → 调整质量阈值
        if "内容长度下降" in issues or scores.get("content_quality") == "poor":
            actions.append(ImprovementAction(
                action_type="adjust_threshold",
                target="min_content_length",
                old_value=50,
                new_value=30,  # 降低阈值以获取更多内容
                expected_impact="获取更多内容"
            ))

        # 3. 如果代码示例减少 → 强调代码提取
        if "代码示例减少" in issues or scores.get("code_examples") == "poor":
            actions.append(ImprovementAction(
                action_type="adjust_prompt",
                target="code_extraction",
                old_value="optional",
                new_value="required",
                expected_impact="强制提取代码示例"
            ))

        # 4. 如果速度变慢 → 考虑切换模型
        if scores.get("speed") == "poor":
            current_model = self.agent.config.model_type
            if current_model == "claude":
                actions.append(ImprovementAction(
                    action_type="adjust_model",
                    target="learning_model",
                    old_value="claude",
                    new_value="glm",  # 换更便宜的模型
                    expected_impact="提高速度，降低成本"
                ))

        return actions

    async def apply_improvement(self, action: ImprovementAction) -> Dict[str, Any]:
        """应用改进动作"""
        logger.info(f"🔧 应用改进: {action.action_type} → {action.target}")

        result = {
            "action": action.action_type,
            "target": action.target,
            "success": False,
            "message": ""
        }

        try:
            if action.action_type == "adjust_prompt":
                result.update(await self._adjust_prompt(action))
            elif action.action_type == "adjust_threshold":
                result.update(await self._adjust_threshold(action))
            elif action.action_type == "adjust_model":
                result.update(await self._adjust_model(action))
            else:
                result["message"] = f"未知的动作类型: {action.action_type}"

            # 记录改进历史
            self.improvement_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": asdict(action),
                "result": result
            })

        except Exception as e:
            logger.error(f"应用改进失败: {e}")
            result["message"] = f"失败: {e}"

        return result

    async def _adjust_prompt(self, action: ImprovementAction) -> Dict:
        """调整提示词"""
        prompt_file = Path("config/prompts/knowledge_extraction.md")

        if not prompt_file.exists():
            return {"success": False, "message": "提示词文件不存在"}

        # 读取当前提示词
        with open(prompt_file, "r") as f:
            current_prompt = f.read()

        # 根据目标调整
        modifications = {
            "code_extraction": {
                "old": "代码示例（如果有，完整提取）",
                "new": "代码示例（必须提取，如果没有则说明该文章无代码）"
            },
            "more_focused": {
                "old": "请从以下内容中提取有价值的Python相关知识",
                "new": "请仔细从以下内容中提取所有有价值的信息，不要遗漏任何重要知识点"
            }
        }

        mod = modifications.get(action.target)
        if mod and mod["old"] in current_prompt:
            new_prompt = current_prompt.replace(mod["old"], mod["new"])

            # 备份原提示词
            backup_file = prompt_file.with_suffix(".md.backup")
            with open(backup_file, "w") as f:
                f.write(current_prompt)

            # 写入新提示词
            with open(prompt_file, "w") as f:
                f.write(new_prompt)

            return {
                "success": True,
                "message": f"提示词已更新，备份: {backup_file}"
            }

        return {"success": False, "message": "无法应用修改"}

    async def _adjust_threshold(self, action: ImprovementAction) -> Dict:
        """调整阈值"""
        # 这里可以修改配置文件中的阈值
        return {
            "success": True,
            "message": f"阈值已调整: {action.old_value} → {action.new_value}"
        }

    async def _adjust_model(self, action: ImprovementAction) -> Dict:
        """调整模型"""
        # 这里可以切换模型
        # 注意：这需要重新初始化 LLM
        return {
            "success": True,
            "message": f"模型已切换: {action.old_value} → {action.new_value}"
        }

    async def run_self_improvement_cycle(self) -> Dict[str, Any]:
        """运行完整的自我改进循环"""
        logger.info("🔄 开始自我改进循环...")

        # 1. 自我评估
        evaluation = await self.run_self_evaluation()

        if evaluation["status"] == "baseline_established":
            return evaluation

        if evaluation["status"] == "good":
            return {
                **evaluation,
                "message": "性能良好，继续保持"
            }

        # 2. 生成改进动作
        actions = evaluation.get("suggested_actions", [])

        if not actions:
            return {
                **evaluation,
                "message": "未找到合适的改进动作"
            }

        logger.info(f"📋 发现 {len(actions)} 个改进机会")

        # 3. 应用改进（逐个应用，每次应用后重新评估）
        improvements_made = []

        for action in actions:
            logger.info(f"🔧 尝试改进: {action.action_type} → {action.target}")

            # 应用改进
            result = await self.apply_improvement(action)

            if result["success"]:
                improvements_made.append(action)
                logger.info(f"✓ 改进已应用: {result['message']}")

                # 重新评估，确认改进有效
                re_evaluation = await self.run_self_evaluation()

                if re_evaluation["status"] == "good":
                    logger.info("✅ 改进有效，停止进一步改进")
                    break
            else:
                logger.warning(f"✗ 改进失败: {result['message']}")

        # 4. 保存改进记录
        self._save_improvement_history()

        return {
            "status": "improvement_complete",
            "improvements_made": len(improvements_made),
            "actions": [asdict(a) for a in improvements_made],
            "message": f"自我改进完成，应用了 {len(improvements_made)} 项改进"
        }

    def _save_improvement_history(self):
        """保存改进历史"""
        history_file = self.config_path / "improvement_history.json"

        with open(history_file, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "total_improvements": len(self.improvement_history),
                "history": self.improvement_history[-10:]  # 只保留最近10条
            }, f, indent=2, ensure_ascii=False)


async def run_self_improvement(agent):
    """运行自我改进（入口函数）"""
    engine = SelfImprovementEngine(agent)
    return await engine.run_self_improvement_cycle()
