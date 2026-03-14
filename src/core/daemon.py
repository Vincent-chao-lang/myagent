"""守护进程模块"""

import asyncio
import signal
import sys
import os
from pathlib import Path
from datetime import datetime, time
import loguru

from .agent import PyAgent
from .config import config


class PyAgentDaemon:
    """PyAgent守护进程"""

    def __init__(self, agent: PyAgent):
        """
        初始化守护进程

        Args:
            agent: PyAgent实例
        """
        self.agent = agent
        self.pid_file = Path(config.pid_file)
        self.running = False
        self.task = None
        self.shutdown_event = asyncio.Event()  # 用于优雅关闭

        self.logger = loguru.logger

    async def start(self):
        """启动守护进程"""
        # 检查是否已有运行实例
        if self._is_running():
            self.logger.warning("守护进程已在运行")
            return False

        self.running = True
        self.shutdown_event.clear()  # 重置关闭事件

        # 写入PID文件
        self._write_pid()

        # 注册信号处理
        self._setup_signals()

        self.logger.info("守护进程启动")

        # 主循环
        try:
            while self.running:
                await self._wait_for_schedule()
                if self.running:
                    await self.agent.daily_learning()
        except asyncio.CancelledError:
            pass
        finally:
            self._cleanup()

        return True

    def _is_running(self) -> bool:
        """检查是否已有运行实例"""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())

            # 检查进程是否存在
            import os
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                # 进程不存在，清理旧PID文件
                self.pid_file.unlink()
                return False
        except (ValueError, IOError):
            return False

    def _write_pid(self):
        """写入PID文件"""
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))

    def _setup_signals(self):
        """设置信号处理"""
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self._shutdown())
            )

    async def _wait_for_schedule(self):
        """等待调度时间"""
        schedule_time = config.learning_schedule
        hour, minute = map(int, schedule_time.split(":"))

        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # 如果今天的时间已过，设置为明天
        if now >= next_run:
            from datetime import timedelta
            next_run += timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()

        self.logger.info(f"下次学习时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"等待 {wait_seconds:.0f} 秒")

        try:
            # 使用 wait_for 替代 sleep，这样可以被 shutdown_event 中断
            await asyncio.wait_for(
                self.shutdown_event.wait(),
                timeout=wait_seconds
            )
            # 如果被唤醒，说明要关闭
            self.logger.info("等待被中断，准备关闭...")
        except asyncio.TimeoutError:
            # 超时说明等待完成，继续执行学习
            pass
        except asyncio.CancelledError:
            pass

    async def _shutdown(self):
        """优雅关闭"""
        self.logger.info("收到关闭信号，正在关闭...")
        self.running = False
        self.shutdown_event.set()  # 唤醒等待中的任务

    def _cleanup(self):
        """清理资源"""
        self.logger.info("守护进程关闭")

        if self.pid_file.exists():
            self.pid_file.unlink()

    def stop(self):
        """停止守护进程"""
        if not self._is_running():
            self.logger.warning("守护进程未运行")
            # 清理可能存在的PID文件
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False

        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())

            os.kill(pid, signal.SIGTERM)
            self.logger.info(f"已发送停止信号到进程 {pid}")

            # 等待进程退出并清理PID文件
            import time
            for _ in range(10):  # 最多等待10秒
                time.sleep(0.5)
                try:
                    os.kill(pid, 0)  # 检查进程是否还在
                except OSError:
                    # 进程已退出，清理PID文件
                    if self.pid_file.exists():
                        self.pid_file.unlink()
                    self.logger.info("守护进程已停止，PID文件已清理")
                    return True

            # 如果进程还在运行，强制清理PID文件
            if self.pid_file.exists():
                self.pid_file.unlink()
            self.logger.warning("进程未响应，已清理PID文件")
            return True

        except (ValueError, IOError, OSError) as e:
            self.logger.error(f"停止守护进程失败: {e}")
            # 出错时也清理PID文件
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False

    def status(self) -> dict:
        """获取守护进程状态"""
        is_running = self._is_running()

        status_info = {
            "running": is_running,
            "pid_file": str(self.pid_file)
        }

        if is_running and self.pid_file.exists():
            with open(self.pid_file, "r") as f:
                status_info["pid"] = int(f.read().strip())

        return status_info


def start_daemon():
    """启动守护进程的入口函数"""
    async def run():
        agent = PyAgent()
        await agent.initialize()

        daemon = PyAgentDaemon(agent)
        await daemon.start()

        await agent.close()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


def stop_daemon():
    """停止守护进程的入口函数"""
    daemon = PyAgentDaemon(None)
    return daemon.stop()


def daemon_status():
    """获取守护进程状态的入口函数"""
    daemon = PyAgentDaemon(None)
    return daemon.status()
