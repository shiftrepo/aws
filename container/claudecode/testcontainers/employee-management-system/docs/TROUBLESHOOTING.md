# トラブルシューティングガイド - 職員管理システム

よくある問題、パフォーマンスの問題、デバッグ技術の包括的なトラブルシューティングガイドです。

## 🚨 迅速な診断

### システムヘルスチェック
```bash
#!/bin/bash
# 迅速なヘルスチェックスクリプト

echo "=== 職員管理システム ヘルスチェック ==="
echo

echo "1. コンテナ状態を確認中..."
podman-compose ps

echo -e "\n2. データベース接続を確認中..."
podman-compose exec postgres pg_isready -U postgres -d employee_db

echo -e "\n3. アプリケーションの稼働状況を確認中..."
curl -s http://localhost:8080/actuator/health | jq '.' || echo "アプリケーションが応答していません"

echo -e "\n4. ディスク容量を確認中..."
df -h

echo -e "\n5. メモリ使用量を確認中..."
free -h

echo -e "\n6. コンテナログのエラーを確認中..."
podman-compose logs --tail=10 postgres | grep -i error || echo "PostgreSQLエラーなし"
podman-compose logs --tail=10 app | grep -i error || echo "アプリケーションエラーなし"

echo -e "\nヘルスチェック完了！"
```

## 🔧 コンテナの問題

### コンテナが起動しない

#### 症状
```bash
$ podman-compose up -d
ERROR: Service 'postgres' failed to build
```

#### 診断
```bash
# ポートが既に使用されているかを確認
sudo netstat -tulpn | grep -E ':5432|:8080|:5050'

# 利用可能なシステムリソースを確認
df -h
free -h

# 競合するコンテナを確認
podman ps -a
podman container list --all
```

#### 解決方法

**ポート競合:**
```bash
# オプション1: 競合するサービスを停止
sudo systemctl stop postgresql
sudo killall -9 postgres

# オプション2: podman-compose.ymlでポートを変更
# postgresサービスを編集:
services:
  postgres:
    ports:
      - "5433:5432"  # ホストポートを変更
```

**リソース不足:**
```bash
# ディスク容量を確保
podman system prune -a
podman volume prune -f

# メモリを解放
sudo systemctl restart docker  # またはpodman
```

**権限の問題:**
```bash
# ファイル権限を修正
sudo chown -R $USER:$USER .
chmod +x docker/postgres/init.sql

# SELinuxの問題を修正（該当する場合）
sudo setsebool -P container_manage_cgroup true
```

### コンテナが再起動を繰り返す

#### 症状
```bash
$ podman-compose ps
NAME              STATUS
employee_postgres 再起動中...
```

#### 診断
```bash
# コンテナログを確認
podman-compose logs postgres
podman-compose logs app

# コンテナリソース制限を確認
podman stats $(podman-compose ps -q)

# OOMキルを確認
dmesg | grep -i "killed process"
```

#### 解決方法

**メモリの問題:**
```yaml
# podman-compose.ymlでメモリ制限を増加
services:
  postgres:
    mem_limit: 1g
    memswap_limit: 1g
  app:
    mem_limit: 2g
    memswap_limit: 2g
```

**データベース破損:**
```bash
# 破損したデータベースボリュームを削除
podman-compose down -v
podman volume rm $(podman volume ls -q | grep postgres)
podman-compose up -d
```

**設定の問題:**
```bash
# デフォルト設定にリセット
git checkout -- podman-compose.yml
git checkout -- .env
podman-compose up -d
```

## 🗄️ データベースの問題

### 接続の問題

#### 症状
```
org.postgresql.util.PSQLException: Connection to localhost:5432 refused
```

#### 診断
```bash
# PostgreSQLコンテナが実行中かを確認
podman-compose ps postgres

# データベース接続をテスト
podman-compose exec postgres pg_isready -U postgres

# データベースログを確認
podman-compose logs postgres | tail -20

# アプリケーションコンテナからの接続をテスト
podman-compose exec app nc -zv postgres 5432
```

#### 解決方法

**コンテナが実行されていない:**
```bash
# PostgreSQLサービスを再起動
podman-compose restart postgres

# 起動エラーを確認
podman-compose logs postgres
```

