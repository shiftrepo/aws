# J-PlatPat 特許分析システム

このサブディレクトリは日本特許情報プラットフォーム (J-PlatPat) からデータを取得し、特許分析を行うための独立したツールです。特許データのスクレイピング、SQLiteデータベースへの保存、および様々な分析機能を提供します。

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

- **models.py**: SQLiteデータベースのモデル定義（SQLAlchemyセッション管理を含む）
- **scraper.py**: J-PlatPatからのデータ取得機能
- **db_manager.py**: データベース操作のための管理クラス
- **importer.py**: スクレイピングとデータ取り込み機能
- **analyzer.py**: 特許データの分析機能
- **cli.py**: コマンドラインインターフェース

## 使用方法

### 前提条件

システムは必要なライブラリの依存関係を自動的に管理します。初回実行時に必要なライブラリがチェックされ、不足しているライブラリがある場合はインストールするかどうか確認されます。

または、以下のコマンドを使用して手動でライブラリをインストールすることもできます：

```bash
pip install -r app/patent_system/jplatpat/requirements.txt
```

### データのインポート

```bash
# 企業名での検索
python -m app.patent_system.jplatpat.cli import --company "トヨタ自動車" --limit 100

# 技術分野での検索
python -m app.patent_system.jplatpat.cli import --technology "人工知能" --limit 50 

# キーワード検索
python -m app.patent_system.jplatpat.cli import --query "自動運転 AND センサー" --limit 30

# 出願番号での検索（複数指定する場合はカンマ区切り）
python -m app.patent_system.jplatpat.cli import --application "2022-100000,2022-100001"

# 公開番号での検索（複数指定する場合はカンマ区切り）
python -m app.patent_system.jplatpat.cli import --publication "JP2022-100000A,JP2022-100001A"
```

### データの分析

```bash
# 技術トレンド分析
python -m app.patent_system.jplatpat.cli analyze trend --years 5 --top-n 10

# 出願者競争分析
python -m app.patent_system.jplatpat.cli analyze applicant --top-n 8

# 特許ランドスケープ分析
python -m app.patent_system.jplatpat.cli analyze landscape --ipc-level 2

# レポート生成
python -m app.patent_system.jplatpat.cli analyze report --output my_report.md
```

## プログラムでの利用

本機能はライブラリとしても利用できます：

```python
from app.patent_system.jplatpat.importer import Importer
from app.patent_system.jplatpat.analyzer import PatentAnalyzer

# データのインポート
importer = Importer()
count = importer.import_by_company("トヨタ自動車", limit=10)
print(f"インポートした特許数: {count}")

# データの分析
analyzer = PatentAnalyzer()
with analyzer:
    # 技術トレンド分析
    trends = analyzer.analyze_technology_trends(years=5, top_n=10)
    
    # レポート生成
    report = analyzer.generate_analysis_report()
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report)
```

## データベース構造

特許データは以下のテーブルで構成されています：

- **patents**: 特許の基本情報（出願番号、公開番号、タイトル、概要など）
- **applicants**: 出願者情報
- **inventors**: 発明者情報
- **ipc_classifications**: IPCコード分類
- **claims**: 特許請求の範囲
- **descriptions**: 発明の詳細な説明

## 注意事項

- 本システムはJ-PlatPatの利用規約を遵守して使用してください
- 大量のリクエストを短時間に送信するとIPブロックなどのペナルティを受ける可能性があります
- テスト環境では実際のスクレイピングではなくモックデータを使用することを推奨します
