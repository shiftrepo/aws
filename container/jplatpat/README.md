# J-PlatPat コンテナ化システム

このディレクトリには、J-PlatPat特許分析システムをコンテナ化するための設定ファイルが含まれています。
podmanとpodman-composeを利用してコンテナ化されたJ-PlatPatシステムを実行できます。

## 必要条件

- podman
- podman-compose

## 構成ファイル

- `Dockerfile`: J-PlatPatシステムのコンテナイメージを構築するための設定
- `podman-compose.yml`: サービスの定義とボリュームマウントの設定
- `entrypoint.sh`: コンテナ実行時のエントリポイントスクリプト
- `wrapper.py`: モジュールのインポート構造を調整するラッパー
- `fix-imports.sh`: コンテナ内でモジュールのインポートパスを修正するスクリプト
- `sql_query_tool.py`: SQLiteデータベースにクエリを実行するツール
- `sql.sh`: SQLクエリ実行のためのシェルスクリプト

## 使用方法

### コンテナのビルド

以下のコマンドでコンテナをビルドします：

```bash
cd container/jplatpat
podman-compose build
```

### コンテナの実行

#### ヘルプの表示

```bash
podman-compose run --rm jplatpat
```

#### データのインポート

##### 企業名による検索

```bash
podman-compose run --rm jplatpat import --company "トヨタ自動車" --limit 10
```

##### 技術分野による検索

```bash
podman-compose run --rm jplatpat import --technology "人工知能" --limit 5
```

##### キーワード検索

```bash
podman-compose run --rm jplatpat import --query "自動運転 AND センサー" --limit 3
```

##### 出願番号による検索

```bash
podman-compose run --rm jplatpat import --application "2003-101546,2022-100001"
```

##### 公開番号による検索

```bash
podman-compose run --rm jplatpat import --publication "JP2022-100000A,JP2022-100001A"
```

#### データの分析

##### 技術トレンド分析

```bash
podman-compose run --rm jplatpat analyze trend --years 5 --top-n 10
```

##### 出願者競争分析

```bash
podman-compose run --rm jplatpat analyze applicant --top-n 8
```

##### 特許ランドスケープ分析

```bash
podman-compose run --rm jplatpat analyze landscape --ipc-level 2
```

##### レポート生成

```bash
podman-compose run --rm jplatpat analyze report --output /data/my_report.md
```

#### SQLによるデータベース操作

##### テーブル一覧の表示

```bash
podman-compose run --rm jplatpat sql --tables
```

##### テーブルのスキーマ表示

```bash
podman-compose run --rm jplatpat sql --schema patents
```

##### テーブルの行数カウント

```bash
podman-compose run --rm jplatpat sql --count patents
```

##### SQLクエリの実行

```bash
podman-compose run --rm jplatpat sql -q "SELECT * FROM patents LIMIT 5"
```

##### 複雑なクエリの実行（ファイルから）

```bash
echo "SELECT p.title, a.name FROM patents p JOIN applicants a ON p.id = a.patent_id LIMIT 10" > query.sql
podman-compose run --rm -v $(pwd)/query.sql:/query.sql jplatpat sql -f /query.sql
```

##### 出力形式の指定

```bash
# CSV形式での出力
podman-compose run --rm jplatpat sql -q "SELECT * FROM patents LIMIT 5" --format csv

# JSON形式での出力
podman-compose run --rm jplatpat sql -q "SELECT * FROM patents LIMIT 5" --format json
```

##### 出力ファイルの保存

```bash
podman-compose run --rm jplatpat sql -q "SELECT * FROM patents" -o /data/results.csv --format csv
```

#### データベースのリセット

```bash
podman-compose run --rm jplatpat reset --force
```

### データの永続化

特許データベースは、`jplatpat-data`という名前のボリュームに保存されます。
このボリュームは、コンテナが削除されても維持されます。

### データへのアクセス

データベースファイルは、コンテナ内の`/data/patents.db`に保存されています。
必要に応じて、このパスをホスト上の別のパスにマウントすることも可能です。

```bash
# カスタムパスへのマウント例
podman run --rm -v /path/on/host:/data jplatpat-image import --company "トヨタ自動車" --limit 10
```

## カスタマイズ

`podman-compose.yml`ファイルを編集することで、ポート番号やマウントポイントなどの設定をカスタマイズできます。
