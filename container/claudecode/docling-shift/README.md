# Docling Container Setup

このプロジェクトは、IBM Doclingを使用したドキュメント処理のためのPodmanコンテナ環境です。

## 概要

- **Docling**: IBM製のドキュメント解析・変換ツール
- **Podman**: コンテナ実行環境
- **podman-compose**: Docker ComposeのPodman版

## ディレクトリ構造

```
docling-shift/
├── Dockerfile              # Doclingコンテナの定義
├── podman-compose.yml      # コンテナオーケストレーション設定
├── process_documents.py    # ドキュメント処理スクリプト
├── data/                   # ホストとコンテナ間で共有されるデータ
│   ├── input/             # 処理対象ファイルを配置
│   ├── output/            # 変換結果ファイルが出力される
│   ├── config/            # 設定ファイル
│   └── cache/             # Doclingキャッシュ
└── README.md
```

## 前提条件

- Podman がインストールされていること
- podman-compose がインストールされていること

### インストール方法（RHEL/CentOS/Fedora）

```bash
# Podmanのインストール
sudo dnf install podman

# podman-composeのインストール
pip3 install podman-compose
```

## セットアップ手順

### 1. コンテナイメージのビルド

```bash
podman-compose build
```

### 2. コンテナの起動

```bash
# バックグラウンドで起動
podman-compose up -d

# フォアグラウンドで起動（ログを表示）
podman-compose up
```

### 3. コンテナの停止

```bash
podman-compose down
```

## 使用方法

### 基本的なドキュメント処理

1. 処理したいファイルを `data/input/` ディレクトリに配置
2. コンテナ内でスクリプトを実行

```bash
# コンテナに入る
podman exec -it docling-processor bash

# 単一ファイルの処理
python process_documents.py document.pdf

# ディレクトリ内の全ファイルを処理
python process_documents.py /shared/input/

# 出力形式を指定（markdown, json, text）
python process_documents.py document.pdf json
```

### ホストからの直接実行

```bash
# ホストから直接コマンド実行
podman exec docling-processor python process_documents.py /shared/input/document.pdf

# RapidOCRエンジンを使用した処理
podman exec docling-processor docling --ocr-engine rapidocr --to md /shared/input/document.pdf --output /shared/output/document.md
```

## サポートされるファイル形式

- **入力**: PDF, DOCX, PPTX, HTML, TXT, MD, JSON, XML
- **出力**: Markdown, JSON, Text

## 共有ディレクトリ

| ホスト側 | コンテナ側 | 用途 |
|---------|-----------|------|
| `./data/input` | `/shared/input` | 処理対象ファイルの配置 |
| `./data/output` | `/shared/output` | 変換結果の出力 |
| `./data/config` | `/shared/config` | 設定ファイル |
| `./data/cache` | `/shared/cache` | Doclingキャッシュ |

## 設定のカスタマイズ

`data/config/docling_config.py` ファイルを編集して、Doclingの動作をカスタマイズできます：

- OCR設定（言語、DPI、認識モード）
- 出力設定（画像含む、テーブル含む、レイアウト保持）
- サポートファイル形式

## トラブルシューティング

### よくある問題

1. **ファイルが見つからない**
   ```bash
   # ファイルパスとマウントを確認
   ls -la data/input/
   podman exec docling-processor ls -la /shared/input/
   ```

2. **権限エラー**
   ```bash
   # ディレクトリの権限を修正
   sudo chown -R $USER:$USER data/
   chmod -R 755 data/
   ```

3. **コンテナが起動しない**
   ```bash
   # ログを確認
   podman-compose logs docling
   ```

4. **RapidOCRエンジンエラー** （issue #110対応）
   ```bash
   # "ImportError: onnxruntime is not installed" エラーが発生した場合
   podman-compose build --no-cache

   # RapidOCRの動作確認
   podman exec docling-processor docling --ocr-engine rapidocr --help

   # RapidOCRでドキュメント処理テスト
   podman exec docling-processor docling --ocr-engine rapidocr --to md input.pdf --output output.md
   ```

### デバッグ

```bash
# コンテナの状態確認
podman-compose ps

# ログの確認
podman-compose logs -f docling

# コンテナ内での対話的操作
podman exec -it docling-processor bash
```

## API サーバーモード（オプション）

FastAPIサーバーとして起動する場合：

```bash
# コンテナ内でAPIサーバーを起動
podman exec -d docling-processor uvicorn api_server:app --host 0.0.0.0 --port 8000
```

APIエンドポイントは `http://localhost:8000` でアクセス可能です。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。