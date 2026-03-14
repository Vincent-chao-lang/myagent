"""PyAgent主入口"""

import sys
import loguru

# 配置日志
loguru.logger.remove()
loguru.logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)

from .cli.commands import cli

# CLI入口点
def main():
    """CLI主入口"""
    cli()

# 对外暴露的CLI命令
def cli_entry():
    """Click CLI入口"""
    cli()

if __name__ == "__main__":
    main()
