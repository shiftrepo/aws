# 特許出願人分析システム

このシステムは特許審査官や知財担当者向けに、特許出願人の詳細な分析を提供するサービスです。AI（人工知能）アシスタントを通じて特許データを分析し、視覚的なレポートを生成することができます。

## システムの概要

このシステムを使うと、次のようなことができます：

- 企業（出願人）ごとの特許出願状況の分析
- 特許査定率と拒絶率の確認
- 企業が強みを持つ技術分野の把握
- 競合他社との比較分析
- 視覚的なグラフやチャートを含むレポートの生成
- PDFレポートの自動作成（分類別出願数の棒グラフ、査定状況の円グラフを含む）

## はじめに

### 必要なもの

- Python 3.8以上
- 必要なライブラリ（requirements.txtに記載）
  - matplotlib（グラフ作成）
  - pandas（データ処理）
  - reportlab（PDFレポート作成）
  - sqlalchemy（データベース処理）

### インストール方法

```bash
# 必要なライブラリをインストール
pip install -r requirements.txt

# 初期化とデモの実行
python init_and_demo.py
```

## 基本的な使い方

### デモの実行

このシステムの機能を確認するには、以下のデモスクリプトを実行してください：

```bash
# 特許分析機能のデモ
python demo_analysis.py

# PDFレポート生成機能のデモ
python report_demo.py
```

### AIアシスタント（Claude、ChatGPT等）との連携

このシステムはMCP（Model Context Protocol）を通じて、AIアシスタントと連携できます。AIアシスタントに対して、以下のように質問するだけで、分析結果が返ってきます：

- 「テック株式会社の特許出願状況を教えてください」
- 「AIソリューションズと未来技研の特許査定率を比較してください」
- 「データシステムズの技術分野別の出願分布をPDFレポートとして作成してください」

## PDF出力機能について

企業の情報要求に応えて、以下のようなPDFレポートを自動生成できます：

1. **分類別出願数の年別推移（棒グラフ）**：
   - 特許分類（IPC）ごとの出願数推移を視覚的に表示
   - 最大10年分のトレンドを確認可能

2. **査定状況の分布（円グラフ）**：
   - 特許査定、拒絶査定、審査中などの割合を表示
   - 特定企業または全体の査定状況を比較可能

3. **企業比較レポート**：
   - 最大5社の査定率や技術分布を比較
   - 競合優位性の分析に活用可能

## MCPサーバーの利用方法（システム管理者向け）

### MCPサーバーとは

MCPサーバーは、AIアシスタント（Claude、ChatGPTなど）が特許分析機能を利用するための接続点です。APIのように働き、AIアシスタントからのリクエストを受け取り、処理結果を返します。

### セットアップ方法

1. **MCPサーバーの構成設定**

   `mcp_config.json`ファイルは、MCPサーバーの基本設定を含んでいます：

   ```json
   {
     "servers": [
       {
         "name": "patent-applicant-analyzer",
         "version": "1.0.0",
         "description": "特許出願人の分析ツール",
         "module_path": "app.patent_system.mcp_patent_server",
         "enabled": true,
         "auth": {
           "type": "none"
         }
       }
     ]
   }
   ```

2. **Difyでの利用方法**

   Difyでこのシステムを利用する場合：
   
   a. Difyのアプリ設定画面に移動
   b. 「ツール」→「カスタムツール」を選択
   c. 「新規作成」ボタンをクリック
   d. 以下の情報を入力：
      - **名前**: patent-applicant-analyzer
      - **説明**: 特許出願人の分析ツールです
      - **認証タイプ**: None
      - **エンドポイントURL**: http://[あなたのサーバーのアドレス]:8000/
      - **OpenAPI仕様**: 下記の情報をアップロード（または手動入力）

   ```yaml
   openapi: 3.0.0
   info:
     title: 特許出願人分析API
     description: 特許出願人の詳細分析とレポート生成のためのAPI
     version: 1.0.0
   paths:
     /tools/patent-applicant-analyzer/get_applicant_summary:
       post:
         summary: 出願人の要約情報を取得
         requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   applicant_name:
                     type: string
                     description: 分析する出願人名
                 required:
                   - applicant_name
         responses:
           200:
             description: 成功
     /tools/patent-applicant-analyzer/generate_pdf_report:
       post:
         summary: PDF分析レポートを生成
         requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   applicant_name:
                     type: string
                     description: 分析する出願人名（省略可能）
                   years:
                     type: integer
                     description: 分析年数
                     default: 10
                   top_n:
                     type: integer
                     description: 表示する分類数
                     default: 5
         responses:
           200:
             description: 成功
     /tools/patent-applicant-analyzer/generate_comparison_report:
       post:
         summary: 複数出願人の比較レポートを生成
         requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   applicants:
                     type: array
                     items:
                       type: string
                     description: 比較する出願人名のリスト
                 required:
                   - applicants
         responses:
           200:
             description: 成功
   ```

### サーバーの起動方法

```bash
# MCPサーバーを単独で起動
python -m app.patent_system.mcp_demo

# または本体アプリケーションサーバー起動時に自動的に開始されます
```

## 使用例とシナリオ

### 例1：特許出願状況の分析

特許審査官や知財担当者が、特定企業の特許出願状況を把握したい場合：

```
「テック株式会社の過去5年間の特許出願傾向と査定率を教えてください。特に、G06F分野の詳細情報も知りたいです。」
```

### 例2：複数企業の比較

競合他社との状況を比較したい場合：

```
「テック株式会社、イノベーション製造、未来技研の特許査定状況を比較したPDFレポートを作成してください。」
```

### 例3：技術分野別の分析

特定の技術分野における企業の状況を分析したい場合：

```
「AIソリューションズのAI関連技術（G06N）の特許出願について詳細に分析し、棒グラフと円グラフを含むPDFレポートを生成してください。」
```

## トラブルシューティング

### よくある問題と解決策

1. **グラフに日本語が正しく表示されない場合**
   - matplotlibの日本語フォント設定を確認してください
   - システムに適切な日本語フォントがインストールされているか確認してください

2. **PDFに日本語が表示されない場合**
   - reportlabで日本語対応フォントを適切に設定してください
   - PDFに日本語を埋め込む設定を確認してください

3. **特定の出願人の情報が取得できない場合**
   - 企業名の表記が正確か確認してください
   - データベースに該当する出願人が存在するか確認してください

## 更新履歴

* **2025-04-20**: 
  * 企業の情報要求に応えるために、分類別の出願数を表した年別の棒グラフと特許査定、拒絶査定その他の査定比率の円グラフをPDFの別添資料として出力する機能を追加しました。
  * MCPサーバーを通じた`generate_pdf_report`と`generate_comparison_report`の2つの新しいツールを追加しました。
  * Dify等の外部システムとの連携手順を追加しました。

## お問い合わせ

システムに関するご質問・お問い合わせは、以下にお寄せください：

- メール: support@example.com
- 内線: 1234
