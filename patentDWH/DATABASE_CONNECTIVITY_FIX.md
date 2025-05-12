# MCPサーバとデータベース接続問題の修正について

## 問題の概要

MCPサーバからデータベースへのアクセスに問題があり、以下のようなエラーが発生していました：

```
ERROR - Error in API status: no such table: inpit_data
```

このエラーは、以下の原因から発生していました：

1. **欠落したテーブル**: `inpit_data` テーブルがデータベース内に存在しない
2. **データダウンロードの問題**: AWS S3からのデータダウンロードが失敗し、テーブルが正しく作成されていない
3. **ネットワーク接続の問題**: コンテナ間のネットワーク通信が正しく設定されていない

## 修正方法

この問題を解決するために、以下の2つのスクリプトが用意されました：

1. **`fix_database_connectivity.sh`**: データベース接続問題を修正し、必要なテーブルを作成するスクリプト
2. **`verify_database_fix.sh`**: 修正が正しく適用されたかを確認するためのスクリプト

### `fix_database_connectivity.sh` の主な機能

1. コンテナランタイム（podmanまたはdocker）を自動検出
2. 必要なネットワーク（`patentdwh_default`）の存在を確認し、必要に応じて作成
3. `inpit_data`テーブルをデータベース内に自動的に作成し、サンプルデータを挿入
4. テーブルに適切なインデックスを作成
5. データベースとMCPサーバ間の接続をテスト

### `verify_database_fix.sh` の主な機能

1. `inpit_data`テーブルの存在を確認
2. テーブル内のデータを確認
3. データベースAPIエンドポイントの機能をテスト
4. MCPコンテナからのデータベース接続をテスト
5. エラーが発生していた `/api/status` エンドポイントを確認

## 使用方法

### 初回のみ必要な手順

以下の手順は、データベース接続問題が発生した場合に**1度だけ**実行する必要があります：

1. すべてのサービスが実行中であることを確認します：
   ```bash
   cd /root/aws.git/patentDWH
   ./start_all_services.sh
   ```

2. データベース接続を修正します（**初回のみ**、または問題が再発した場合のみ必要）：
   ```bash
   ./fix_database_connectivity.sh
   ```

このスクリプトは、以下の作業を行います：
- `inpit_data` テーブルが存在しない場合に作成
- サンプルデータを挿入
- データベースに適切な権限を設定
- ネットワーク接続をテスト

通常のシステム運用では毎回実行する必要はありません。データベースがリセットされた場合、またはネットワーク接続問題が再発した場合にのみ再実行してください。

### 必要に応じて実行する手順

データベース接続が正しく機能しているかを確認するには：

```bash
./verify_database_fix.sh
```

## 問題が解決しない場合

修正を適用しても問題が解決しない場合は、以下の手順を試してください：

1. すべてのサービスを再起動します：
   ```bash
   cd /root/aws.git/patentDWH
   ./stop_all_services.sh
   ./start_all_services.sh
   ```

2. コンテナ間のネットワーク接続をテストします：
   ```bash
   cd /root/aws.git/patent_analysis_container
   ./test_container_connectivity.sh
   ```

3. 問題が特定できたら、再度 `fix_database_connectivity.sh` を実行します。

## 技術的な詳細

### テーブル構造

修正スクリプトは、以下の構造を持つ `inpit_data` テーブルを作成します：

```sql
CREATE TABLE IF NOT EXISTS inpit_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    open_patent_info_number TEXT,
    title TEXT,
    open_patent_info_registration_date TEXT,
    latest_update_date TEXT,
    application_number TEXT,
    application_date TEXT,
    applicant TEXT,
    publication_number TEXT,
    registration_number TEXT,
    patent_owner TEXT,
    invention_name TEXT,
    technical_field1 TEXT,
    technical_field2 TEXT,
    technical_field3 TEXT,
    function1 TEXT,
    function2 TEXT,
    function3 TEXT,
    applicable_products TEXT,
    purpose TEXT,
    effect TEXT,
    technical_overview TEXT,
    implementation_record_status TEXT,
    licensing_record_status TEXT,
    patent_right_transfer TEXT
)
```

### ネットワーク設定

正しいネットワーク設定は以下の通りです：

1. すべてのコンテナが `patentdwh_default` ネットワーク上にあること
2. コンテナ間でDNS名前解決ができること（例：`patentdwh-db`、`patentdwh-mcp-enhanced`）
3. 以下のポートが正しく設定されていること：
   - patentdwh-db: 5002
   - patentdwh-mcp-enhanced: 8080
   - patent-analysis-mcp: 8000
