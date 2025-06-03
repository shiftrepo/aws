# 円の為替相場チェッカー

シンプルな円の為替相場を確認するWebアプリケーションです。

## 機能

- 複数の通貨（USD、EUR、GBP、AUD、CAD、CNY）の為替レートを確認できます
- ExchangeRate-APIを利用してリアルタイムデータを取得します
- 選択した通貨1単位あたりの円価格を表示します
- 為替レートの更新時間も表示されます

## 実行方法

### 方法1: ブラウザで直接開く

`index.html` ファイルをブラウザで直接開いて利用できます。

### 方法2: HTTPサーバーを利用する（ポート8080）

1. 以下のコマンドでサーバーを起動します:

```bash
cd /root/aws.git/container/claudecode/test/
python3 -m http.server 8080
```

2. ブラウザで http://localhost:8080 にアクセスします

または、同梱の `server.py` を使用することもできます:

```bash
cd /root/aws.git/container/claudecode/test/
./server.py
```

3. サーバーを停止するには、ターミナルで `Ctrl+C` を押します

## ファイル構成

- `index.html`: メインのHTMLファイル
- `style.css`: スタイルシート
- `script.js`: JavaScriptファイル（APIリクエストとUI更新ロジック）
- `server.py`: 8080ポートでアプリを提供する簡易HTTPサーバー
- `sequence-diagram.md`: アプリケーションの処理フローを示すシーケンス図
- `CLAUDE.md`: Claudeデジタルアシスタント用の情報ファイル