**間違った接続パラメータ:**
```bash
# application.ymlの接続パラメータを確認
podman-compose exec app cat src/main/resources/application.yml | grep -A 5 datasource

# 正しいパラメータでテスト
podman-compose exec app psql -h postgres -p 5432 -U postgres -d employee_db
```

**ネットワークの問題:**
```bash
# コンテナネットワークを確認
podman network ls
podman network inspect $(podman-compose ps -q | head -1)

# ネットワークを再作成
podman-compose down
podman network prune -f
podman-compose up -d
```

### データベースパフォーマンスの問題

#### 症状
クエリ実行の遅延、タイムアウト、またはCPU使用率の上昇。

#### 診断
```bash
# データベースパフォーマンス統計を確認
podman-compose exec postgres psql -U postgres -d employee_db -c "
  SELECT * FROM pg_stat_activity WHERE state = 'active';
"

# 遅いクエリを確認
podman-compose exec postgres psql -U postgres -d employee_db -c "
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  ORDER BY total_time DESC LIMIT 10;
"

# データベースサイズとテーブル統計を確認
podman-compose exec postgres psql -U postgres -d employee_db -c "
  SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
  FROM pg_stat_user_tables;
"
```

#### 解決方法

**クエリの最適化:**
```sql
-- 不足しているインデックスを追加
CREATE INDEX IF NOT EXISTS idx_employees_email ON employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_department_active ON employees(department_id, active);
CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON employees(hire_date);

-- クエリパフォーマンスを分析
EXPLAIN ANALYZE SELECT * FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.active = true;
```

**データベース設定:**
```bash
# 共有メモリを増加（podman-compose.ymlで）
services:
  postgres:
    command: >
      postgres
      -c shared_preload_libraries=pg_stat_statements
      -c shared_buffers=256MB
      -c max_connections=100
      -c work_mem=4MB
```

**コネクションプールの調整:**
```yaml
# application.ymlで
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
```

### データ破損または不整合

#### 症状
- 外部キー制約違反
- 予期しないNULL値
- レコードの欠損または重複

#### 診断
```bash
# データベースの整合性を確認
podman-compose exec postgres psql -U postgres -d employee_db -c "
  -- 孤立した職員を確認
  SELECT e.id, e.email, e.department_id
  FROM employees e
  LEFT JOIN departments d ON e.department_id = d.id
  WHERE e.department_id IS NOT NULL AND d.id IS NULL;
"

# 制約違反を確認
podman-compose exec postgres psql -U postgres -d employee_db -c "
  -- メールの一意性を確認
  SELECT email, COUNT(*)
  FROM employees
  GROUP BY email
  HAVING COUNT(*) > 1;
"
```

#### 解決方法

**孤立したレコードの修正:**
```sql
-- オプション1: 孤立した職員を削除
DELETE FROM employees
WHERE department_id NOT IN (SELECT id FROM departments);

-- オプション2: 孤立した職員の部署をNULLに設定
UPDATE employees
SET department_id = NULL
WHERE department_id NOT IN (SELECT id FROM departments);
```

**データベースのリセット:**
```bash
# 完全なデータベースリセット（全データが削除されます）
podman-compose down -v
podman volume rm $(podman volume ls -q | grep postgres)
podman-compose up -d

# 初期化を待機
sleep 30
podman-compose logs postgres | grep "ready to accept connections"
```

## ☕ アプリケーションの問題

### アプリケーションが起動しない

#### 症状
```
Error starting ApplicationContext
```

#### 診断
```bash
# アプリケーションログを確認
podman-compose logs app | tail -50

# Javaバージョンと環境を確認
podman-compose exec app java -version
podman-compose exec app env | grep -E 'JAVA|SPRING'

# 不足した依存関係を確認
podman-compose exec app mvn dependency:tree | grep -i missing
```

#### 解決方法

**Maven依存関係:**
```bash
# クリーンとリビルド
podman-compose exec app mvn clean install -DskipTests

# 依存関係を更新
podman-compose exec app mvn versions:display-dependency-updates
```

