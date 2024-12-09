"""PydanticAIを使用してユーザー入力に基づいてSQLクエリを生成する例です。

postgresの実行方法:

    mkdir postgres-data
    docker run --rm -e POSTGRES_PASSWORD=postgres -p 54320:5432 postgres

実行方法:

    uv run -m pydantic_ai_examples.sql_gen "昨日のエラーレベルのログを表示して"
"""

import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Any, Union

import asyncpg
import logfire
from annotated_types import MinLen
from devtools import debug
from pydantic import BaseModel, Field
from typing_extensions import TypeAlias

from pydantic_ai import Agent, ModelRetry, RunContext

# 'if-token-present'は、logfireが設定されていない場合は何も送信されないことを意味します（この場合でも例は動作します）
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_asyncpg()

DB_SCHEMA = """
CREATE TABLE records (
    created_at timestamptz,
    start_timestamp timestamptz,
    end_timestamp timestamptz,
    trace_id text,
    span_id text,
    parent_span_id text,
    level log_level,
    span_name text,
    message text,
    attributes_json_schema text,
    attributes jsonb,
    tags text[],
    is_exception boolean,
    otel_status_message text,
    service_name text
);
"""


@dataclass
class Deps:
    conn: asyncpg.Connection


class Success(BaseModel):
    """SQLが正常に生成された場合のレスポンス。"""

    sql_query: Annotated[str, MinLen(1)]
    explanation: str = Field(
        '', description='SQLクエリの説明（マークダウン形式）'
    )


class InvalidRequest(BaseModel):
    """ユーザー入力にSQLを生成するための十分な情報が含まれていない場合のレスポンス。"""

    error_message: str


Response: TypeAlias = Union[Success, InvalidRequest]
agent = Agent(
    'gemini-1.5-flash',
    # PEP-0747を待つ間のType ignore、それ以外の場所ではユニオンは正常に動作します
    result_type=Response,  # type: ignore
    deps_type=Deps,
)


@agent.system_prompt
async def system_prompt() -> str:
    return f"""\
以下のPostgreSQLのレコードテーブルについて、
ユーザーのリクエストに合うSQLクエリを作成することがあなたの仕事です。

データベーススキーマ:

{DB_SCHEMA}

今日の日付 = {date.today()}

例
    リクエスト: foobarがfalseのレコードを表示して
    レスポンス: SELECT * FROM records WHERE attributes->>'foobar' = false
例
    リクエスト: 属性にfoobarというキーを含むレコードを表示して
    レスポンス: SELECT * FROM records WHERE attributes ? 'foobar'
例
    リクエスト: 昨日のレコードを表示して
    レスポンス: SELECT * FROM records WHERE start_timestamp::date > CURRENT_TIMESTAMP - INTERVAL '1 day'
例
    リクエスト: タグ"foobar"があるエラーレコードを表示して
    レスポンス: SELECT * FROM records WHERE level = 'error' and 'foobar' = ANY(tags)
"""


@agent.result_validator
async def validate_result(ctx: RunContext[Deps], result: Response) -> Response:
    if isinstance(result, InvalidRequest):
        return result

    # geminiはしばしばSQLに余分なバックスラッシュを追加します
    result.sql_query = result.sql_query.replace('\\', '')
    if not result.sql_query.upper().startswith('SELECT'):
        raise ModelRetry('SELECTクエリを作成してください')

    try:
        await ctx.deps.conn.execute(f'EXPLAIN {result.sql_query}')
    except asyncpg.exceptions.PostgresError as e:
        raise ModelRetry(f'無効なクエリ: {e}') from e
    else:
        return result


async def main():
    if len(sys.argv) == 1:
        prompt = '昨日のエラーレベルのログを表示して'
    else:
        prompt = sys.argv[1]

    async with database_connect(
        'postgresql://postgres:postgres@localhost:54320', 'pydantic_ai_sql_gen'
    ) as conn:
        deps = Deps(conn)
        result = await agent.run(prompt, deps=deps)
    debug(result.data)


# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
@asynccontextmanager
async def database_connect(server_dsn: str, database: str) -> AsyncGenerator[Any, None]:
    with logfire.span('データベースの確認と作成'):
        conn = await asyncpg.connect(server_dsn)
        try:
            db_exists = await conn.fetchval(
                'SELECT 1 FROM pg_database WHERE datname = $1', database
            )
            if not db_exists:
                await conn.execute(f'CREATE DATABASE {database}')
        finally:
            await conn.close()

    conn = await asyncpg.connect(f'{server_dsn}/{database}')
    try:
        with logfire.span('スキーマ作成'):
            async with conn.transaction():
                if not db_exists:
                    await conn.execute(
                        "CREATE TYPE log_level AS ENUM ('debug', 'info', 'warning', 'error', 'critical')"
                    )
                await conn.execute(DB_SCHEMA)
        yield conn
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())