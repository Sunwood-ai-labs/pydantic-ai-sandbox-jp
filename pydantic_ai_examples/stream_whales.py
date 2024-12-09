"""クジラに関する情報 - ストリーミング構造化レスポンス検証の例。

このスクリプトは、クジラに関するGPT-4からの構造化レスポンスをストリーミングし、
データを検証し、受信したデータをRichを使用して動的なテーブルとして表示します。

実行方法:

    uv run -m pydantic_ai_examples.whales
"""

from typing import Annotated, NotRequired, TypedDict

import devtools
import logfire
from pydantic import Field, ValidationError
from rich.console import Console
from rich.live import Live
from rich.table import Table

from pydantic_ai import Agent

# 'if-token-present'は、logfireが設定されていない場合は何も送信されないことを意味します（この場合でも例は動作します）
logfire.configure(send_to_logfire='if-token-present')


class Whale(TypedDict):
    name: str
    length: Annotated[
        float, Field(description='成体クジラの平均体長（メートル）')
    ]
    weight: NotRequired[
        Annotated[
            float,
            Field(description='成体クジラの平均体重（キログラム）', ge=50),
        ]
    ]
    ocean: NotRequired[str]
    description: NotRequired[Annotated[str, Field(description='短い説明')]]


agent = Agent('openai:gpt-4', result_type=list[Whale])


def check_validation_error(e: ValidationError) -> bool:
    devtools.debug(e.errors())
    return False


async def main():
    console = Console()
    with Live('\n' * 36, console=console) as live:
        console.print('データをリクエスト中...', style='cyan')
        async with agent.run_stream(
            '5種類のクジラの詳細情報を生成してください。'
        ) as result:
            console.print('レスポンス:', style='green')

            async for message, last in result.stream_structured(debounce_by=0.01):
                try:
                    whales = await result.validate_structured_result(
                        message, allow_partial=not last
                    )
                except ValidationError as exc:
                    if all(
                        e['type'] == 'missing' and e['loc'] == ('response',)
                        for e in exc.errors()
                    ):
                        continue
                    else:
                        raise

                table = Table(
                    title='クジラの種類',
                    caption='GPT-4からのストリーミング構造化レスポンス',
                    width=120,
                )
                table.add_column('ID', justify='right')
                table.add_column('名前')
                table.add_column('平均体長 (m)', justify='right')
                table.add_column('平均体重 (kg)', justify='right')
                table.add_column('生息海域')
                table.add_column('説明', justify='right')

                for wid, whale in enumerate(whales, start=1):
                    table.add_row(
                        str(wid),
                        whale['name'],
                        f'{whale["length"]:0.0f}',
                        f'{w:0.0f}' if (w := whale.get('weight')) else '…',
                        whale.get('ocean') or '…',
                        whale.get('description') or '…',
                    )
                live.update(table)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())