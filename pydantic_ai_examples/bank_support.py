"""銀行のサポートエージェントを構築するためのPydanticAIの小規模かつ完全な例

実行方法:

    uv run -m pydantic_ai_examples.bank_support
"""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext


class DatabaseConn:
    """これはサンプル用の模擬データベースです。

    実際の環境では、外部データベース（PostgreSQLなど）に
    接続して顧客情報を取得することになります。
    """

    @classmethod
    async def customer_name(cls, *, id: int) -> str | None:
        if id == 123:
            return 'John'

    @classmethod
    async def customer_balance(cls, *, id: int, include_pending: bool) -> float:
        if id == 123:
            return 123.45
        else:
            raise ValueError('Customer not found')


@dataclass
class SupportDependencies:
    customer_id: int
    db: DatabaseConn


class SupportResult(BaseModel):
    support_advice: str = Field(description='顧客に返すアドバイス')
    block_card: bool = Field(description='カードをブロックするかどうか')
    risk: int = Field(description='問い合わせのリスクレベル', ge=0, le=10)


support_agent = Agent(
    'openai:gpt-4',
    deps_type=SupportDependencies,
    result_type=SupportResult,
    system_prompt=(
        'あなたは当行のサポートエージェントです。顧客にサポートを提供し、'
        '問い合わせのリスクレベルを判断してください。'
        '顧客の名前を使用して返信してください。'
    ),
)


@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"顧客の名前は {customer_name!r} です"


@support_agent.tool
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> str:
    """顧客の現在の口座残高を返します。"""
    balance = await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id,
        include_pending=include_pending,
    )
    return f'${balance:.2f}'


deps = SupportDependencies(customer_id=123, db=DatabaseConn())
result = support_agent.run_sync('残高を教えてください', deps=deps)
print(result.data)
"""
support_advice='こんにちはJohnさん、保留中の取引を含む現在の口座残高は$123.45です。' block_card=False risk=1
"""

result = support_agent.run_sync('カードをなくしてしまいました！', deps=deps)
print(result.data)
"""
support_advice="申し訳ありません、Johnさん。不正な取引を防ぐため、一時的にカードをブロックさせていただきます。" block_card=True risk=8
"""
