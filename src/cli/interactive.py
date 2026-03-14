"""交互式对话模式"""

from typing import List, Dict
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.syntax import Syntax
from loguru import logger

from ..core.agent import PyAgent


class InteractiveSession:
    """交互式会话"""

    def __init__(self, agent: PyAgent):
        """
        初始化交互会话

        Args:
            agent: PyAgent实例
        """
        self.agent = agent
        self.console = Console()
        self.history: List[Dict] = []
        self.running = True

    async def run(self):
        """运行交互会话"""
        self._print_welcome()

        while self.running:
            try:
                # 获取用户输入
                user_input = self._get_user_input()

                if not user_input:
                    continue

                # 处理命令
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                    continue

                # 发送消息
                await self._send_message(user_input)

            except KeyboardInterrupt:
                self.console.print("\n👋 再见！")
                break
            except Exception as e:
                self.console.print(f"\n❌ 错误: {e}\n")

    def _print_welcome(self):
        """打印欢迎信息"""
        welcome = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🤖 PyAgent - 自进化Python专家Agent                      ║
║                                                           ║
║   输入你的问题，我会基于我的知识库为你解答                ║
║                                                           ║
║   命令:                                                   ║
║     /help    - 显示帮助                                   ║
║     /clear   - 清空对话历史                               ║
║     /skills  - 查看技能树                                 ║
║     /quit    - 退出                                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(welcome)

    def _get_user_input(self) -> str:
        """获取用户输入"""
        try:
            return Prompt.ask(
                "\n💭 你",
                console=self.console,
                default=""
            )
        except EOFError:
            return "/quit"

    async def _send_message(self, user_input: str):
        """发送消息并获取回复"""
        # 显示用户消息
        self.console.print(f"\n💭 [bold cyan]你:[/bold cyan] {user_input}")

        # 添加到历史
        self.history.append({"role": "user", "content": user_input})

        # 获取回复
        with self.console.status("🤔 思考中..."):
            response = await self.agent.chat(user_input, self.history)

        # 显示回复
        self._print_response(response)

        # 添加到历史
        self.history.append({"role": "assistant", "content": response})

        # 限制历史长度
        if len(self.history) > 20:
            self.history = self.history[-20:]

        # 询问是否需要反馈
        self._ask_for_feedback(response)

    def _print_response(self, response: str):
        """打印回复"""
        # 检测是否包含代码块
        if "```" in response:
            self._print_response_with_code(response)
        else:
            # 作为Markdown渲染
            markdown = Markdown(response)
            self.console.print("\n🤖 [bold green]PyAgent:[/bold green]\n")
            self.console.print(markdown)

    def _print_response_with_code(self, response: str):
        """打印包含代码的回复"""
        self.console.print("\n🤖 [bold green]PyAgent:[/bold green]\n")

        parts = response.split("```")
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # 普通文本
                if part.strip():
                    markdown = Markdown(part.strip())
                    self.console.print(markdown)
            else:
                # 代码块
                lines = part.split("\n", 1)
                if len(lines) > 1:
                    lang = lines[0].strip() or "python"
                    code = lines[1]
                    syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
                    self.console.print(syntax)

    def _handle_command(self, command: str):
        """处理命令"""
        cmd = command.lower().strip()

        if cmd == "/help":
            self._print_help()
        elif cmd == "/clear":
            self.history.clear()
            self.console.print("✅ 对话历史已清空")
        elif cmd == "/skills":
            self._show_skills()
        elif cmd in ["/quit", "/exit", "/q"]:
            self.running = False
            self.console.print("👋 再见！")
        else:
            self.console.print(f"❌ 未知命令: {command}")
            self.console.print("   输入 /help 查看可用命令")

    def _print_help(self):
        """打印帮助信息"""
        help_text = """
[bold cyan]可用命令:[/bold cyan]

  /help    - 显示此帮助信息
  /clear   - 清空对话历史
  /skills  - 查看技能树
  /quit    - 退出对话

[bold cyan]技巧:[/bold cyan]

  - 可以问我任何Python相关的问题
  - 我的知识库每天都在更新
  - 支持代码示例和最佳实践
        """
        self.console.print(help_text)

    async def _show_skills(self):
        """显示技能信息"""
        skill_map = self.agent.get_skills()

        self.console.print(f"\n📊 技能概览")
        self.console.print(f"   总技能数: {skill_map['total_skills']}")
        self.console.print(f"   总提及: {skill_map['total_mentions']}")

        # 显示热门技能
        self.console.print(f"\n🔥 热门技能:")
        tag_cloud = self.agent.get_skill_cloud(10)
        for name, count in tag_cloud:
            self.console.print(f"   {name}: {count}")

    def _ask_for_feedback(self, response: str):
        """询问是否需要反馈"""
        # 简化：只根据回复长度决定是否询问
        # 如果回复很长（可能是有价值的知识），询问反馈
        if len(response) < 200:
            return  # 太短的内容不问反馈

        try:
            ask = Prompt.ask(
                "\n💡 这个回答对您有帮助吗？(1-5星，回车跳过)",
                console=self.console,
                default="",
                show_default=False
            )

            if not ask:
                return

            try:
                rating = int(ask)
                if 1 <= rating <= 5:
                    self._save_feedback(response, rating)
            except ValueError:
                pass
        except (EOFError, KeyboardInterrupt):
            pass

    def _save_feedback(self, response: str, rating: int):
        """保存反馈"""
        from ..feedback.collector import FeedbackCollector, Feedback
        from datetime import datetime

        # 生成一个简单的 learning_id（基于响应内容）
        import hashlib
        learning_id = f"chat_{hashlib.md5(response[:50].encode()).hexdigest()[:8]}"

        collector = FeedbackCollector()

        feedback = Feedback(
            id=f"{learning_id}_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            learning_id=learning_id,
            rating=rating,
            useful=rating >= 4,
            problem=None,
            user_comment=None
        )

        collector.save_feedback(feedback)
        self.console.print(f"[dim]✓ 感谢反馈！这将帮助我进化[/dim]")
