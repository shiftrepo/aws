# Patent SQLite

特許情報へのアクセスを簡素化する SQLite ベースのコンテナアプリケーション

## アプリケーションの概要

Patent SQLite は、Google BigQuery の公開特許データセットおよびJ-PlatPat（日本特許情報プラットフォーム）から特許情報を取得し、ローカルの SQLite データベースに格納するコンテナ化されたアプリケーションです。このアプリケーションにより、以下のことが可能になります：

- 特許番号、公開番号、出願人、技術分類によるデータフィルタリング
- BigQuery および J-PlatPat から特許データのインポート
- 日本語の特許情報を含む多様な特許データへのアクセス
- ローカル SQLite データベースへの保存と高速なクエリ
- RESTful API を通じたデータアクセス

### データベース構造

特許データは以下のスキーマで SQLite データベースに保存されます：

```sql
CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    publication_number TEXT,
    applicant TEXT,
    theme TEXT,
    title TEXT,
    abstract TEXT,
    filing_date TEXT,
    grant_date TEXT,
    assignee TEXT,
    inventor TEXT,
    additional_data TEXT
)
```

## セットアップと操作手順

### 前提条件

- Docker または Podman
- docker-compose または podman-compose
- BigQuery アクセス権を持つ Google Cloud サービスアカウント

### 起動手順

1. プロジェクトディレクトリに移動します：
   ```
   cd patent-sqlite
   ```

2. セットアップスクリプトを実行します：
   ```
   ./setup.sh
   ```

   このスクリプトは以下のことを行います：
   - GCP サービスアカウントキーのダウンロード（可能な場合）
   - コンテナのビルドと起動
   - データベースの初期化

   **注意**: サービスアカウントキーのダウンロードに失敗した場合は、手動でサービスアカウントキーをコピーする必要があります：
   ```
   cp /path/to/your/key.json ./service-key/tosapi-bd19ecc6f5bb.json
   ```

### 手動での起動（setup.sh を使用しない場合）

コンテナをビルドして起動します：
```
# Docker の場合
docker-compose up -d --build

# Podman の場合
podman-compose up -d --build
```

データベースを初期化します：
```
curl http://localhost:5000/init
```

### 停止手順

コンテナの停止とリソースの解放：
```
# Docker の場合
docker-compose down

# Podman の場合
podman-compose down
```

## 使用例

### データベースのステータス確認

データベースの初期化状態と保存されている特許数を確認します：

```
curl http://localhost:5000/status
```

レスポンス例：
```json
{
  "status": "success",
  "database_initialized": true,
  "patent_count": 42
}
```

### データソース

Patent SQLite は、以下のデータソースから特許情報を取得・格納することができます：

1. **Google BigQuery 特許データセット**
2. **J-PlatPat（日本特許情報プラットフォーム）**

### BigQuery からの特許データのインポート

各種フィルタを使用して特許をインポートすることができます。すべてのフィルタはオプションです。

#### 例1: 特許番号によるインポート

```
curl -X POST http://localhost:5000/import \
  -H "Content-Type: application/json" \
  -d '{"patent_id": "US12345678"}'
```

#### 例2: 公開番号によるインポート

```
curl -X POST http://localhost:5000/import \
  -H "Content-Type: application/json" \
  -d '{"publication_number": "US20200123456A1"}'
```

#### 例3: 出願人によるインポート

```
curl -X POST http://localhost:5000/import \
  -H "Content-Type: application/json" \
  -d '{"applicant": "Google"}'
```

#### 例4: 技術分類によるインポート

```
curl -X POST http://localhost:5000/import \
  -H "Content-Type: application/json" \
  -d '{"theme": "G06F"}'
```

#### 例5: 複数条件によるインポート

```
curl -X POST http://localhost:5000/import \
  -H "Content-Type: application/json" \
  -d '{
    "applicant": "Google",
    "theme": "G06F"
  }'
```

### J-PlatPat からの特許データのインポート

J-PlatPat（日本特許情報プラットフォーム）から特許情報を取得し、SQLite データベースに保存することができます。

#### 例1: 企業/出願人名による特許情報の取得

```
curl -X POST http://localhost:5000/import-jplatpat \
  -H "Content-Type: application/json" \
  -d '{
    "company": "トヨタ自動車",
    "limit": 10
  }'
```

#### 例2: 技術分類による特許情報の取得

```
curl -X POST http://localhost:5000/import-jplatpat \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "G06N",
    "limit": 20
  }'
```

#### 例3: キーワードによる特許情報の取得

```
curl -X POST http://localhost:5000/import-jplatpat \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "人工知能",
    "limit": 15
  }'
```

#### 例4: 複数条件による特許情報の取得

```
curl -X POST http://localhost:5000/import-jplatpat \
  -H "Content-Type: application/json" \
  -d '{
    "company": "本田技研工業",
    "keyword": "自動運転",
    "limit": 10
  }'
```

#### パラメータ説明

- `company`: 企業名/出願人名（部分一致）
- `theme`: 特許分類/テーマコード（部分一致）
- `keyword`: タイトルや概要に含まれるキーワード（部分一致）
- `limit`: 取得する特許データの最大数（デフォルト: 100）

#### J-PlatPat インポートのテスト

テスト用のスクリプトを使用して、J-PlatPat からのデータ取得機能をテストできます：

```
python test_jplatpat_import.py
```

このスクリプトは、トヨタ自動車の特許と「人工知能」をキーワードとする特許を取得するサンプル実行を行います。

### 特許データの検索

SQLite データベースから条件に合わせて特許を検索します。すべてのパラメータはオプションです。

- `patent_id`: 特許ID（完全一致）
- `publication_number`: 公開番号（完全一致）
- `applicant`: 出願人/譲受人名（部分一致）
- `theme`: 特許分類/テーマ（部分一致）
- `limit`: 返す結果の数（デフォルト: 100）
- `offset`: ページネーションオフセット（デフォルト: 0）

