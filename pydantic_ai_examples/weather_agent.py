"""質問に答えるためにLLMが順番に複数のツールを呼び出す必要がある、PydanticAIの例です。

この例では「天気」エージェントを想定しています — ユーザーが複数の都市の天気を尋ねると、
エージェントは`get_lat_lng`ツールを使用して位置の緯度と経度を取得し、
その後`get_weather`ツールを使用して天気を取得します。

実行方法:

    uv run -m pydantic_ai_examples.weather
"""

from __future__ import annotations as _annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

import logfire
from devtools import debug
from httpx import AsyncClient

from pydantic_ai import Agent, ModelRetry, RunContext

# 'if-token-present'は、logfireが設定されていない場合は何も送信されないことを意味します（この場合でも例は動作します）
logfire.configure(send_to_logfire='if-token-present')


@dataclass
class Deps:
    client: AsyncClient
    weather_api_key: str | None
    geo_api_key: str | None


weather_agent = Agent(
    'openai:gpt-4',
    system_prompt='簡潔に、1文で返答してください。',
    deps_type=Deps,
    retries=2,
)


@weather_agent.tool
async def get_lat_lng(
    ctx: RunContext[Deps], location_description: str
) -> dict[str, float]:
    """場所の緯度と経度を取得します。

    Args:
        ctx: コンテキスト
        location_description: 場所の説明
    """
    if ctx.deps.geo_api_key is None:
        # APIキーが提供されていない場合、ダミーのレスポンス（ロンドン）を返す
        return {'lat': 51.1, 'lng': -0.1}

    params = {
        'q': location_description,
        'api_key': ctx.deps.geo_api_key,
    }
    with logfire.span('ジオコードAPIを呼び出し中', params=params) as span:
        r = await ctx.deps.client.get('https://geocode.maps.co/search', params=params)
        r.raise_for_status()
        data = r.json()
        span.set_attribute('response', data)

    if data:
        return {'lat': data[0]['lat'], 'lng': data[0]['lon']}
    else:
        raise ModelRetry('場所が見つかりませんでした')


@weather_agent.tool
async def get_weather(ctx: RunContext[Deps], lat: float, lng: float) -> dict[str, Any]:
    """指定された場所の天気を取得します。

    Args:
        ctx: コンテキスト
        lat: 場所の緯度
        lng: 場所の経度
    """
    if ctx.deps.weather_api_key is None:
        # APIキーが提供されていない場合、ダミーのレスポンスを返す
        return {'temperature': '21 °C', 'description': '晴れ'}

    params = {
        'apikey': ctx.deps.weather_api_key,
        'location': f'{lat},{lng}',
        'units': 'metric',
    }
    with logfire.span('天気APIを呼び出し中', params=params) as span:
        r = await ctx.deps.client.get(
            'https://api.tomorrow.io/v4/weather/realtime', params=params
        )
        r.raise_for_status()
        data = r.json()
        span.set_attribute('response', data)

    values = data['data']['values']
    # https://docs.tomorrow.io/reference/data-layers-weather-codes
    code_lookup = {
        1000: '快晴',
        1100: 'ほぼ晴れ',
        1101: '所々曇り',
        1102: 'ほぼ曇り',
        1001: '曇り',
        2000: '霧',
        2100: '薄い霧',
        4000: '霧雨',
        4001: '雨',
        4200: '小雨',
        4201: '大雨',
        5000: '雪',
        5001: '吹雪',
        5100: '小雪',
        5101: '大雪',
        6000: '凍る霧雨',
        6001: '凍る雨',
        6200: '弱い凍る雨',
        6201: '強い凍る雨',
        7000: '氷粒',
        7101: '強い氷粒',
        7102: '弱い氷粒',
        8000: '雷雨',
    }
    return {
        'temperature': f'{values["temperatureApparent"]:0.0f}°C',
        'description': code_lookup.get(values['weatherCode'], '不明'),
    }


async def main():
    async with AsyncClient() as client:
        # 無料APIキーは https://www.tomorrow.io/weather-api/ で作成できます
        weather_api_key = os.getenv('WEATHER_API_KEY')
        # 無料APIキーは https://geocode.maps.co/ で作成できます
        geo_api_key = os.getenv('GEO_API_KEY')
        deps = Deps(
            client=client, weather_api_key=weather_api_key, geo_api_key=geo_api_key
        )
        result = await weather_agent.run(
            'ロンドンとウィルトシャーの天気はどうですか？', deps=deps
        )
        debug(result)
        print('応答:', result.data)


if __name__ == '__main__':
    asyncio.run(main())