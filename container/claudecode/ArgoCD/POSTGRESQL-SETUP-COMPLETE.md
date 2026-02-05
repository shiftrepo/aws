# ✅ PostgreSQL 外部接続設定完了

## 🎉 設定完了！

PostgreSQLがどこからでも接続できるように設定されました。
**セキュリティ制限は完全に無効化されています。**

---

## 📊 現在の状態

| 項目 | 値 | 状態 |
|------|-----|------|
| **PostgreSQLバージョン** | 16.11 | ✅ 起動中 |
| **コンテナ名** | orgmgmt-postgres | ✅ Healthy |
| **リスニングアドレス** | `*` (全てのIP) | ✅ 設定済み |
| **ポート** | 5432 (0.0.0.0) | ✅ 公開中 |
| **認証方式** | trust (パスワード不要) | ✅ 設定済み |
| **最大接続数** | 200 | ✅ 設定済み |

---

## 🔌 接続情報

### 基本情報

```
ホスト:         localhost (ローカル) または ホストのIPアドレス
ポート:         5432
データベース:   postgres または orgmgmt
ユーザー名:     orgmgmt_user
パスワード:     SecurePassword123! (trustモードのため認証なしでも接続可)
```

### 接続文字列

```
# ローカルから
postgresql://orgmgmt_user:SecurePassword123!@localhost:5432/postgres
postgresql://orgmgmt_user:SecurePassword123!@localhost:5432/orgmgmt

# 外部から（ホストのIPが192.168.1.100の場合）
postgresql://orgmgmt_user:SecurePassword123!@192.168.1.100:5432/postgres
```

---

## 💻 接続コマンド例

### psqlコマンドライン

```bash
# ローカルから接続
psql -h localhost -p 5432 -U orgmgmt_user -d postgres

# パスワード付き（trustモードでは不要だが指定可能）
PGPASSWORD=SecurePassword123! psql -h localhost -p 5432 -U orgmgmt_user -d postgres

# 外部から接続（ホストのIPを指定）
psql -h <HOST_IP> -p 5432 -U orgmgmt_user -d postgres
```

### コンテナ内から

```bash
# コンテナ内でpsql実行
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d postgres

# コンテナ内でSQLクエリ実行
podman exec orgmgmt-postgres psql -U orgmgmt_user -d postgres -c "SELECT version();"
```

---

## 🌍 外部ネットワークからの接続

### 1. ホストのIPアドレスを確認

```bash
# 現在のIPアドレスを確認
hostname -I

# または
ip addr show
```

### 2. ファイアウォール設定（必要な場合）

```bash
# RHEL/Rocky Linux 9
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload

# 確認
sudo firewall-cmd --list-ports
```

### 3. 別のマシンから接続テスト

```bash
# ホストのIPが192.168.1.100の場合
psql -h 192.168.1.100 -p 5432 -U orgmgmt_user -d postgres

# 接続テスト（nc/netcatを使用）
nc -zv 192.168.1.100 5432
```

---

## 🔧 プログラミング言語別の接続例

### Python (psycopg2)

```python
import psycopg2

# ローカル接続
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="orgmgmt_user",
    password="SecurePassword123!"
)

# 外部接続（IPを指定）
conn = psycopg2.connect(
    host="192.168.1.100",
    port=5432,
    database="postgres",
    user="orgmgmt_user",
    password="SecurePassword123!"
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
conn.close()
```

### Java (JDBC)

```java
String url = "jdbc:postgresql://localhost:5432/postgres";
// または外部から: "jdbc:postgresql://192.168.1.100:5432/postgres";
String user = "orgmgmt_user";
String password = "SecurePassword123!";

Connection conn = DriverManager.getConnection(url, user, password);
System.out.println("接続成功！");
conn.close();
```

### Node.js (pg)

```javascript
const { Client } = require('pg');

const client = new Client({
    host: 'localhost',  // または '192.168.1.100'
    port: 5432,
    database: 'postgres',
    user: 'orgmgmt_user',
    password: 'SecurePassword123!'
});

await client.connect();
console.log('接続成功！');
await client.end();
```

### Go (lib/pq)

```go
connStr := "host=localhost port=5432 user=orgmgmt_user password=SecurePassword123! dbname=postgres sslmode=disable"
// または外部から: "host=192.168.1.100 port=5432 ..."

db, _ := sql.Open("postgres", connStr)
defer db.Close()

_ = db.Ping()
fmt.Println("接続成功！")
```

---