#### 例1: 特許IDでの検索

```
curl "http://localhost:5000/patents?patent_id=US12345678"
```

#### 例2: 公開番号での検索

```
curl "http://localhost:5000/patents?publication_number=US20200123456A1"
```

#### 例3: 出願人での検索

```
curl "http://localhost:5000/patents?applicant=Google"
```

#### 例4: 技術分類での検索

```
curl "http://localhost:5000/patents?theme=G06F"
```

#### 例5: 複数条件での検索とページネーション

```
curl "http://localhost:5000/patents?applicant=Google&theme=G06F&limit=50&offset=0"
```

## SQLiteによるデータの直接操作

SQLite データベースは `./data/patents.db` に保存されています。コンテナの外部からデータベースに直接アクセスして SQL クエリを実行することもできます。

### SQLiteを使用したデータ表示例

1. SQLite クライアントで接続:
   ```
   sqlite3 ./data/patents.db
   ```

2. テーブル情報の確認:
   ```sql
   .tables
   PRAGMA table_info(patents);
   ```

3. 基本的なデータの表示:
   ```sql
   -- 最近インポートされた特許を表示
   SELECT patent_id, publication_number, title 
   FROM patents 
   LIMIT 10;
   ```

4. 特定の出願人の特許数をカウント:
   ```sql
   SELECT applicant, COUNT(*) as patent_count 
   FROM patents 
   WHERE applicant LIKE '%Google%' 
   GROUP BY applicant;
   ```

5. 技術分類別の特許数:
   ```sql
   SELECT theme, COUNT(*) as count 
   FROM patents 
   GROUP BY theme 
   ORDER BY count DESC;
   ```

6. 年別の特許出願数:
   ```sql
   SELECT substr(filing_date, 1, 4) as year, 
          COUNT(*) as application_count 
   FROM patents 
   GROUP BY year 
   ORDER BY year DESC;
   ```

7. 特定の技術分野における主要出願人を特定:
   ```sql
   SELECT applicant, COUNT(*) as patent_count 
   FROM patents 
   WHERE theme LIKE 'G06F%' 
   GROUP BY applicant 
   ORDER BY patent_count DESC 
   LIMIT 10;
   ```

8. 出願人と発明者の共同分析:
   ```sql
   SELECT applicant, inventor, COUNT(*) as collaboration_count 
   FROM patents 
   GROUP BY applicant, inventor 
   HAVING COUNT(*) > 1 
   ORDER BY collaboration_count DESC;
   ```

## J-PlatPat 機能について

J-PlatPat（日本特許情報プラットフォーム）からの特許データインポート機能は、以下のような特徴があります：

### 主な機能

- 企業/出願人名での特許検索
- 特許分類（IPCコードなど）での特許検索
- キーワードによるタイトルおよび要約文の検索
- 検索結果のSQLiteデータベースへの自動保存
- 既存データとの重複排除および更新機能

### 検索パラメータの詳細

- **企業/出願人名検索** (`company`): 企業名や出願人名を指定して検索します。部分一致で検索されます。
  例: `トヨタ自動車`、`日立製作所`、`パナソニック`など

- **特許分類検索** (`theme`): IPC（国際特許分類）などの分類コードで検索します。
  例: `G06F`（コンピュータ）、`G06N`（AIや機械学習）、`H04L`（通信）など

- **キーワード検索** (`keyword`): 特許のタイトルや要約文に含まれるキーワードで検索します（曖昧検索対応）。
  例: `人工知能`（「人工知能システム」や「次世代人工知能」など部分一致も検索されます）、`自動運転`、`半導体`など

- **検索結果数制限** (`limit`): 取得する特許データの最大数を指定します。
  デフォルトは100件です。API呼び出しの負荷を考慮して適切な値を設定してください。

### インポート結果の確認

J-PlatPatからのインポート結果は以下の情報を含みます：

- 検索にマッチした特許の総数
- 新規インポートされた特許数
- 更新された既存特許数
- 取得された特許のサンプル（最大5件）

### エラーケースと対処法

- **API接続エラー**: J-PlatPatサービスに接続できない場合は、インターネット接続やAPIの稼働状況を確認してください。
- **検索結果なし**: 検索パラメータが厳しすぎる場合は、より一般的な用語やキーワードを使用してみてください。
- **レート制限**: 短時間に多数のリクエストを行うと、APIからレート制限がかかる場合があります。その場合は間隔を開けて再試行してください。

## トラブルシューティング

### BigQuery 関連の問題

BigQuery での認証問題が発生した場合：

1. サービスアカウントキーファイルが `service-key` ディレクトリに正しく配置されていることを確認します
2. サービスアカウントが BigQuery データセットにアクセスするために必要な権限を持っていることを確認します
3. 詳細なエラーメッセージについてはコンテナログを確認してください:
   ```
   # Docker の場合
   docker-compose logs
   
   # Podman の場合
   podman-compose logs
   ```

### J-PlatPat 関連の問題

J-PlatPat APIでの問題が発生した場合：

1. ネットワーク接続が正常であることを確認してください
2. J-PlatPat APIが正常に動作しているか確認してください
3. 認証情報（設定されている場合）が正しいことを確認してください
4. リクエスト制限に達していないか確認してください
5. 詳細なエラーログを確認するには以下のコマンドを実行してください:
   ```
   # Docker の場合
   docker-compose logs | grep "J-PlatPat"
   
   # Podman の場合
   podman-compose logs | grep "J-PlatPat"
   ```

## データストレージ

SQLite データベースは `./data` ディレクトリにボリュームとしてマウントされ、コンテナを停止しても保持されます。
