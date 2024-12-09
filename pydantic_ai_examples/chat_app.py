"""FastAPIを使用した簡単なチャットアプリの例です。

実行方法:

    uv run -m pydantic_ai_examples.chat_app
"""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import fastapi
import logfire
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from pydantic import Field, TypeAdapter

from pydantic_ai import Agent
from pydantic_ai.messages import (
    Message,
    MessagesTypeAdapter,
    ModelTextResponse,
    UserPrompt,
)

# 'if-token-present'は、logfireが設定されていない場合は何も送信されないことを意味します（この場合でも例は動作します）
logfire.configure(send_to_logfire='if-token-present')

agent = Agent('openai:gpt-4')

app = fastapi.FastAPI()
logfire.instrument_fastapi(app)


@app.get('/')
async def index() -> HTMLResponse:
    return HTMLResponse((THIS_DIR / 'chat_app.html').read_bytes())


@app.get('/chat_app.ts')
async def main_ts() -> Response:
    """生のTypeScriptコードを取得します。ブラウザでコンパイルされます（ご容赦ください）。"""
    return Response((THIS_DIR / 'chat_app.ts').read_bytes(), media_type='text/plain')


@app.get('/chat/')
async def get_chat() -> Response:
    msgs = database.get_messages()
    return Response(
        b'\n'.join(MessageTypeAdapter.dump_json(m) for m in msgs),
        media_type='text/plain',
    )


@app.post('/chat/')
async def post_chat(prompt: Annotated[str, fastapi.Form()]) -> StreamingResponse:
    async def stream_messages():
        """クライアントに新しい行区切りのJSON `Message`をストリーミングします。"""
        # ユーザープロンプトをすぐに表示できるようにストリーミング
        yield MessageTypeAdapter.dump_json(UserPrompt(content=prompt)) + b'\n'
        # エージェントにコンテキストとして渡すためのチャット履歴を取得
        messages = list(database.get_messages())
        # ユーザープロンプトとチャット履歴でエージェントを実行
        async with agent.run_stream(prompt, message_history=messages) as result:
            async for text in result.stream(debounce_by=0.01):
                # ここのtextは `str` で、フロントエンドは
                # JSONエンコードされたModelTextResponseを期待しているので、作成します
                m = ModelTextResponse(content=text, timestamp=result.timestamp())
                yield MessageTypeAdapter.dump_json(m) + b'\n'

        # 新しいメッセージ（この場合はユーザープロンプトとエージェントの応答）をデータベースに追加
        database.add_messages(result.new_messages_json())

    return StreamingResponse(stream_messages(), media_type='text/plain')


THIS_DIR = Path(__file__).parent
MessageTypeAdapter: TypeAdapter[Message] = TypeAdapter(
    Annotated[Message, Field(discriminator='role')]
)


@dataclass
class Database:
    """JSONLファイルにチャットメッセージを保存する非常に基本的なデータベースです。"""

    file: Path = THIS_DIR / '.chat_app_messages.jsonl'

    def add_messages(self, messages: bytes):
        with self.file.open('ab') as f:
            f.write(messages + b'\n')

    def get_messages(self) -> Iterator[Message]:
        if self.file.exists():
            with self.file.open('rb') as f:
                for line in f:
                    if line:
                        yield from MessagesTypeAdapter.validate_json(line)


database = Database()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'pydantic_ai_examples.chat_app:app', reload=True, reload_dirs=[str(THIS_DIR)]
    )