## 🔍 設定詳細

### podman-compose.yml設定

```yaml
postgres:
  image: docker.io/library/postgres:16-alpine
  container_name: orgmgmt-postgres
  environment:
    POSTGRES_HOST_AUTH_METHOD: trust  # 認証なし
  ports:
    - "0.0.0.0:5432:5432"  # 全インターフェースで公開
  command: >
    postgres
    -c listen_addresses='*'     # 全IPから接続許可
    -c max_connections=200      # 最大接続数
    -c log_connections=on       # 接続ログ
    -c log_disconnections=on    # 切断ログ
```

### 実際のPostgreSQL設定

```bash
# 設定確認
podman exec orgmgmt-postgres psql -U orgmgmt_user -d postgres -c "SHOW listen_addresses;"
# 結果: *

podman exec orgmgmt-postgres psql -U orgmgmt_user -d postgres -c "SHOW max_connections;"
# 結果: 200
```

---

## ✅ 動作確認済み

以下の接続方法が動作確認済みです:

- ✅ ローカルホストからの接続 (localhost:5432)
- ✅ 同一マシン内の他のコンテナからの接続
- ✅ 同一ネットワーク内の別マシンからの接続
- ✅ コンテナ名での接続 (Docker/Podmanネットワーク内)
- ✅ パスワードなし接続 (trustモード)
- ✅ パスワード付き接続 (任意)

---

## 🛠️ トラブルシューティング

### 接続できない場合

#### 1. PostgreSQLが起動しているか確認

```bash
podman ps | grep postgres
# 期待される出力: orgmgmt-postgres  Up X minutes (healthy)
```

#### 2. ポートがリスニングしているか確認

```bash
ss -tlnp | grep 5432
# 期待される出力: LISTEN ... *:5432 ...
```

#### 3. ファイアウォールを確認

```bash
sudo firewall-cmd --list-ports
# 5432/tcp が含まれているか確認
```

#### 4. 接続テスト

```bash
# ポート到達性テスト
nc -zv localhost 5432

# PostgreSQL接続テスト
podman exec orgmgmt-postgres pg_isready -U orgmgmt_user
```

#### 5. ログ確認

```bash
# PostgreSQLログ
podman logs orgmgmt-postgres

# 最新のログのみ
podman logs --tail 50 orgmgmt-postgres
```

---

## 📝 重要な注意事項

### ⚠️ セキュリティについて

この設定は**開発・テスト環境専用**です:

- ❌ 認証なしで誰でも接続可能
- ❌ 全てのIPアドレスから接続可能
- ❌ 暗号化なし (SSL/TLS無効)
- ❌ 全データベース・全ユーザーへのアクセス可能

**本番環境では絶対に使用しないでください！**

### ✅ 開発環境での利点

- ✅ どこからでも簡単に接続可能
- ✅ 認証設定不要
- ✅ クイックプロトタイピングに最適
- ✅ デバッグが容易

---

## 🎯 次のステップ

1. **データベース初期化**
   ```bash
   # Flywayマイグレーションを実行
   cd /root/aws.git/container/claudecode/ArgoCD
   # または手動でSQLを実行
   podman exec -i orgmgmt-postgres psql -U orgmgmt_user -d postgres < infrastructure/config/postgres/init.sql
   ```

2. **アプリケーション接続設定**
   - Spring Boot application.yml で接続文字列を設定
   - フロントエンドAPIクライアントで接続

3. **他のインフラサービスを起動**
   ```bash
   cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
   podman-compose up -d
   ```

---

## 📚 関連ドキュメント

- [POSTGRESQL-EXTERNAL-ACCESS.md](./POSTGRESQL-EXTERNAL-ACCESS.md) - 詳細な外部アクセス設定ガイド
- [README.md](../README.md) - プロジェクト全体のドキュメント
- [infrastructure/README.md](./README.md) - インフラストラクチャのドキュメント

---

## 🎉 まとめ

PostgreSQLは**完全にオープン**で設定されています:

| 機能 | 状態 |
|------|------|
| 外部接続 | ✅ 有効 |
| 認証 | ❌ 無効 (trust) |
| 暗号化 | ❌ 無効 |
| IPアドレス制限 | ❌ 無効 |
| ポート公開 | ✅ 0.0.0.0:5432 |

**どこからでも制限なく接続できます！**

---

**最終更新**: 2026-02-05
**PostgreSQLバージョン**: 16.11
**状態**: ✅ 稼働中・外部接続可能
