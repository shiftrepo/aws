# J-PlatPat 特許分析システム

このシステムは日本特許情報プラットフォーム (J-PlatPat) からデータを取得し、特許分析を行うためのツールです。特許データのスクレイピング、SQLiteデータベースへの保存、および様々な分析機能を提供します。

## 機能概要

1. **J-PlatPatからのデータ取得**
   - 企業名、技術分野、または一般的なキーワードでの検索
   - 出願番号と公開番号による特許データの取得
   - 特許の基本情報、出願人、発明者、IPCコードなどの取得
   - 実際のサイトからスクレイピングするロジックを実装（現在はモック実装）

2. **SQLiteデータベース管理**
   - 取得したデータの保存と管理
   - 既存データの更新と重複の排除
   - リレーショナルデータ構造による効率的な検索と分析

3. **特許分析機能**
   - 技術トレンド分析
   - 出願者競争分析
   - 特許ランドスケープ分析
   - 分析レポートの生成

## システム構成

システムは以下のモジュールで構成されています：

- **models_sqlite.py**: SQLiteデータベースのモデル定義（SQLAlchemyセッション管理を含む）
- **jplatpat_scraper.py**: J-PlatPatからのデータ取得機能
- **db_sqlite.py**: データベース操作のための管理クラス
- **jplatpat_importer.py**: スクレイピングとデータ取り込み機能
- **patent_analyzer_sqlite.py**: 特許データの分析機能
- **demo_jplatpat.py**: コマンドラインインターフェース

## 使用方法

### 前提条件

システムを利用する前に、以下のライブラリをインストールする必要があります：

```bash
pip install sqlalchemy pandas numpy requests bs4 tqdm
```

### データのインポート

```bash
# 企業名での検索
python demo_jplatpat.py import --company "トヨタ自動車" --limit 100

# 技術分野での検索
python demo_jplatpat.py import --technology "人工知能" --limit 50 

# キーワード検索
python demo_jplatpat.py import --query "自動運転 AND センサー" --limit 30

# 出願番号での検索（複数指定する場合はカンマ区切り）
python demo_jplatpat.py import --application "2022-100000,2022-100001"

# 公開番号での検索（複数指定する場合はカンマ区切り）
python demo_jplatpat.py import --publication "JP2022-100000A,JP2022-100001A"
```

### データの分析

```bash
# 技術トレンド分析
python demo_jplatpat.py analyze trend --years 5 --top-n 10

# 出願者競争分析
python demo_jplatpat.py analyze applicant --top-n 8

# 特許ランドスケープ分析
python demo_jplatpat.py analyze landscape --ipc-level 2

# レポート生成
python demo_jplatpat.py analyze report --output my_report.md
```

## 実装の詳細

### データベースモデル

特許データは以下のテーブルで構成されています：

- **patents**: 特許の基本情報（出願番号、公開番号、タイトル、概要など）
- **applicants**: 出願者情報
- **inventors**: 発明者情報
- **ipc_classifications**: IPCコード分類
- **claims**: 特許請求の範囲
- **descriptions**: 発明の詳細な説明

### J-PlatPat スクレイパー

現在のスクレイパー実装はモックデータを生成しています。実際のサイトをスクレイピングするためには、以下の改善が必要です：

1. **Seleniumなどを使用したブラウザ自動化**
   - Headless Chromeなどのブラウザを使用
   - フォーム入力と検索の自動化
   - 検索結果のページネーション処理

2. **HTMLパーシング**
   - BeautifulSoupを使用した要素の抽出
   - データ構造化とクリーニング
   - エラー処理とリトライロジック

### 今後の拡張可能性

- **API機能追加**: REST APIでのデータアクセス
- **ビジュアライゼーション**: グラフや図による分析結果の可視化
- **機械学習の導入**: 特許の自動分類や類似特許の検出
- **多言語対応**: 英語、中国語などの特許データベースとの統合
- **詳細な特許分析**: 引用分析、テキストマイニングなど

## 注意事項

- 本システムはJ-PlatPatの利用規約を遵守して使用してください
- 大量のリクエストを短時間に送信するとIPブロックなどのペナルティを受ける可能性があります
- テスト環境では実際のスクレイピングではなくモックデータを使用することを推奨します
