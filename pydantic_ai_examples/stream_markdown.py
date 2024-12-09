"""このサンプルは、`rich`ライブラリを使用してエージェントからmarkdownをストリーミングして表示する方法を示します。

実行方法:

    uv run -m pydantic_ai_examples.stream_markdown
"""

import asyncio
import os

import logfire
from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.markdown import CodeBlock, Markdown
from rich.syntax import Syntax
from rich.text import Text

from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName

# 'if-token-present'は、logfireが設定されていない場合は何も送信されないことを意味します（この場合でも例は動作します）
logfire.configure(send_to_logfire='if-token-present')

agent = Agent()

# 試すモデルと対応する環境変数
models: list[tuple[KnownModelName, str]] = [
    ('gemini-1.5-flash', 'GEMINI_API_KEY'),
    ('openai:gpt-4o-mini', 'OPENAI_API_KEY'),
    ('groq:llama-3.1-70b-versatile', 'GROQ_API_KEY'),
]


async def main():
    prettier_code_blocks()
    console = Console()
    prompt = 'Pydanticの簡単な使用例を示してください。'
    console.log(f'質問: {prompt}...', style='cyan')
    for model, env_var in models:
        if env_var in os.environ:
            console.log(f'使用モデル: {model}')
            with Live('', console=console, vertical_overflow='visible') as live:
                async with agent.run_stream(prompt, model=model) as result:
                    async for message in result.stream():
                        live.update(Markdown(message))
            console.log(result.cost())
        else:
            console.log(f'{model}を使用するには{env_var}を設定する必要があります。')


def prettier_code_blocks():
    """richのコードブロックをより見やすく、コピーしやすくします。

    参照元: https://github.com/samuelcolvin/aicli/blob/v0.8.0/samuelcolvin_aicli.py#L22
    """

    class SimpleCodeBlock(CodeBlock):
        def __rich_console__(
            self, console: Console, options: ConsoleOptions
        ) -> RenderResult:
            code = str(self.text).rstrip()
            yield Text(self.lexer_name, style='dim')
            yield Syntax(
                code,
                self.lexer_name,
                theme=self.theme,
                background_color='default',
                word_wrap=True,
            )
            yield Text(f'/{self.lexer_name}', style='dim')

    Markdown.elements['fence'] = SimpleCodeBlock


if __name__ == '__main__':
    asyncio.run(main())