**設定の問題:**
```bash
# アプリケーション設定を確認
podman-compose exec app cat src/main/resources/application.yml

# 設定を検証
podman-compose exec app mvn validate
```

**ポート競合:**
```yaml
# podman-compose.ymlでアプリケーションポートを変更
services:
  app:
    ports:
      - "8081:8080"  # 異なるホストポートを使用
    environment:
      - SERVER_PORT=8080  # コンテナポートは同じ
```

### メモリの問題（OutOfMemoryError）

#### 症状
```
java.lang.OutOfMemoryError: Java heap space
```

#### 診断
```bash
# JVMメモリ設定を確認
podman-compose exec app jps -v

# メモリ使用量を監視
podman stats $(podman-compose ps -q app)

# ヒープダンプを確認（利用可能な場合）
podman-compose exec app jcmd $(pidof java) GC.run_finalization
```

#### 解決方法

**ヒープサイズを増加:**
```yaml
# podman-compose.ymlで
services:
  app:
    environment:
      - JAVA_OPTS=-Xmx2g -Xms1g -XX:+UseG1GC
```

**メモリリーク検出:**
```bash
# OOM時のヒープダンプを有効化
services:
  app:
    environment:
      - JAVA_OPTS=-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/heapdump.hprof
```

**メモリ使用量のプロファイリング:**
```bash
# JProfilerや類似ツールを使用
podman-compose exec app java -XX:+UnlockCommercialFeatures -XX:+FlightRecorder -XX:StartFlightRecording=duration=60s,filename=/tmp/recording.jfr YourApp
```

## 🧪 テストの問題

### テストの失敗

#### 症状
```
Tests run: 50, Failures: 5, Errors: 2, Skipped: 0
```

#### 診断
```bash
# 詳細ログでテストを実行
podman-compose exec app mvn test -X

# 特定の失敗したテストを実行
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest#shouldFindByEmail"

# テストデータベースの状態を確認
podman-compose exec postgres psql -U postgres -d employee_db -c "\dt"
```

#### 解決方法

**テストデータの問題:**
```bash
# テストデータを検証
podman-compose exec app mvn test -Dtestdata.validate-only=true

# テストデータを更新
podman-compose exec app mvn test -Dtestdata.refresh=true

# テストデータベースをクリーン
podman-compose exec app mvn clean test
```

**TestContainersの問題:**
```bash
# Docker/Podman接続を確認
podman info | grep -E "Rootless|Version"

# TestContainersをクリーン
export TESTCONTAINERS_REUSE_ENABLE=false
podman-compose exec app mvn clean test

# TestContainerログを有効化
export TESTCONTAINERS_LOG_LEVEL=DEBUG
```

**トランザクション/分離の問題:**
```java
// テストクラスで適切なトランザクション管理を確保
@Transactional
@Rollback
public class EmployeeServiceTest {
    // テストメソッド
}
```

### 不安定なテスト

#### 症状
テストが時々成功し、時々失敗する。

#### 診断
```bash
# テストを複数回実行
for i in {1..10}; do
  podman-compose exec app mvn test -Dtest="FlakyTest" || echo "反復 $i で失敗"
done

# タイミング依存関係を確認
podman-compose exec app mvn test -Dtest="FlakyTest" -X | grep -i time
```

#### 解決方法

**適切な待機条件を追加:**
```java
// Thread.sleep()の代わりに
@Test
public void shouldWaitForAsyncOperation() {
    // 非同期操作を開始
    service.asyncMethod();

    // 条件を待機
    await().atMost(Duration.ofSeconds(10))
           .until(() -> service.isCompleted());
}
```

**競合状態を修正:**
```java
// 適切な同期を使用
@Test
@Transactional
public void shouldHandleConcurrentAccess() {
    // 適切な分離レベルを確保
}
```

### テストパフォーマンスの問題

#### 症状
テストの実行時間が長すぎる。

#### 診断
```bash
# テスト実行をプロファイル
podman-compose exec app mvn test -Dtest.profile=true

# データベースコネクションプールを確認
podman-compose logs postgres | grep -i connection

# テスト中のコンテナリソースを監視
podman stats $(podman-compose ps -q) &
podman-compose exec app mvn test
```

#### 解決方法

