# PostgreSQL 外部アクセス設定

## 概要

このプロジェクトでは、PostgreSQLをどこからでも接続できるように設定しています。
**セキュリティ制限は無効化されています。**

## 設定内容

### 1. ネットワーク設定

- **リスニングアドレス**: `*` (全てのIPアドレスから接続可能)
- **ポート**: `5432` (ホストの全インターフェースで公開)
- **認証方式**: `trust` (パスワード不要、全て許可)

### 2. 設定ファイル

#### postgresql.conf
```
listen_addresses = '*'
port = 5432
max_connections = 100
```

場所: `/root/aws.git/container/claudecode/ArgoCD/infrastructure/config/postgres/postgresql.conf`

#### pg_hba.conf
全てのホストからの接続を許可:
```
host    all    all    0.0.0.0/0      trust
host    all    all    ::/0           trust
```

場所: `/root/aws.git/container/claudecode/ArgoCD/infrastructure/config/postgres/pg_hba.conf`

### 3. Podman設定

```yaml
ports:
  - "0.0.0.0:5432:5432"  # 全インターフェースで公開
environment:
  POSTGRES_HOST_AUTH_METHOD: trust
command: >
  postgres
  -c listen_addresses='*'
```

## 接続方法

### 1. ローカルホストから接続

```bash
# psqlコマンド
psql -h localhost -p 5432 -U orgmgmt_user -d orgmgmt

# コンテナ内から接続
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt
```

### 2. 同一ネットワーク内の別マシンから接続

```bash
# ホストのIPアドレスを確認
hostname -I

# 別マシンから接続（例: ホストのIPが 192.168.1.100 の場合）
psql -h 192.168.1.100 -p 5432 -U orgmgmt_user -d orgmgmt
```

### 3. インターネット経由での接続

**前提条件:**
- ホストのファイアウォールでポート5432を開放
- ルーターでポートフォワーディング設定（必要な場合）

```bash
# パブリックIPまたはDNSで接続
psql -h <your-public-ip> -p 5432 -U orgmgmt_user -d orgmgmt
```

## ファイアウォール設定

### RHEL/Rocky Linux 9の場合

```bash
# PostgreSQLポートを開放
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload

# 確認
sudo firewall-cmd --list-ports
```

### iptablesの場合

```bash
# ルールを追加
sudo iptables -A INPUT -p tcp --dport 5432 -j ACCEPT

# 永続化
sudo iptables-save > /etc/iptables/rules.v4
```

## 接続情報

| 項目 | 値 |
|------|-----|
| **ホスト** | localhost（ローカル）または ホストのIP |
| **ポート** | 5432 |
| **データベース** | orgmgmt |
| **ユーザー名** | orgmgmt_user |
| **パスワード** | SecurePassword123! |
| **接続文字列** | postgresql://orgmgmt_user:SecurePassword123!@localhost:5432/orgmgmt |

## プログラミング言語別の接続例

### Python (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="orgmgmt",
    user="orgmgmt_user",
    password="SecurePassword123!"
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
version = cursor.fetchone()
print(f"PostgreSQL version: {version}")

conn.close()
```

### Java (JDBC)

```java
import java.sql.*;

public class PostgreSQLConnection {
    public static void main(String[] args) {
        String url = "jdbc:postgresql://localhost:5432/orgmgmt";
        String user = "orgmgmt_user";
        String password = "SecurePassword123!";

        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            System.out.println("Connected to PostgreSQL!");
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

### Node.js (pg)

```javascript
const { Client } = require('pg');

const client = new Client({
    host: 'localhost',
    port: 5432,
    database: 'orgmgmt',
    user: 'orgmgmt_user',
    password: 'SecurePassword123!'
});

client.connect()
    .then(() => console.log('Connected to PostgreSQL'))
    .then(() => client.query('SELECT version()'))
    .then(result => console.log(result.rows[0]))
    .finally(() => client.end());
```

### Go (lib/pq)

```go
package main

import (
    "database/sql"
    "fmt"
    _ "github.com/lib/pq"
)

func main() {
    connStr := "host=localhost port=5432 user=orgmgmt_user password=SecurePassword123! dbname=orgmgmt sslmode=disable"
    db, err := sql.Open("postgres", connStr)
    if err != nil {
        panic(err)
    }
    defer db.Close()

    err = db.Ping()
    if err != nil {
        panic(err)
    }
    fmt.Println("Connected to PostgreSQL!")
}
```

## テストツール

### DBeaver
1. 新規接続 → PostgreSQL
2. ホスト: localhost（またはホストIP）
3. ポート: 5432
4. データベース: orgmgmt
5. ユーザー: orgmgmt_user
6. パスワード: SecurePassword123!

### pgAdmin
すでに含まれています: http://localhost:5050

### DataGrip (JetBrains)
1. 新規データソース → PostgreSQL
2. 接続情報を入力
3. Test Connection

## トラブルシューティング

### 接続できない場合

1. **PostgreSQLが起動しているか確認**
   ```bash
   podman ps | grep postgres
   ```

2. **ポートがリッスンしているか確認**
   ```bash
   sudo ss -tlnp | grep 5432
   # または
   sudo netstat -tlnp | grep 5432
   ```

3. **ファイアウォールを確認**
   ```bash
   sudo firewall-cmd --list-ports
   ```

4. **ログを確認**
   ```bash
   podman logs orgmgmt-postgres
   ```

5. **設定を確認**
   ```bash
   # コンテナ内で確認
   podman exec -it orgmgmt-postgres cat /etc/postgresql/postgresql.conf | grep listen_addresses
   podman exec -it orgmgmt-postgres cat /var/lib/postgresql/data/pg_hba.conf
   ```

### 接続は成功するがデータベースが見つからない場合

```bash
# データベース一覧を確認
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -c "\l"

# データベースを手動作成
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -c "CREATE DATABASE orgmgmt;"
```

## セキュリティに関する注意

**このプロジェクトではセキュリティ考慮は不要と指定されていますが、本番環境では以下を推奨します:**

- ❌ `trust`認証は使用しない → ✅ `md5`または`scram-sha-256`を使用
- ❌ `0.0.0.0/0`での接続許可 → ✅ 特定IPレンジのみ許可
- ❌ デフォルトパスワード → ✅ 強力なパスワードを使用
- ❌ 暗号化なし → ✅ SSL/TLS接続を使用
- ❌ 全データベース・全ユーザー許可 → ✅ 最小権限の原則

## まとめ

現在の設定では、PostgreSQLは **完全にオープン** で、どこからでも制限なく接続できます:

✅ 全てのIPアドレスから接続可能
✅ パスワード認証不要（trustモード）
✅ 全データベース・全ユーザーへのアクセス可能
✅ ファイアウォール開放で外部ネットワークからも接続可能

**開発・テスト環境専用の設定です。**
