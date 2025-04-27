# Patent System SQL Query Tools

このツールセットは、patent_systemで格納されたSQLiteデータベースをSQLで検索するための機能を提供します。コマンドラインインターフェースとWebインターフェースの両方が利用可能です。

## 概要

このプロジェクトには以下の2つのツールが含まれています：

1. **SQL Query Tool** (command line) - SQLクエリをコマンドラインから実行するためのツール
2. **SQL Web Interface** - ブラウザからSQLクエリを実行するためのWebインターフェース

これらのツールを使用することで、特許データベースの検索、分析、データの抽出が可能になります。

## 必要なパッケージ

両方のツールを使用するには、以下のPythonパッケージが必要です：

```bash
pip install pandas tabulate flask
```

## 1. SQL Query Tool (コマンドラインツール)

### 基本的な使用方法

コマンドラインからSQLクエリを実行するには：

```bash
python sql_query_tool.py -q "SELECT * FROM patents LIMIT 10"
```

### オプション

```
usage: sql_query_tool.py [-h] [-q QUERY] [-f FILE] [-o OUTPUT]
                         [--format {table,csv,json}] [-l LIMIT] [--tables]
                         [--schema SCHEMA] [--count COUNT]

SQL Query Tool for Patent Database

optional arguments:
  -h, --help            ヘルプメッセージの表示
  -q QUERY, --query QUERY
                        実行するSQLクエリ
  -f FILE, --file FILE  SQLクエリを含むファイル
  -o OUTPUT, --output OUTPUT
                        結果を保存するファイル
  --format {table,csv,json}
                        出力形式 (デフォルト: table)
  -l LIMIT, --limit LIMIT
                        結果の最大行数
  --tables              すべてのテーブルを一覧表示
  --schema SCHEMA       指定したテーブルのスキーマを表示
  --count COUNT         指定したテーブルの行数を表示
```

### 使用例

#### テーブル一覧の取得

```bash
python sql_query_tool.py --tables
```

#### テーブル構造の確認

```bash
python sql_query_tool.py --schema patents
```

#### テーブルの行数を確認

```bash
python sql_query_tool.py --count patents
```

#### クエリの結果をCSVファイルに保存

```bash
python sql_query_tool.py -q "SELECT * FROM patents LIMIT 100" --format csv -o patents_export.csv
```

#### クエリの結果をJSONファイルに保存

```bash
python sql_query_tool.py -q "SELECT * FROM patents JOIN applicants ON patents.id = applicants.patent_id LIMIT 50" --format json -o patents_with_applicants.json
```

#### ファイルからSQLクエリを読み込んで実行

```bash
python sql_query_tool.py -f query.sql --format table
```

## 2. SQL Web Interface (ウェブインターフェース)

### 開始方法

Webインターフェースを起動するには：

```bash
python sql_web_interface.py
```

ブラウザで http://localhost:5001 にアクセスするとWebインターフェースが表示されます。

### 機能

Webインターフェースには以下のタブがあります：

1. **Query** - SQLクエリを入力して実行するためのタブ
2. **Schema** - データベース内のテーブル構造を確認するためのタブ
3. **Examples** - サンプルクエリを表示するタブ（クリックでクエリエディタに読み込み可能）
4. **Help** - ヘルプとドキュメントを表示するタブ

### クエリ実行

1. **Query**タブのテキストエリアにSQLクエリを入力
2. **Execute Query**ボタンをクリックして実行
3. 結果は下部に表形式で表示されます

### サンプルクエリ

**Examples**タブには、以下のようなサンプルクエリが用意されています：

- 基本的なクエリ（テーブル全体の取得、カウントなど）
- 特許検索クエリ（出願人、発明者によるフィルタリングなど）
- 高度なクエリ（集計、グループ化など）

## データベース構造

主なテーブルは以下の通りです：

- **patents** - 特許の基本情報（タイトル、要約、出願日など）
- **applicants** - 特許の出願人情報
- **inventors** - 特許の発明者情報
- **ipc_classifications** - 国際特許分類情報
- **claims** - 特許請求項
- **descriptions** - 特許の詳細説明

## クエリ例

### 基本的なクエリ

```sql
-- 特許テーブルから10件取得
SELECT * FROM patents LIMIT 10;

-- 特許の総数を取得
SELECT COUNT(*) AS patent_count FROM patents;
```

### 特許検索クエリ

```sql
-- 出願人名付きの特許情報を取得
SELECT p.id, p.title, p.publication_number, p.application_date, a.name as applicant_name
FROM patents p
JOIN applicants a ON p.id = a.patent_id
LIMIT 20;

-- 最近の特許を発明者情報付きで取得
SELECT p.id, p.title, p.application_date, i.name as inventor_name
FROM patents p
JOIN inventors i ON p.id = i.patent_id
ORDER BY p.application_date DESC
LIMIT 20;
```

### 分析クエリ

```sql
-- 特許数トップ10の出願人を表示
SELECT a.name as applicant_name, COUNT(p.id) as patent_count
FROM patents p
JOIN applicants a ON p.id = a.patent_id
GROUP BY a.name
ORDER BY patent_count DESC
LIMIT 10;

-- 年別の特許出願数を表示
SELECT strftime('%Y', p.application_date) as year, COUNT(*) as patent_count
FROM patents p
WHERE p.application_date IS NOT NULL
GROUP BY year
ORDER BY year DESC;

-- トップ15のIPC分類
SELECT c.code, COUNT(c.id) as usage_count
FROM patents p
JOIN ipc_classifications c ON p.id = c.patent_id
GROUP BY c.code
ORDER BY usage_count DESC
LIMIT 15;
```

### 特殊な検索クエリ

```sql
-- AI関連の特許を検索
SELECT p.id, p.title, p.abstract, GROUP_CONCAT(a.name, ', ') as applicants
FROM patents p
JOIN applicants a ON p.id = a.patent_id
WHERE p.title LIKE '%artificial intelligence%' OR p.abstract LIKE '%artificial intelligence%'
GROUP BY p.id
LIMIT 10;

-- 特許とその第1請求項を表示
SELECT p.title, p.abstract, claim.text as claim_text
FROM patents p
JOIN claims claim ON p.id = claim.patent_id
WHERE claim.claim_number = 1
LIMIT 10;
```

## 注意事項

- パフォーマンスの観点から、大規模なデータセットに対するクエリには必ず `LIMIT` 句を使用してください
- 複雑な結合や集計を行う場合は、クエリの最適化を検討してください
- Webインターフェースでは、セキュリティ上の理由から結果は最大1000行に制限されています
