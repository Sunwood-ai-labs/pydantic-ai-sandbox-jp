"""PydanticAIを使用して簡単なルーレットゲームを作成する例です。

実行方法:
    uv run -m pydantic_ai_examples.roulette_wheel
"""

from __future__ import annotations as _annotations

import asyncio
from dataclasses import dataclass
from typing import Literal

from pydantic_ai import Agent, RunContext


# 依存関係クラスの定義
@dataclass
class Deps:
    winning_number: int


# 適切な型定義を持つエージェントの作成
roulette_agent = Agent(
    'groq:llama-3.1-70b-versatile',
    deps_type=Deps,
    retries=3,
    result_type=bool,
    system_prompt=(
        '`roulette_wheel`関数を使用して、'
        'プレイヤーが賭けた番号に基づいて勝利したかどうかを判定してください。'
    ),
)


@roulette_agent.tool
async def roulette_wheel(
    ctx: RunContext[Deps], square: int
) -> Literal['winner', 'loser']:
    """賭けたマスが当選かどうかを確認します。

    Args:
        ctx: 当選番号を含むコンテキスト
        square: プレイヤーが賭けた番号
    """
    return 'winner' if square == ctx.deps.winning_number else 'loser'


async def main():
    # 依存関係のセットアップ
    winning_number = 18
    deps = Deps(winning_number=winning_number)

    # ストリーミングを使用していくつかのベット例を実行
    async with roulette_agent.run_stream(
        '18番に賭けます', deps=deps
    ) as response:
        result = await response.get_data()
        print('18への賭け:', result)

    async with roulette_agent.run_stream(
        '5番が勝つと賭けます', deps=deps
    ) as response:
        result = await response.get_data()
        print('5への賭け:', result)


if __name__ == '__main__':
    asyncio.run(main())