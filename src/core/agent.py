"""Agent主类"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import loguru

from .config import config, Config
from ..models.factory import create_llm
from ..knowledge.hybrid_store import HybridKnowledgeStore
from ..learning.engine import LearningEngine
from ..daily.report import DailyReportGenerator
from ..daily.skills import SkillTracker


class PyAgent:
    """自进化Python专家Agent主类"""

    def __init__(self, config_obj: Optional['Config'] = None):
        """
        初始化Agent

        Args:
            config_obj: 配置对象，默认使用全局配置
        """
        self.config = config_obj or config

        # 初始化LLM
        self.llm = create_llm(
            self.config.model_type,
            self.config.model_config
        )

        # 初始化知识库（支持禁用向量库）
        self.knowledge = HybridKnowledgeStore(
            file_store_path=self.config.file_store_path,
            vector_db_path=self.config.vector_db_path,
            embedding_model=self.config.embedding_model,
            use_vector_db=self.config.use_vector_db,
            offline_mode=self.config.offline_mode,
            cache_dir=self.config.embedding_cache_dir
        )

        # 初始化学习引擎
        self.learner = LearningEngine(
            llm=self.llm,
            knowledge_store=self.knowledge,
            config=self.config
        )

        # 初始化日报生成器
        self.reporter = DailyReportGenerator(
            knowledge_store=self.knowledge,
            skill_tracker=self.knowledge.skill_tracker,
            config=self.config
        )

        # 初始化技能追踪器
        self.skill_tracker = self.knowledge.skill_tracker

        self.logger = loguru.logger
        self._setup_logger()

    def _setup_logger(self):
        """设置日志"""
        log_dir = Path("./data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        self.logger.add(
            log_dir / "agent.log",
            rotation="1 day",
            retention="30 days"
        )

    async def initialize(self):
        """初始化Agent"""
        self.logger.info(f"初始化 {self.config.agent_name} v{self.config.agent_version}")

        # 创建必要目录
        self._create_directories()

        # 初始化知识库
        await self.knowledge.initialize()

        self.logger.info("Agent初始化完成")

    def _create_directories(self):
        """创建必要目录"""
        directories = [
            self.config.file_store_path,
            self.config.vector_db_path,
            self.config.report_path,
            Path("./data/logs"),
            Path("./data/knowledge/patterns"),
            Path("./data/knowledge/architectures"),
            Path("./data/knowledge/best_practices"),
            Path("./data/knowledge/python_features"),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    async def chat(self, user_input: str, context: Optional[List[Dict]] = None) -> str:
        """
        主对话接口

        Args:
            user_input: 用户输入
            context: 对话上下文

        Returns:
            Agent回复
        """
        self.logger.info(f"用户输入: {user_input[:100]}...")

        # 1. 检索相关知识
        relevant_knowledge = await self.knowledge.search(user_input, top_k=5)

        # 2. 构建消息
        system_prompt = self._load_system_prompt()

        messages = [{"role": "system", "content": system_prompt}]

        # 添加相关知识到系统提示
        if relevant_knowledge:
            knowledge_context = "\n\n".join([
                f"- {k.get('title', '')}: {k.get('content', '')[:200]}..."
                for k in relevant_knowledge
            ])
            messages[0]["content"] += f"\n\n相关知识:\n{knowledge_context}"

        # 添加历史上下文
        if context:
            messages.extend(context[-4:])  # 保留最近4轮对话

        # 添加当前输入
        messages.append({"role": "user", "content": user_input})

        # 3. 调用LLM
        try:
            response = await self.llm.achat(messages)
            self.logger.info(f"生成回复: {len(response)} 字符")

            # 4. 应用学到的技能来改进回复
            response = await self._apply_learned_skills(response, user_input)

            return response
        except Exception as e:
            self.logger.error(f"生成回复失败: {e}")
            return "抱歉，我遇到了一些问题，请稍后再试。"

    async def _apply_learned_skills(self, response: str, user_input: str) -> str:
        """应用学到的技能来改进回复"""
        try:
            from ..skills.application import SkillApplicationEngine
            skill_engine = SkillApplicationEngine(self)

            # 获取基于技能的推荐
            recommendations = await skill_engine.get_recommendations(user_input)

            if recommendations:
                # 将推荐添加到回复末尾
                rec_text = "\n\n" + "\n".join(recommendations)
                response += rec_text

            return response
        except Exception as e:
            self.logger.debug(f"技能应用失败: {e}")
            return response

    def _load_system_prompt(self) -> str:
        """加载系统提示词"""
        prompt_path = Path(__file__).parent.parent.parent / "config" / "prompts" / "system.md"

        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()

        return "你是一个Python专家，帮助用户解决Python相关问题。"

    async def daily_learning(self) -> Dict[str, Any]:
        """
        每日学习流程

        Returns:
            学习结果统计（包含时长）
        """
        self.logger.info("开始每日学习流程")

        try:
            # 调用学习引擎的learn方法，返回包含时长的统计信息
            learning_result = await self.learner.learn()

            # 提取学习内容和统计信息
            learnings = learning_result.get("learnings", [])
            learning_stats = {
                "stage_times": learning_result.get("stage_times", {}),
                "total_time": learning_result.get("total_time", 0),
                "start_time": learning_result.get("start_time", ""),
                "end_time": learning_result.get("end_time", "")
            }

            # 限制学习条目数量
            learnings = learnings[:self.config.max_daily_learnings]

            self.logger.info(f"提取了 {len(learnings)} 条知识")

            # 1. 更新知识库
            added_count = 0
            for learning in learnings:
                try:
                    await self.knowledge.add(
                        content=learning.get("content", ""),
                        metadata={
                            "title": learning.get("title", ""),
                            "category": learning.get("category", ""),
                            "tags": learning.get("tags", []),
                            "source": learning.get("source", ""),
                            "date": datetime.now().isoformat(),
                            "importance": learning.get("importance", 3)
                        }
                    )
                    added_count += 1
                except Exception as e:
                    self.logger.error(f"添加知识失败: {e}")

            # 2. 更新技能
            self.skill_tracker.update_from_learnings(learnings)

            # 2.1 将技能转化为行为（关键！）
            try:
                from ..skills.application import SkillApplicationEngine
                skill_engine = SkillApplicationEngine(self)

                self.logger.info("🧠 将学到的技能转化为行为...")
                skill_result = await skill_engine.learn_and_apply(self)

                if skill_result["learning_result"].get("status") == "policies_updated":
                    active = skill_result["active_policies"]["active_policies"]
                    self.logger.info(f"✓ 行为策略已更新，当前激活 {active} 项策略")
            except Exception as e:
                self.logger.warning(f"技能应用跳过: {e}")

            # 3. 生成日报（传入学习统计信息）
            report = await self.reporter.generate(learnings, learning_stats)

            # 保存日报
            report_path = self.config.report_path / f"report_{datetime.now().strftime('%Y%m%d')}.md"
            report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)

            # 格式化总时长
            total_time = learning_stats.get("total_time", 0)
            if total_time > 0:
                duration_str = self.learner.format_duration(total_time)
                self.logger.info(f"学习完成，添加 {added_count} 条知识，用时 {duration_str}，日报已保存")
            else:
                self.logger.info(f"学习完成，添加 {added_count} 条知识，日报已保存")

            # 4. 自我评估与改进（每次学习后主动进行）
            try:
                from ..improvement.engine import SelfImprovementEngine
                improvement_engine = SelfImprovementEngine(self)

                self.logger.info("🧪 开始自我评估...")
                improvement_result = await improvement_engine.run_self_improvement_cycle()

                if improvement_result.get("status") == "needs_improvement":
                    self.logger.info(f"🔧 发现改进机会: {improvement_result.get('message')}")
                    # 记录到日报
                    self.logger.info(f"   - 建议改进数: {len(improvement_result.get('suggested_actions', []))}")
                elif improvement_result.get("status") == "good":
                    self.logger.info("✅ 自我评估通过，性能良好")
                elif improvement_result.get("status") == "improvement_complete":
                    self.logger.info(f"🎉 自我改进完成: {improvement_result.get('message')}")
            except Exception as e:
                self.logger.warning(f"自我评估跳过: {e}")

            return {
                "search_results": learning_result.get("search_results", 0),
                "parsed": learning_result.get("parsed", 0),
                "learnings": len(learnings),
                "added": added_count,
                "report_path": str(report_path),
                "total_time": total_time,
                "stage_times": learning_stats.get("stage_times", {}),
                "self_improvement": improvement_result if 'improvement_result' in locals() else None
            }

        except Exception as e:
            self.logger.error(f"学习流程失败: {e}")
            return {"error": str(e)}

    async def get_daily_report(self, date: Optional[datetime] = None) -> str:
        """
        获取日报

        Args:
            date: 日期，默认为今天

        Returns:
            日报内容
        """
        if date is None:
            date = datetime.now()

        report_path = self.config.report_path / f"report_{date.strftime('%Y%m%d')}.md"

        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                return f.read()

        return f"没有找到 {date.strftime('%Y-%m-%d')} 的日报"

    def get_skills(self) -> Dict[str, Any]:
        """获取当前技能树"""
        return self.skill_tracker.get_skill_map()

    def get_skill_cloud(self, limit: int = 50) -> List[tuple]:
        """获取技能标签云"""
        return self.skill_tracker.get_tag_cloud(limit)

    async def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        搜索知识库

        Args:
            query: 搜索查询
            top_k: 返回结果数量

        Returns:
            搜索结果列表
        """
        return await self.knowledge.search(query, top_k)

    async def close(self):
        """关闭Agent"""
        self.logger.info("关闭Agent")
        await self.knowledge.close()
