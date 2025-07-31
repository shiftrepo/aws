# category_name カラム変更影響分析レポート

## 概要
このレポートは、Neo4j GraphDB を使用して `category_name` カラムの物理名またはデータ型変更が既存システムに与える影響を詳細に分析した結果をまとめたものです。

## 分析対象
- **対象カラム**: `category_name`
- **所属テーブル**: `categories` (ec_site スキーマ)
- **現在のデータ型**: `VARCHAR2(100)`
- **NULL 許可**: `NOT NULL`
- **制約**: なし（Primary Key、Foreign Key ではない）

## 影響度評価

### 総合影響度: **中程度 (MEDIUM)**

| 評価項目 | 影響度 | 詳細 |
|----------|--------|------|
| アプリケーション影響 | 低 (LOW) | 1つのアプリケーションのみが直接依存 |
| CRUD操作影響 | 低 (LOW) | 直接的なCRUD操作は現在未検出 |
| 関連テーブル影響 | 中 (MEDIUM) | 2つの外部キー関係が存在 |

## 詳細分析結果

### 1. カラム詳細情報
```
カラム名: category_name
データ型: VARCHAR2(100)
NULL許可: NOT NULL
デフォルト値: なし
所属テーブル: categories (ec_site.categories)
```

### 2. 影響を受けるアプリケーション

#### product_operations アプリケーション
- **言語**: C
- **フレームワーク**: MySQL/C
- **バージョン**: 1.0
- **影響度**: **高 (HIGH)**
- **影響内容**: categories テーブルに直接アクセスしているため、category_name カラムの変更により修正が必要

### 3. 外部キー関係と連鎖影響

#### 3.1 products テーブルとの関係
- **制約名**: `fk_products_category`
- **関係**: `products.category_id` → `categories.category_id`
- **連鎖タイプ**: RESTRICT
- **関係タイプ**: many-to-one
- **影響度**: **高 (HIGH)**
- **影響内容**: 
  - products テーブルからのJOIN操作でcategory_nameを参照している可能性
  - 商品マスタの表示・検索機能に影響の可能性

#### 3.2 categories テーブル自己参照
- **制約名**: `fk_categories_parent`
- **関係**: `categories.parent_category_id` → `categories.category_id`
- **連鎖タイプ**: RESTRICT
- **関係タイプ**: one-to-many
- **影響度**: **中 (MEDIUM)**
- **影響内容**: 
  - カテゴリー階層構造の表示処理に影響
  - 親カテゴリー名の表示ロジックに影響

### 4. 関連テーブル分析

#### 4.1 products テーブル
- **スキーマ**: ec_site
- **テーブルタイプ**: master
- **業務重要度**: high
- **影響**: カテゴリー名を使用した商品検索・表示機能

#### 4.2 categories テーブル（自己参照）
- **スキーマ**: ec_site
- **テーブルタイプ**: reference
- **業務重要度**: medium
- **影響**: 階層カテゴリー表示機能

## 想定される変更シナリオと影響

### シナリオ1: カラム名変更 (category_name → category_display_name)

#### 必要な修正内容
1. **DDL修正**
   ```sql
   ALTER TABLE ec_site.categories 
   RENAME COLUMN category_name TO category_display_name;
   ```

2. **アプリケーション修正**
   - product_operations アプリケーションのC言語コード
   - category_name を参照しているすべてのSQL文
   - 構造体メンバー名の変更

3. **予想される影響箇所**
   - カテゴリー一覧表示機能
   - 商品検索時のカテゴリー名表示
   - 階層カテゴリー表示機能

### シナリオ2: データ型変更 (VARCHAR2(100) → VARCHAR2(200))

#### 必要な修正内容
1. **DDL修正**
   ```sql
   ALTER TABLE ec_site.categories 
   MODIFY category_name VARCHAR2(200);
   ```

2. **アプリケーション修正**
   - C言語の文字列バッファサイズ修正
   - データベース接続時の列定義修正