**TestContainersを最適化:**
```bash
# コンテナを再利用
export TESTCONTAINERS_REUSE_ENABLE=true

# より高速なデータベース初期化を使用
# テスト設定でFlywayを無効にし、直接SQLを使用
```

**並列テスト実行:**
```xml
<!-- pom.xmlで -->
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-surefire-plugin</artifactId>
  <configuration>
    <forkCount>2</forkCount>
    <reuseForks>true</reuseForks>
  </configuration>
</plugin>
```

## 🌐 ネットワークと接続の問題

### サービスにアクセスできない

#### 症状
- pgAdminがhttp://localhost:5050でアクセスできない
- APIがhttp://localhost:8080で応答しない

#### 診断
```bash
# ポートバインディングを確認
podman-compose ps
podman port $(podman-compose ps -q postgres)
podman port $(podman-compose ps -q app)

# 接続をテスト
curl -I http://localhost:8080/actuator/health
curl -I http://localhost:5050

# サービスがリッスンしているかを確認
podman-compose exec app netstat -tlnp
podman-compose exec postgres netstat -tlnp
```

#### 解決方法

**ポートバインディングの問題:**
```yaml
# podman-compose.ymlで適切なポートマッピングを確保
services:
  postgres:
    ports:
      - "5432:5432"  # host:container
  app:
    ports:
      - "8080:8080"
  pgladmin:
    ports:
      - "5050:80"    # pgAdminはコンテナ内でポート80で動作
```

**ファイアウォールの問題:**
```bash
# ファイアウォールルールを確認（Linux）
sudo iptables -L | grep -E '5432|8080|5050'

# テスト用に一時的にファイアウォールを無効化
sudo ufw disable  # Ubuntu/Debian
sudo systemctl stop firewalld  # CentOS/RHEL

# 永続的なルールを追加
sudo ufw allow 5432
sudo ufw allow 8080
sudo ufw allow 5050
```

**コンテナネットワークの問題:**
```bash
# ネットワークを再作成
podman-compose down
podman network prune -f
podman-compose up -d

# コンテナIPアドレスを確認
podman-compose exec app ip addr show
podman-compose exec postgres ip addr show
```

## 📊 パフォーマンストラブルシューティング

### CPU使用率が高い

#### 診断
```bash
# コンテナCPU使用量を監視
podman stats

# Javaスレッド使用量を確認
podman-compose exec app jstack $(pidof java)

# データベースクエリを確認
podman-compose exec postgres psql -U postgres -d employee_db -c "
  SELECT pid, now() - pg_stat_activity.query_start AS duration, query
  FROM pg_stat_activity
  WHERE state = 'active'
  ORDER BY duration DESC;
"
```

#### 解決方法

**アプリケーション最適化:**
```yaml
# JVMガベージコレクションを調整
services:
  app:
    environment:
      - JAVA_OPTS=-XX:+UseG1GC -XX:MaxGCPauseMillis=200 -Xmx2g
```

**データベースクエリ最適化:**
```sql
-- 遅いクエリを特定
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 不足しているインデックスを追加
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_employees_search
ON employees USING gin(to_tsvector('english', first_name || ' ' || last_name));
```

### メモリ使用量が高い

#### 診断
```bash
# コンテナ別メモリ使用量を確認
podman stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Javaヒープ分析
podman-compose exec app jstat -gc $(pidof java)

# データベースメモリ使用量
podman-compose exec postgres psql -U postgres -c "
  SELECT * FROM pg_stat_database WHERE datname = 'employee_db';
"
```

#### 解決方法

**JVMメモリ調整:**
```yaml
services:
  app:
    environment:
      - JAVA_OPTS=-Xmx1g -Xms512m -XX:+UseG1GC -XX:MaxMetaspaceSize=256m
    mem_limit: 2g
```

**PostgreSQLメモリ調整:**
```yaml
services:
  postgres:
    command: >
      postgres
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c work_mem=4MB
      -c max_connections=50
```

## 🛠️ デバッグツールとコマンド

