# ECサイトサンプルアプリケーション

このプロジェクトは、C言語で実装されたシンプルなECサイトのサンプルアプリケーションです。MySQLデータベースを使用し、ユーザー管理、商品管理、注文管理、カート管理の基本的なCRUD操作を提供します。

## ディレクトリ構成

```
sample/
├── src/                    # C言語ソースコード
│   ├── main.c             # メインプログラム
│   ├── database.h/c       # データベース接続・基本操作
│   ├── user_operations.h/c # ユーザー関連操作
│   ├── product_operations.h/c # 商品関連操作
│   ├── order_operations.h/c   # 注文関連操作
│   ├── cart_operations.h/c    # カート関連操作
│   └── Makefile          # ビルド設定
├── ddl/                   # データベース定義
│   ├── create_tables.sql  # テーブル作成DDL
│   └── sample_data.sql    # サンプルデータ
└── README.md             # このファイル
```

## データベース設計

### 主要テーブル
- `users`: ユーザー情報
- `categories`: 商品カテゴリ
- `products`: 商品情報
- `addresses`: 住所情報
- `orders`: 注文情報
- `order_items`: 注文詳細
- `cart_items`: ショッピングカート
- `reviews`: 商品レビュー

## 機能概要

### 実装済み機能
- **ユーザー管理**: CRUD操作、認証機能
- **商品管理**: CRUD操作、カテゴリ別検索、価格帯検索、在庫管理
- **注文管理**: 注文作成・更新・削除、ステータス管理、注文詳細管理
- **カート管理**: 商品追加・削除・更新、合計金額計算

### CRUD操作マトリックス
各テーブルに対して以下のCRUD操作が実装されています：

| テーブル | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| users | ✓ | ✓ | ✓ | ✓ |
| products | ✓ | ✓ | ✓ | ✓ |
| orders | ✓ | ✓ | ✓ | ✓ |
| order_items | ✓ | ✓ | ✓ | ✓ |
| cart_items | ✓ | ✓ | ✓ | ✓ |
| categories | - | - | - | - |
| addresses | - | - | - | - |
| reviews | - | - | - | - |

## セットアップ

### 1. データベースセットアップ（Oracle）
```sql
-- テーブルスペース作成（オプション）
CREATE TABLESPACE EC_SITE_DATA
DATAFILE 'ec_site_data.dbf' SIZE 100M
AUTOEXTEND ON NEXT 10M MAXSIZE 1G;

-- ユーザー作成
CREATE USER ec_site IDENTIFIED BY password
DEFAULT TABLESPACE EC_SITE_DATA;

GRANT CONNECT, RESOURCE TO ec_site;
GRANT CREATE TABLE, CREATE INDEX, CREATE SEQUENCE TO ec_site;

-- テーブル作成（番号順に実行）
-- ec_siteユーザーで接続後実行
@ddl/01_users.sql
@ddl/02_categories.sql
@ddl/03_products.sql
@ddl/04_addresses.sql
@ddl/05_orders.sql
@ddl/06_order_items.sql
@ddl/07_cart_items.sql
@ddl/08_reviews.sql
@ddl/99_indexes.sql

-- サンプルデータ投入
@ddl/sample_data.sql
```

### 1-2. データベースセットアップ（MySQL）
```sql
-- データベース作成
CREATE DATABASE ec_site CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- テーブル作成（統合ファイルを使用）
mysql -u root -p ec_site < ddl/create_tables.sql

-- サンプルデータ投入
mysql -u root -p ec_site < ddl/sample_data.sql
```

### 2. 依存関係インストール
```bash
cd sample/src
make install-deps
```

### 3. ビルド
```bash
make
```

### 4. 実行
```bash
make run
```

## 設定

`src/database.h`でデータベース接続設定を変更できます：

```c
#define DB_HOST "localhost"
#define DB_USER "root"
#define DB_PASSWORD "password"
#define DB_NAME "ec_site"
```

## 使用技術
- **言語**: C言語 (C99標準)
- **データベース**: Oracle Database / MySQL
- **ライブラリ**: MySQL C API (libmysqlclient) / Oracle Call Interface (OCI)

### DDL形式
- **Oracle形式**: 各テーブルファイル（01_users.sql～99_indexes.sql）はOracle Database用
- **MySQL形式**: create_tables.sql（統合ファイル）はMySQL用

## 注意事項
- このサンプルは学習・テスト目的で作成されています
- 本番環境での使用は推奨されません
- セキュリティ対策（SQLインジェクション対策など）は簡素化されています
- エラーハンドリングは最小限の実装です