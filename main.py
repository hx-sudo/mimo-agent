import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown
from agent.core import Agent
from tools.calculator import Calculator
from utils.config import get_models, get_default_model


console = Console()


def select_model() -> str:
    """让用户选择模型"""
    models = get_models()
    default_model = get_default_model()

    console.print("\n[bold]可用模型:[/bold]")
    for i, model in enumerate(models, 1):
        default_mark = " (默认)" if model["name"] == default_model else ""
        console.print(f"  {i}. {model['label']} [dim]{model['name']}[/dim]{default_mark}")

    choice = IntPrompt.ask(
        "\n选择模型编号",
        default=next(
            i for i, m in enumerate(models, 1) if m["name"] == default_model
        ),
    )

    if 1 <= choice <= len(models):
        selected = models[choice - 1]
        console.print(f"已选择: [green]{selected['label']}[/green]\n")
        return selected["name"]

    console.print("[yellow]无效选择，使用默认模型[/yellow]")
    return default_model


def main():
    console.print(Panel.fit(
        "[bold cyan]AI Agent[/bold cyan]\n"
        "[dim]输入 /help 查看命令，/quit 退出[/dim]",
        border_style="cyan",
    ))

    model = select_model()
    agent = Agent(model=model)

    # 注册工具
    agent.register_tool(Calculator())

    console.print("[green]Agent 已就绪，开始对话吧！[/green]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold blue]你[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n再见！")
            break

        if not user_input.strip():
            continue

        # 内置命令
        if user_input.startswith("/"):
            cmd = user_input.strip().lower()
            if cmd == "/quit" or cmd == "/exit":
                console.print("再见！")
                break
            elif cmd == "/clear":
                agent.clear_history()
                console.print("[yellow]对话历史已清除[/yellow]")
            elif cmd == "/help":
                console.print(Panel(
                    "/clear  - 清除对话历史\n"
                    "/quit   - 退出程序\n"
                    "/help   - 显示帮助",
                    title="命令",
                ))
            else:
                console.print(f"[red]未知命令: {cmd}[/red]")
            continue

        # 调用 agent
        with console.status("[dim]思考中...[/dim]"):
            response = agent.chat(user_input)

        console.print(f"\n[bold green]Agent[/bold green]")
        console.print(Markdown(response))
        console.print()


if __name__ == "__main__":
    main()
