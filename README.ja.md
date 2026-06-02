# Claude Json2md for NotebookLM

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/github/license/minipoisson/Claude_Json2md4NotebookLM)
[![Release](https://img.shields.io/github/v/release/minipoisson/Claude_Json2md4NotebookLM)](https://github.com/minipoisson/Claude_Json2md4NotebookLM/releases)

ClaudeのエクスポートデータJSON（`conversations.json`）を、NotebookLMに取り込みやすい連番Markdownファイル（`Claude_History-01.md` など）に変換するスクリプトです。

[Gemini_Json2md4NotebookLM](https://github.com/minipoisson/Gemini_Json2md4NotebookLM) および [ChatGPT_Json2md4NotebookLM](https://github.com/minipoisson/ChatGPT_Json2md4NotebookLM) と同じ設計思想を踏襲した姉妹ツールシリーズの一つです。

[English README is here](README.md)

## 主な機能

- HTMLタグを除去し、会話をMarkdown形式に整形
- NotebookLMの取り込み上限を考慮して自動でファイル分割（デフォルト: 1MB）
- `last_entry_time.txt` による差分更新対応 — 2回目以降は新しい会話分のみ処理

## 依存関係

外部ライブラリは不要です（Python標準ライブラリのみ）

## 動作要件

- Python 3.9 以上

## 使い方

### 1. Claudeのチャット履歴をエクスポート

[claude.ai/settings/privacy](https://claude.ai/settings/privacy) にアクセスし、データエクスポートをリクエストします。  
メールでダウンロードリンクが届きます（数分〜数日以内）。  
ZIPを展開し、`conversations.json` を取り出します。

### 2. ファイルの配置

`conversations.json` をスクリプトと同じディレクトリに置きます。

### 3. スクリプトの実行

```bash
python convert_claude_history.py [--input_file FILE] [--output_file FILE] [--limit SIZE]
```

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--input_file` | `conversations.json` | エクスポートしたJSONファイルのパス |
| `--output_file` | `Claude_History.md` | 出力Markdownファイルのベース名 |
| `--limit` | `1000000` | ファイル分割の上限バイト数 |

実行例:

```bash
python convert_claude_history.py --input_file conversations.json --output_file Claude_History.md --limit 1000000
```

### 4. NotebookLMへのアップロード

生成された `Claude_History-00.md`、`-01.md`... をNotebookLMのノートブックのソースとして追加します。

## 注意事項

- `--limit` のデフォルトは **1,000,000バイト（1MB）** に設定しています。1.5MBでは稀にNotebookLMへの取り込みに失敗することがあったため、この値に変更しています。
- 初回実行時はすべての会話を処理します。2回目以降は前回処理以降に更新された会話のみを追記処理します（差分更新）。
- エクスポートされたJSONの構造を確認したい場合は以下を実行してください:  
  ```bash
  python -c "import json; d=json.load(open('conversations.json')); print(list(d[0].keys())); print(list(d[0]['chat_messages'][0].keys()))"
  ```

## 複数のAIチャット履歴を一つのNotebookLMに統合する

Claude・Gemini・ChatGPT のチャット履歴を同一のNotebookLMノートブックに登録することで、AI横断の分析が可能になります。たとえば、あるAIが出力したハルシネーションが、別のAIとの会話で検証・発見された経緯を、NotebookLM上で一連の流れとして追跡できます。

| AIサービス | エクスポートツール |
|-----------|------------------|
| Gemini    | [Gemini_Json2md4NotebookLM](https://github.com/minipoisson/Gemini_Json2md4NotebookLM) |
| ChatGPT   | [ChatGPT_Json2md4NotebookLM](https://github.com/minipoisson/ChatGPT_Json2md4NotebookLM) |

このAI横断のユースケースこそが、このツールシリーズが各AI公式機能では代替できない固有の価値を持つ理由です。

## ライセンス

MIT License。詳細は [LICENSE](LICENSE) を参照してください。