### コンテナ検査
```bash
# 詳細なコンテナ情報を取得
podman inspect $(podman-compose ps -q app)

# 実行中のコンテナでコマンドを実行
podman-compose exec app bash
podman-compose exec postgres bash

# コンテナからファイルをコピー
podman cp $(podman-compose ps -q app):/workspace/target/logs ./app-logs
```

### ログ分析
```bash
# リアルタイムでログを追跡
podman-compose logs -f app | grep -E "ERROR|WARN|Exception"

# ログでパターンを検索
podman-compose logs app | grep -i "connection"

# ログをファイルに保存
podman-compose logs app > app.log 2>&1
```

### データベースデバッグ
```bash
# データベースに接続
podman-compose exec postgres psql -U postgres -d employee_db

# 有用なPostgreSQLデバッグクエリ
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_locks;
SHOW all;
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM employees;
```

### アプリケーションデバッグ
```bash
# デバッグモードを有効化
podman-compose exec app mvn spring-boot:run -Dspring.profiles.active=dev -Ddebug=true

# リモートデバッグ設定
services:
  app:
    environment:
      - JAVA_OPTS=-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005
    ports:
      - "5005:5005"  # デバッグポート
```

## 🆘 緊急復旧

### システム完全リセット
```bash
#!/bin/bash
# 最後の手段 - 完全リセット（全データが削除されます）

echo "警告: これにより全データが削除されます！"
read -p "本当に実行しますか？（続行するには 'yes' と入力）: " confirm

if [ "$confirm" = "yes" ]; then
    echo "全サービスを停止中..."
    podman-compose down -v

    echo "コンテナとボリュームをクリーンアップ中..."
    podman system prune -a -f
    podman volume prune -f

    echo "サービスを再ビルドして開始中..."
    podman-compose build --no-cache
    podman-compose up -d

    echo "サービス開始を待機中..."
    sleep 30

    echo "ヘルスチェックを実行中..."
    ./scripts/health-check.sh

    echo "システムリセット完了！"
else
    echo "リセットをキャンセルしました。"
fi
```

### バックアップと復元
```bash
# 主要な変更前にバックアップを作成
podman-compose exec postgres pg_dump -U postgres employee_db > backup-$(date +%Y%m%d).sql

# バックアップから復元
podman-compose exec -T postgres psql -U postgres employee_db < backup-20240115.sql
```

## 📞 サポートの取得

### サポート用情報収集
```bash
#!/bin/bash
# サポート情報収集スクリプト

echo "職員管理システム - サポート情報" > support-info.txt
echo "================================" >> support-info.txt
date >> support-info.txt
echo "" >> support-info.txt

echo "システム情報:" >> support-info.txt
uname -a >> support-info.txt
echo "" >> support-info.txt

echo "コンテナ状態:" >> support-info.txt
podman-compose ps >> support-info.txt
echo "" >> support-info.txt

echo "コンテナログ:" >> support-info.txt
podman-compose logs >> support-info.txt
echo "" >> support-info.txt

echo "システムリソース:" >> support-info.txt
free -h >> support-info.txt
df -h >> support-info.txt
echo "" >> support-info.txt

echo "ネットワーク設定:" >> support-info.txt
podman network ls >> support-info.txt

echo "サポート情報をsupport-info.txtに収集しました"
```

### よくあるサポートシナリオ

| 問題 | 最初の対処 | ドキュメント |
|------|-----------|-------------|
| コンテナが起動しない | ログを確認: `podman-compose logs` | [コンテナの問題](#🔧-コンテナの問題) |
| データベース接続失敗 | PostgreSQLを確認: `podman-compose exec postgres pg_isready` | [データベースの問題](#🗄️-データベースの問題) |
| テスト失敗 | デバッグで実行: `mvn test -X` | [テストの問題](#🧪-テストの問題) |
| リソース使用量が高い | 監視: `podman stats` | [パフォーマンス](#📊-パフォーマンストラブルシューティング) |
| APIが応答しない | ヘルス確認: `curl localhost:8080/actuator/health` | [アプリケーションの問題](#☕-アプリケーションの問題) |

---

**覚えておいてください**: ほとんどの問題はログの確認、設定の検証、全サービスの稼働状況確認で解決できます。わからない場合は、ヘルスチェックスクリプトから始めて、診断手順を体系的に進めてください。