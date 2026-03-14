"""基于反馈的进化引擎 - 简化版"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger


class FeedbackDrivenEvolution:
    """基于反馈的进化引擎"""

    def __init__(self, agent, feedback_dir: Path = None):
        self.agent = agent
        self.feedback_dir = feedback_dir or Path("./data/evolution")
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件
        self.config_file = self.feedback_dir / "evolution_config.json"
        self.history_file = self.feedback_dir / "evolution_history.json"

        # 加载配置
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载进化配置"""
        if self.config_file.exists():
            import json
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {
            "learning_prompt_style": "balanced",
            "extraction_threshold": 50,
            "code_requirement": "optional",
            "last_adjustment": None
        }

    def _save_config(self):
        """保存配置"""
        import json
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    async def analyze_feedback(self) -> Dict:
        """分析用户反馈，决定是否需要进化"""
        from ..feedback.collector import FeedbackCollector

        collector = FeedbackCollector()
        stats = collector.get_feedback_stats(days=7)

        logger.info(f"📊 反馈统计 (7天):")
        logger.info(f"  总反馈数: {stats['total']}")
        logger.info(f"  平均评分: {stats['avg_rating']:.1f}/5")
        logger.info(f"  有用率: {stats['useful_rate']*100:.1f}%")

        if stats["main_problems"]:
            logger.info(f"  主要问题:")
            for problem, count in stats["main_problems"][:3]:
                logger.info(f"    - {problem}: {count}次")

        # 决定是否需要进化
        needs_evolution = False
        actions = []

        # 条件1: 评分低
        if stats["avg_rating"] < 3.5 and stats["total"] >= 10:
            needs_evolution = True
            actions.append({
                "type": "improve_quality",
                "reason": f"平均评分 {stats['avg_rating']:.1f} 低于 3.5",
                "suggestion": "调整提示词，提高内容质量"
            })

        # 条件2: 有用率低
        if stats["useful_rate"] < 0.6 and stats["total"] >= 10:
            needs_evolution = True
            actions.append({
                "type": "adjust_focus",
                "reason": f"有用率 {stats['useful_rate']*100:.1f}% 低于 60%",
                "suggestion": "调整知识筛选标准"
            })

        # 条件3: 特定问题突出
        if stats["main_problems"]:
            top_problem, count = stats["main_problems"][0]
            if count >= 3:  # 同一问题出现3次以上
                needs_evolution = True
                actions.append({
                    "type": "address_issue",
                    "problem": top_problem,
                    "reason": f"'{top_problem}' 问题出现 {count} 次",
                    "suggestion": self._get_fix_suggestion(top_problem)
                })

        return {
            "needs_evolution": needs_evolution,
            "stats": stats,
            "actions": actions
        }

    def _get_fix_suggestion(self, problem: str) -> str:
        """根据问题类型获取修复建议"""
        suggestions = {
            "内容太简略": "提高最小内容长度阈值",
            "没有代码": "将代码要求改为必需",
            "不相关": "提高检索准确性，调整学习源",
            "信息错误": "增加事实核查步骤",
            "太复杂": "简化解释，增加示例",
            "代码太少": "强调代码示例提取",
            "提取重复": "增加去重逻辑"
        }
        return suggestions.get(problem, "需要调整提取策略")

    async def evolve(self, action: Dict) -> bool:
        """执行进化动作"""
        action_type = action["type"]

        logger.info(f"🧬 开始进化: {action_type}")
        logger.info(f"   原因: {action['reason']}")
        logger.info(f"   建议: {action['suggestion']}")

        try:
            if action_type == "improve_quality":
                return await self._improve_quality(action)
            elif action_type == "adjust_focus":
                return await self._adjust_focus(action)
            elif action_type == "address_issue":
                return await self._address_issue(action)
            else:
                logger.warning(f"未知的动作类型: {action_type}")
                return False
        except Exception as e:
            logger.error(f"进化失败: {e}")
            return False

    async def _improve_quality(self, action: Dict) -> bool:
        """提高质量"""
        # 调整提示词风格
        styles = {
            "balanced": "balanced",
            "detailed": "detailed",
            "concise": "concise",
            "practical": "practical"
        }

        current_style = self.config.get("learning_prompt_style", "balanced")

        # 循环切换风格
        style_list = list(styles.keys())
        current_index = style_list.index(current_style)
        new_style = style_list[(current_index + 1) % len(style_list)]

        self.config["learning_prompt_style"] = new_style
        self._save_config()

        logger.info(f"✓ 提示词风格已调整: {current_style} → {new_style}")
        return True

    async def _adjust_focus(self, action: Dict) -> bool:
        """调整关注点"""
        # 调整阈值
        current_threshold = self.config.get("extraction_threshold", 50)

        if current_threshold > 30:
            new_threshold = current_threshold - 10
        else:
            new_threshold = current_threshold

        self.config["extraction_threshold"] = new_threshold
        self._save_config()

        logger.info(f"✓ 提取阈值已调整: {current_threshold} → {new_threshold}")
        return True

    async def _address_issue(self, action: Dict) -> bool:
        """解决特定问题"""
        problem = action["problem"]
        suggestion = action["suggestion"]

        # 根据问题调整配置
        if "代码" in problem:
            self.config["code_requirement"] = "required"
        elif "简略" in problem or "太短" in problem:
            self.config["extraction_threshold"] = self.config.get("extraction_threshold", 50) + 20
        elif "重复" in problem:
            self.config["deduplication_enabled"] = True

        self._save_config()
        logger.info(f"✓ 已应用修复: {suggestion}")
        return True

    def _save_history(self, evolution_record: Dict):
        """保存进化历史"""
        history = []

        if self.history_file.exists():
            import json
            with open(self.history_file, "r") as f:
                history = json.load(f)

        history.append({
            "timestamp": datetime.now().isoformat(),
            **evolution_record
        })

        # 只保留最近20条
        history = history[-20:]

        import json
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    async def run_evolution_cycle(self) -> Dict:
        """运行完整的进化循环"""
        logger.info("🔄 开始进化循环...")

        # 1. 分析反馈
        analysis = await self.analyze_feedback()

        if not analysis["needs_evolution"]:
            return {
                "status": "no_evolution_needed",
                "message": "反馈良好，无需进化",
                "stats": analysis["stats"]
            }

        # 2. 执行进化
        successful_evolutions = []

        for action in analysis["actions"]:
            success = await self.evolve(action)
            if success:
                successful_evolutions.append(action)

        # 3. 记录历史
        self._save_history({
            "trigger_stats": analysis["stats"],
            "actions_taken": len(successful_evolutions),
            "actions": successful_evolutions
        })

        return {
            "status": "evolution_complete",
            "message": f"进化完成，应用了 {len(successful_evolutions)} 项改进",
            "actions": successful_evolutions,
            "stats": analysis["stats"]
        }


async def run_evolution(agent):
    """运行进化（入口函数）"""
    engine = FeedbackDrivenEvolution(agent)
    return await engine.run_evolution_cycle()
