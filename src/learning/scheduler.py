"""学习任务调度"""

import asyncio
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from ..core.agent import PyAgent


class LearningScheduler:
    """学习调度器"""

    def __init__(self, agent: PyAgent):
        """
        初始化调度器

        Args:
            agent: PyAgent实例
        """
        self.agent = agent
        self.scheduler = AsyncIOScheduler()
        self.logger = logger

    def start(self):
        """启动调度器"""
        # 解析配置的时间
        schedule_time = self.agent.config.learning_schedule
        hour, minute = map(int, schedule_time.split(":"))

        # 添加定时任务
        self.scheduler.add_job(
            self._run_learning,
            trigger=CronTrigger(hour=hour, minute=minute),
            id="daily_learning",
            name="每日学习任务",
            replace_existing=True
        )

        self.scheduler.start()
        self.logger.info(f"学习调度器启动，每日 {schedule_time} 执行学习")

    async def _run_learning(self):
        """执行学习任务"""
        self.logger.info("定时学习任务触发")
        try:
            result = await self.agent.daily_learning()
            self.logger.info(f"学习完成: {result}")
        except Exception as e:
            self.logger.error(f"学习任务失败: {e}")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        self.logger.info("学习调度器已停止")

    def get_next_run_time(self) -> datetime:
        """获取下次运行时间"""
        job = self.scheduler.get_job("daily_learning")
        if job:
            return job.next_run_time
        return None