3. **予想される影響箇所**
   - データバインド処理
   - 文字列長チェック処理
   - 表示画面の項目幅

## 推奨テストシナリオ

### 1. 外部キー制約テスト
- **テスト名**: Foreign Key Constraint Test
- **対象**: fk_products_category, fk_categories_parent
- **テスト内容**: 
  - 参照整合性の確認
  - 制約違反時の動作確認
  - カスケード動作の確認
- **優先度**: **高**

### 2. アプリケーション統合テスト
- **テスト名**: Application Integration Test
- **対象**: product_operations アプリケーション
- **テスト内容**:
  - categories テーブルアクセス機能
  - カテゴリー名表示機能
  - 検索・フィルタリング機能
- **優先度**: **高**

### 3. 関連テーブル影響テスト
- **テスト名**: Related Table Impact Test
- **対象**: products テーブル
- **テスト内容**:
  - JOIN操作の動作確認
  - 商品-カテゴリー関連表示
  - 階層カテゴリー表示
- **優先度**: **中**

## 変更実施時の推奨手順

### 1. 事前準備
1. 現在のデータベース状態のバックアップ
2. 影響範囲の最終確認
3. テスト環境での動作確認

### 2. 変更実施順序
1. **第1段階**: テスト環境でのDDL変更
2. **第2段階**: アプリケーションコードの修正
3. **第3段階**: 統合テストの実行
4. **第4段階**: 本番環境への適用

### 3. 変更後の検証
1. 外部キー制約の動作確認
2. アプリケーション機能の動作確認
3. 性能影響の確認
4. データ整合性の確認

## リスク評価と対策

### 高リスク項目
1. **product_operations アプリケーションの停止**
   - 対策: 段階的な変更実施とロールバック計画
   
2. **外部キー制約違反**
   - 対策: 事前の制約確認と整合性チェック

### 中リスク項目
1. **階層カテゴリー表示の不具合**
   - 対策: 階層構造の表示ロジック検証

2. **商品検索機能の影響**
   - 対策: 検索機能の網羅的テスト

## 推奨Cypherクエリ（追加分析用）

### 1. CRUD操作の詳細分析
```cypher
MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table {name: 'categories'})
RETURN crud.operation_type as operation_type,
       crud.function_name as function_name,
       crud.file_path as file_path,
       crud.line_number as line_number,
       crud.complexity as complexity
ORDER BY crud.operation_type, crud.function_name
```

### 2. 高依存度アプリケーションの特定
```cypher
MATCH (app:Application)-[:USES]->(table:Table {name: 'categories'})
MATCH (app)-[:IMPLEMENTS]->(crud:CRUDOperation)-[:TARGETS]->(table)
RETURN app.name as application,
       app.language as language,
       count(crud) as crud_count,
       collect(DISTINCT crud.operation_type) as operations
ORDER BY crud_count DESC
```

### 3. 外部キー連鎖影響の分析
```cypher
MATCH (table1:Table)-[ref:REFERENCES]->(table2:Table)
WHERE table1.name = 'categories' OR table2.name = 'categories'
RETURN table1.name as source_table,
       table2.name as target_table,
       ref.constraint_name as constraint_name,
       ref.cascade_type as cascade_type,
       ref.relationship_type as relationship_type
```

## 結論

`category_name` カラムの変更は**中程度の影響**を与えると評価されます。主な影響は：

1. **product_operations アプリケーション**への直接的な影響
2. **products テーブル**との外部キー関係による間接的な影響
3. **categories テーブル**の自己参照による階層構造への影響

変更を実施する際は、段階的なアプローチを取り、十分なテストを実施することを強く推奨します。特に外部キー制約とアプリケーション統合部分については重点的な検証が必要です。

## 分析実施日時
**実施日**: 2025年7月31日  
**分析ツール**: Neo4j GraphDB (バージョン確認済み)  
**データソース**: 本番データベーススキーマ分析結果