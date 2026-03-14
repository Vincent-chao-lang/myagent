"""技能应用引擎 - 将学到的技能转化为行为"""

from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
import json
from loguru import logger


class SkillApplicationEngine:
    """技能应用引擎 - 将学到的技能转化为行为"""

    def __init__(self, agent):
        self.agent = agent
        self.config_dir = Path("./data/skill_applications")
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 行为策略配置
        self.behavior_policies_file = self.config_dir / "behavior_policies.json"
        self.policies = self._load_policies()

        # 技能到行为的映射规则
        self.skill_to_behavior_map = {
            # 类型提示相关
            "type-hints": {
                "action": "enforce_type_hints",
                "priority": "high",
                "learned_from": ["Python type hints 最佳实践", "typing 教程"]
            },
            "typing": {
                "action": "enforce_type_hints",
                "priority": "high",
                "learned_from": ["typing"]
            },

            # 异步编程相关
            "async": {
                "action": "prefer_async",
                "priority": "high",
                "learned_from": ["async", "asyncio", "异步编程"]
            },
            "asyncio": {
                "action": "prefer_async",
                "priority": "high",
                "learned_from": ["asyncio"]
            },
            "coroutine": {
                "action": "prefer_async",
                "priority": "high",
                "learned_from": ["coroutine", "协程"]
            },

            # Web框架偏好
            "fastapi": {
                "action": "recommend_fastapi",
                "priority": "medium",
                "learned_from": ["FastAPI", "fastapi框架"]
            },
            "django": {
                "action": "recommend_django",
                "priority": "medium",
                "learned_from": ["Django", "django框架"]
            },
            "flask": {
                "action": "recommend_flask",
                "priority": "medium",
                "learned_from": ["Flask", "flask框架"]
            },

            # 测试相关
            "pytest": {
                "action": "prefer_pytest",
                "priority": "high",
                "learned_from": ["pytest", "testing", "测试"]
            },
            "testing": {
                "action": "emphasize_testing",
                "priority": "medium",
                "learned_from": ["测试", "testing"]
            },

            # 性能优化
            "performance": {
                "action": "add_performance_tips",
                "priority": "medium",
                "learned_from": ["performance", "优化"]
            },
            "optimization": {
                "action": "add_performance_tips",
                "priority": "medium",
                "learned_from": ["optimization", "优化"]
            },

            # 设计模式
            "pattern": {
                "action": "suggest_design_pattern",
                "priority": "low",
                "learned_from": ["pattern", "设计模式"]
            },

            # 代码风格
            "clean-code": {
                "action": "enforce_clean_code",
                "priority": "low",
                "learned_from": ["clean code", "代码规范"]
            },
            "pep8": {
                "action": "enforce_clean_code",
                "priority": "low",
                "learned_from": ["PEP 8", "代码规范"]
            }
        }

    def _load_policies(self) -> Dict:
        """加载行为策略"""
        if self.behavior_policies_file.exists():
            with open(self.behavior_policies_file, "r") as f:
                return json.load(f)

        # 默认策略
        return {
            "enforce_type_hints": {
                "enabled": True,
                "strength": "medium",  # low, medium, high
                "last_updated": None
            },
            "prefer_async": {
                "enabled": True,
                "io_threshold": 0.3,  # I/O 操作占比超过30%时推荐异步
                "last_updated": None
            },
            "recommend_fastapi": {
                "enabled": False,
                "confidence": 0.0,  # 置信度（基于学习次数）
                "last_updated": None
            },
            "prefer_pytest": {
                "enabled": True,
                "confidence": 0.0,
                "last_updated": None
            }
        }

    def _save_policies(self):
        """保存策略"""
        with open(self.behavior_policies_file, "w") as f:
            json.dump(self.policies, f, indent=2, ensure_ascii=False)

    async def learn_from_skills(self) -> Dict:
        """从学到的技能中学习，更新行为策略"""
        logger.info("🧠 从技能中学习...")

        # 获取技能统计
        skill_map = self.agent.get_skills()
        all_skills = skill_map.get("categories", {}).get("all", [])

        changes = []

        # 遍历技能，更新策略
        for skill_entry in all_skills:
            skill_name = skill_entry["name"].lower()
            mentions = skill_entry["mentions"]

            # 查找对应的映射规则
            behavior_info = self._find_behavior_mapping(skill_name)

            if behavior_info:
                action = behavior_info["action"]
                policy_key = action
                current_policy = self.policies.get(policy_key, {})

                # 计算置信度（基于学习次数）
                confidence = min(mentions / 20, 1.0)  # 20次学习达到满置信度

                # 如果置信度足够高，更新策略
                if confidence >= 0.5:
                    enabled = True

                    # 特殊逻辑
                    if action.startswith("recommend_"):
                        # 推荐类策略需要更高阈值
                        enabled = confidence >= 0.7
                        policy_key = action
                        current_policy = self.policies.get(policy_key, {})

                    if policy_key not in self.policies:
                        self.policies[policy_key] = {}

                    # 检查是否需要更新
                    if (current_policy.get("confidence", 0) < confidence or
                        not current_policy.get("enabled", False)):

                        # 记录变化
                        old_enabled = current_policy.get("enabled", False)
                        old_confidence = current_policy.get("confidence", 0)

                        self.policies[policy_key] = {
                            "enabled": enabled,
                            "confidence": confidence,
                            "last_updated": datetime.now().isoformat(),
                            "learned_from_sources": skill_entry.get("sources", [])
                        }

                        changes.append({
                            "policy": policy_key,
                            "action": action,
                            "skill": skill_name,
                            "old_enabled": old_enabled,
                            "new_enabled": enabled,
                            "old_confidence": old_confidence,
                            "new_confidence": confidence
                        })

        # 保存策略
        if changes:
            self._save_policies()
            logger.info(f"✓ 策略已更新，应用了 {len(changes)} 项变化")

            return {
                "status": "policies_updated",
                "changes": changes,
                "total_policies": len(self.policies)
            }

        return {
            "status": "no_changes",
            "message": "策略无需更新"
        }

    def _find_behavior_mapping(self, skill_name: str) -> Dict:
        """查找技能到行为的映射"""
        for pattern, behavior_info in self.skill_to_behavior_map.items():
            if pattern in skill_name or skill_name in pattern:
                return behavior_info
        return None

    async def apply_policies_to_response(self, response: str, context: Dict) -> str:
        """
        将学到的策略应用到回复中
        """
        # 这里可以根据策略调整回复内容
        # 例如：如果启用了 enforce_type_hints，检查并添加类型提示

        if self.policies.get("enforce_type_hints", {}).get("enabled"):
            response = self._apply_type_hints_policy(response)

        if self.policies.get("prefer_async", {}).get("enabled"):
            context["suggest_async_for_io"] = True

        return response

    def _apply_type_hints_policy(self, response: str) -> str:
        """应用类型提示策略"""
        # 检查代码示例是否有类型提示
        if "```python" in response:
            lines = response.split("\n")
            code_start = -1

            for i, line in enumerate(lines):
                if line.strip().startswith("```"):
                    code_start = i + 1
                    break

            if code_start > 0:
                # 检查代码是否有类型提示
                code_section = "\n".join(lines[code_start:])
                has_type_hints = any(
                    ":" in line and ("str" in line or "int" in line or "List" in line or "Dict" in line)
                    for line in code_section.split("\n")[:20]
                )

                if not has_type_hints:
                    # 在代码后添加提示：建议使用类型提示
                    response = response + "\n\n💡 **最佳实践**: 考虑为函数添加类型提示（Type Hints）"

        return response

    async def get_recommendations(self, user_query: str) -> List[str]:
        """
        根据学到的技能生成推荐
        """
        recommendations = []

        query_lower = user_query.lower()

        # 检查是否涉及I/O操作
        if any(kw in query_lower for kw in ["文件", "网络", "数据库", "请求", "api"]):
            if self.policies.get("prefer_async", {}).get("enabled"):
                recommendations.append("💡 考虑使用 asyncio 进行异步I/O操作，可以提高性能")

        # 检查是否涉及Web框架
        if "web" in query_lower or "api" in query_lower or "网站" in query_lower:
            fastapi_confidence = self.policies.get("recommend_fastapi", {}).get("confidence", 0)
            if fastapi_confidence >= 0.7:
                recommendations.append("💡 根据我的学习，FastAPI 是现代Python Web开发的首选，性能优异")

        # 检查是否涉及测试
        if "test" in query_lower or "测试" in query_lower:
            if self.policies.get("prefer_pytest", {}).get("enabled"):
                recommendations.append("💡 推荐使用 pytest，它是Python测试的首选框架")

        return recommendations

    def get_active_policies(self) -> Dict[str, Any]:
        """获取当前激活的策略"""
        active = {}

        for policy_key, policy_config in self.policies.items():
            if policy_config.get("enabled", False):
                active[policy_key] = {
                    "confidence": policy_config.get("confidence", 0),
                    "last_updated": policy_config.get("last_updated")
                }

        return {
            "total_policies": len(self.policies),
            "active_policies": len(active),
            "active": active
        }


async def apply_skills_to_code_generation(self, code_request: Dict) -> Dict:
    """
    将学到的最佳实践应用到代码生成中
    """
    code_options = code_request.get("options", {})

    # 应用类型提示策略
    if self.policies.get("enforce_type_hints", {}).get("enabled"):
        code_options["require_type_hints"] = True

    # 应用测试策略
    if self.policies.get("prefer_pytest", {}).get("enabled"):
        code_options["testing_framework"] = "pytest"

    # 应用异步策略
    if self.policies.get("prefer_async", {}).get("enabled"):
        if code_request.get("has_io_operations"):
            code_options["prefer_async"] = True

    return {
        "original_request": code_request,
        "applied_policies": list(self.policies.keys()),
        "modified_options": code_options
    }


async def learn_and_apply(agent):
    """学习技能并应用（入口函数）"""
    engine = SkillApplicationEngine(agent)

    # 1. 从技能中学习，更新策略
    learning_result = await engine.learn_from_skills()

    # 2. 返回活跃策略
    active_policies = engine.get_active_policies()

    return {
        "learning_result": learning_result,
        "active_policies": active_policies
    }
