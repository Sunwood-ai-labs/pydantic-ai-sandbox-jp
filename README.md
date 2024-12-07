<div align="center">
  <img src="assets/header.svg" alt="PydanticAI Sandbox JP">

  # PydanticAI サンドボックス 🚀

PydanticAIを使った日本語での実装例やサンプルコードを集めたリポジトリです。

</div>



## 🌟 PydanticAIとは

PydanticAIは、Pydantic（OpenAI SDK、Anthropic SDK、LangChain、LlamaIndex、AutoGPT、Transformers、CrewAI、Instructorなど多くのライブラリで使用されている検証レイヤー）のチームによって開発された、生成AIを使用した本番環境グレードのアプリケーションを構築するためのPythonエージェントフレームワークです。

### 主な特徴

- 🔧 モデルに依存しない設計（OpenAI、Gemini、Groqをサポート）
- ✨ 型安全なインターフェース
- 🔍 Pydanticによる構造化されたレスポンスの検証
- 🌊 ストリーミングレスポンスのサポート
- 🎯 テストと評価駆動の開発に便利な型安全な依存性注入システム
- 📊 Logfireとの統合によるデバッグとモニタリング

## 🚀 クイックスタート

最もシンプルな例から始めてみましょう：

```python
from pydantic_ai import Agent

# モデルを指定してエージェントを定義
agent = Agent(
    'gemini-1.5-flash',
    # システムプロンプトを設定
    system_prompt='簡潔に、1文で回答してください。',
)

# エージェントを同期的に実行
result = agent.run_sync('プログラミングの"Hello World"の由来は？')
print(result.data)
"""
"Hello World"は1974年のC言語の教科書で初めて使用された例文です。
"""
```

## 🛠 サンプル集

このリポジトリには以下のような実装例が含まれています：

1. 基本的な使い方
2. ツールと依存性注入の例
3. 構造化レスポンスの実装
4. 日本語でのプロンプトエンジニアリング

## 📚 ドキュメント

より詳細な情報は[公式ドキュメント](https://ai.pydantic.dev)をご覧ください。

## 🤝 コントリビューション

サンプルコードの追加や改善案は大歓迎です！お気軽にPRを送ってください。

## ⚠️ 注意事項

このプロジェクトはPydanticAIの使用例を日本語で提供することを目的としています。PydanticAI自体はベータ版であり、APIは変更される可能性があります。

## 📜 ライセンス

MITライセンスの下で公開されています。
