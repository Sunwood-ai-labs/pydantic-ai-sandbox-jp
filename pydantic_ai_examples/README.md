
<div align="center">
  <img src="assets/header.svg" width="100%" alt="AMATERASU Spellbook">

# pydantic_ai_examples

[![CI](https://github.com/pydantic/pydantic-ai/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/pydantic/pydantic-ai/actions/workflows/ci.yml?query=branch%3Amain)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/pydantic/pydantic-ai.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/pydantic/pydantic-ai)
[![PyPI](https://img.shields.io/pypi/v/pydantic-ai.svg)](https://pypi.python.org/pypi/pydantic-ai)
[![versions](https://img.shields.io/pypi/pyversions/pydantic-ai.svg)](https://github.com/pydantic/pydantic-ai)
[![license](https://img.shields.io/github/license/pydantic/pydantic-ai.svg?v)](https://github.com/pydantic/pydantic-ai/blob/main/LICENSE)

</div>


## 💡 概要

本リポジトリは [PydanticAI](https://ai.pydantic.dev/) を活用した、各種 LLM（大規模言語モデル）との連携や入力/出力の構造化を行うサンプルコード集です。  
ここで紹介する例を通じて、PydanticAI の機能や、ツール(Agent・Tool)・型定義・バリデーションを組み合わせた開発手法を理解することができます。

## 📦 セットアップ

本リポジトリは Python 3.9 以上が必要です。  
まず、依存ライブラリをインストールしてください。

```bash
pip install -r requirements.txt
```

また、一部のサンプルは特定の API キー(OPENAI_API_KEY、GEMINI_API_KEY、GROQ_API_KEY、WEATHER_API_KEY、GEO_API_KEY など)が環境変数で必要となります。詳細は各サンプル内のコメントを参照してください。

## 🚀 実行方法

本リポジトリ内の各スクリプトは `pydantic_ai_examples` モジュールとして統一的に実行できます。

例:  
```bash
python -m pydantic_model
```

特定の例外を除き、`python -m <スクリプト名>` の形式で実行可能です。

## 🗂 ディレクトリ構成

```plaintext
C:\Prj\pydantic-ai\pydantic_ai_examples

├─ bank_support.py
├─ chat_app.html
├─ chat_app.py
├─ chat_app.ts
├─ pydantic_model.py
├─ pyproject.toml
├─ rag.py
├─ README.md
├─ roulette_wheel.py
├─ sql_gen.py
├─ stream_markdown.py
├─ stream_whales.py
├─ weather_agent.py
├─ __main__.py
```

## 📝 各サンプルの概要

### 🏦 `bank_support.py`  
銀行のサポートエージェントの例です。  
PydanticAI を用いて顧客IDからデータベースに問い合わせ、顧客名や残高を取得した上で、リスクレベル判定やカードブロック処理などを行います。  
実行方法:  
```bash
python -m bank_support
```

### 💬 `chat_app.py` & `chat_app.html` & `chat_app.ts`  
FastAPI を使った簡易チャットアプリ。  
`chat_app.html` と `chat_app.ts` を組み合わせて、TypeScriptをブラウザ上でトランスパイルし、`chat_app.py` (FastAPI) によるバックエンドと連携してユーザーとのやり取りを行います。  
`/chat/` エンドポイントにユーザー入力を送信し、サーバ側で LLM に問い合わせ、ストリーミングでレスポンス表示が可能です。  

実行例:  
```bash
python -m chat_app
```
その後、ブラウザで `http://localhost:8000` を開いて動作確認ができます。

### 📋 `pydantic_model.py`  
ユーザー入力のテキストから Pydantic モデルを自動生成し、構造化データとして取得する例。  
"風の街はアメリカにあります" のような曖昧な入力から `MyModel`（city, country）を生成させます。

```bash
python -m pydantic_model
```

### 📖 `rag.py` (RAG: Retrieval Augmented Generation)  
RAG 戦略を用いて、外部ドキュメントデータベース(PgVectorによるベクター検索)から関連情報を取得し、LLM の回答精度を向上させる例です。  
`build` コマンドでベクターインデックスを作成し、`search` コマンドで検索実行します。

```bash
# インデックス構築
python -m rag build

# 質問例
python -m rag search "How do I configure logfire to work with FastAPI?"
```

### 🎡 `roulette_wheel.py`  
PydanticAIを使ったシンプルなルーレットゲームの例。  
Tool を用いて、勝利番号とユーザーの掛けた番号を比較し、結果を出力します。

```bash
python -m roulette_wheel
```

### 🗄️ `sql_gen.py`  
ユーザーの自然言語から動的に SQL クエリを生成し、PostgreSQL 上で実行可能か検証する例。  
エージェントが SQL を生成し、実行前にバリデーション、再試行を行います。

```bash
python -m sql_gen "show me logs from yesterday, with level 'error'"
```

### 🖥️ `stream_markdown.py`  
LLMから Markdown形式のコンテンツをストリーミング受信し、`rich` ライブラリでリアルタイム表示する例。  
簡易的な対話内容をマークダウンとして表示するデモです。

```bash
python -m stream_markdown
```

### 🐋 `stream_whales.py`  
クジラに関するデータ(名前、平均体長、平均体重など)をLLMからストリーミングで取得し、PydanticAIでバリデーションしながら `rich` でテーブル表示する例。  
バリデーションエラーなどがあれば即座に再試行や補正が行われます。

```bash
python -m stream_whales
```

### ☀️ `weather_agent.py`  
複数のツール（地名から緯度経度を求める`get_lat_lng`、緯度経度から天気を取得する`get_weather`）を組み合わせ、ユーザーの質問に答えるエージェントの例。  
外部APIキーがある場合は実際のAPIを使用し、ない場合はダミー値を返します。

```bash
python -m weather_agent
```

### 🗄️ `__main__.py`  
CLI補助ツール。  
`--copy-to <dir>` オプションでサンプルコードを別フォルダへまとめてコピーできます。

```bash
uv run -m pydantic_ai_examples --copy-to ./my_new_directory
```

## 📚 詳細ドキュメント

本サンプル集で使用している PydanticAI の詳細なドキュメントは、以下をご確認ください。  
[https://ai.pydantic.dev/](https://ai.pydantic.dev/)

## 🏗️ ライセンス

このプロジェクトは [MIT License](https://github.com/pydantic/pydantic-ai/blob/main/LICENSE) のもとで公開されています。
