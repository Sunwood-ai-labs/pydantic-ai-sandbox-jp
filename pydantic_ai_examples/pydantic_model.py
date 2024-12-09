"""テキスト入力からPydanticモデルを構築するためのPydanticAIの簡単な例です。

実行方法:

    uv run -m pydantic_ai_examples.pydantic_model
"""

import os
from typing import cast

import logfire
from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName

# 'if-token-present'は、logfireが設定されていない場合は何も送信されないことを意味します（この場合でも例は動作します）
logfire.configure(send_to_logfire='if-token-present')


class MyModel(BaseModel):
    city: str
    country: str


model = cast(KnownModelName, os.getenv('PYDANTIC_AI_MODEL', 'openai:gpt-4'))
print(f'使用モデル: {model}')
agent = Agent(model, result_type=MyModel)

if __name__ == '__main__':
    result = agent.run_sync('The windy city in the US of A.')
    print(result.data)
    print(result.cost())