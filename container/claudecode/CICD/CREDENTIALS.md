# 認証情報管理ガイド

このドキュメントでは、CICD環境のすべての認証情報の管理方法を説明します。

## 📋 目次

- [パスワード統一ポリシー](#パスワード統一ポリシー)
- [認証情報一覧の確認](#認証情報一覧の確認)
- [パスワード更新方法](#パスワード更新方法)
- [初回ログイン後の対応](#初回ログイン後の対応)
- [EC2ドメイン名/IPアドレスの変更](#ec2ドメイン名ipアドレスの変更)
- [データベース認証情報](#データベース認証情報)
- [セキュリティベストプラクティス](#セキュリティベストプラクティス)

---

## 🔑 パスワード統一ポリシー

このプロジェクトでは、初期パスワードを **`Degital2026!`** で統一しています。

### デフォルトパスワード

すべてのサービスとデータベースで以下のパスワードを使用：

```
初期パスワード: Degital2026!
```

### 対象サービス

| サービス | ユーザー名 | 初期パスワード |
|---------|----------|--------------|
| GitLab | root | Degital2026! |
| Nexus Repository | admin | Degital2026! |
| SonarQube | admin | admin → Degital2026! (変更必須) |
| pgAdmin | admin@example.com | Degital2026! |
| PostgreSQL | cicduser | Degital2026! |

### 環境変数ファイル (.env)

すべてのパスワードは `.env` ファイルで一元管理されています。

```bash
# CI/CDサービス
GITLAB_ROOT_PASSWORD=Degital2026!
NEXUS_ADMIN_PASSWORD=Degital2026!
SONARQUBE_ADMIN_PASSWORD=Degital2026!

# データベース
POSTGRES_PASSWORD=Degital2026!
PGADMIN_PASSWORD=Degital2026!
SONAR_DB_PASSWORD=Degital2026!
SAMPLE_DB_PASSWORD=Degital2026!
```

---

## 📊 認証情報一覧の確認

### 1. コマンドで確認

```bash
# ターミナルに表示
./scripts/utils/show-credentials.sh

# ファイルに出力
./scripts/utils/show-credentials.sh --file

# 出力されたファイルを確認
cat credentials.txt

# 確認後は削除推奨
rm credentials.txt
```

### 2. 環境変数の確認

```bash
# 現在の設定を表示
./scripts/utils/update-passwords.sh --show

# または .env ファイルを直接確認
cat .env
```

### 3. 認証情報ファイルの内容

`show-credentials.sh --file` を実行すると、以下の情報が `credentials.txt` に出力されます：

- すべてのサービスのURL、ユーザー名、パスワード
- PostgreSQL データベーススキーマ別の認証情報
- SonarQube トークン、GitLab Runner トークン
- 初回ログイン後の対応手順
- 接続確認コマンド
- セキュリティに関する注意事項

**重要**: このファイルには機密情報が含まれているため、確認後は必ず削除してください。

---

## 🔄 パスワード更新方法

### update-passwords.sh の使い方

パスワードやトークンを変更する場合は、専用スクリプトを使用します。

#### 1. 特定のサービスのパスワードを更新

```bash
# GitLabパスワードを更新
./scripts/utils/update-passwords.sh --gitlab 'NewPassword123!'

# Nexusパスワードを更新
./scripts/utils/update-passwords.sh --nexus 'NewPassword123!'

# SonarQubeパスワードを更新
./scripts/utils/update-passwords.sh --sonarqube 'NewPassword123!'

# PostgreSQLパスワードを更新
./scripts/utils/update-passwords.sh --postgres 'NewPassword123!'

# pgAdminパスワードを更新
./scripts/utils/update-passwords.sh --pgadmin 'NewPassword123!'
```

#### 2. すべてのパスワードを一括更新

```bash
# すべてのパスワードを同じ値に統一
./scripts/utils/update-passwords.sh --all 'Degital2026!'
```

#### 3. トークンを更新

```bash
# SonarQubeトークンを更新
./scripts/utils/update-passwords.sh --sonar-token 'sqa_1234567890abcdef'

# GitLab Runnerトークンを更新
./scripts/utils/update-passwords.sh --runner-token 'glrt-xxxxxxxxxxxx'
```

#### 4. 現在の設定を確認

```bash
./scripts/utils/update-passwords.sh --show
```

### パスワード更新後の対応

#### Nexusパスワード変更時

```bash
# 1. .envファイルを更新
./scripts/utils/update-passwords.sh --nexus 'NewPassword123!'

# 2. GitLab CI/CD環境変数を更新
# GitLab → Settings → CI/CD → Variables → NEXUS_ADMIN_PASSWORD

# 3. sample-app/.ci-settings.xml.template を確認（変更不要）
# テンプレートは環境変数を参照するため、自動的に反映されます
```

#### PostgreSQLパスワード変更時

```bash
# 1. .envファイルを更新
./scripts/utils/update-passwords.sh --postgres 'NewPassword123!'

# 2. コンテナを再起動
cd /root/aws.git/container/claudecode/CICD
podman-compose down
podman-compose up -d
```

#### SonarQubeパスワード変更時

```bash
# 1. .envファイルを更新
./scripts/utils/update-passwords.sh --sonarqube 'NewPassword123!'

# 2. SonarQubeトークンを再生成
# SonarQube → My Account → Security → Generate Token

# 3. トークンを更新
./scripts/utils/update-passwords.sh --sonar-token 'sqa_新しいトークン'

# 4. GitLab CI/CD環境変数を更新
# GitLab → Settings → CI/CD → Variables → SONAR_TOKEN
```

---

## 🚪 初回ログイン後の対応

### 1. SonarQube（パスワード変更必須）

SonarQubeは初回ログイン時に必ずパスワード変更が求められます。

#### 手順

```bash
# 1. SonarQubeにアクセス
# http://YOUR_IP:8000

# 2. デフォルト認証情報でログイン
# ユーザー名: admin
# パスワード: admin

# 3. 新しいパスワードを設定（推奨: Degital2026!）

# 4. 環境変数を更新
./scripts/utils/update-passwords.sh --sonarqube 'Degital2026!'

# 5. SonarQubeトークンを生成
# My Account → Security → Generate Token
# Name: gitlab-ci
# Type: Global Analysis Token

# 6. トークンを環境変数に設定
./scripts/utils/update-passwords.sh --sonar-token 'sqa_xxxxxxxxxxxxxxxxxxxxx'

# 7. GitLab CI/CD環境変数を更新
# GitLab → Settings → CI/CD → Variables
# Key: SONAR_TOKEN
# Value: sqa_xxxxxxxxxxxxxxxxxxxxx
# Flags: Masked
```

### 2. Nexus Repository（セットアップウィザード）

Nexusは初回アクセス時にセットアップウィザードが表示される場合があります。

#### 手順

```bash
# 1. Nexusにアクセス
# http://YOUR_IP:8082

# 2. "Sign in" をクリック
# ユーザー名: admin
# パスワード: Degital2026!

# 3. セットアップウィザードが表示された場合
# - "Next" をクリック
# - パスワード変更を求められた場合は、同じパスワードを設定
# - Anonymous access: Disable（推奨）
# - "Finish" をクリック

# 4. パスワードを変更した場合は、環境変数を更新
./scripts/utils/update-passwords.sh --nexus '新しいパスワード'

# 5. GitLab CI/CD環境変数も更新
# GitLab → Settings → CI/CD → Variables → NEXUS_ADMIN_PASSWORD
```

### 3. GitLab Runner の登録

GitLab Runnerは初回セットアップ時に登録が必要です。

#### 手順

```bash
# 1. GitLabにログイン
# http://YOUR_IP:5003
# ユーザー名: root
# パスワード: Degital2026!

# 2. Runnerトークンを取得
# Settings → CI/CD → Runners → "New project runner"
# または既存のトークンを使用

# 3. Runnerを登録
sudo gitlab-runner register \
  --url http://YOUR_IP:5003 \
  --token YOUR_REGISTRATION_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

# 4. Runnerを起動
sudo systemctl enable --now gitlab-runner

# 5. トークンを環境変数に保存（任意）
./scripts/utils/update-passwords.sh --runner-token 'YOUR_REGISTRATION_TOKEN'
```

---

## 🌐 EC2ドメイン名/IPアドレスの変更

### EC2インスタンス再作成時の対応

EC2インスタンスを再作成した場合、IPアドレスやドメイン名が変わります。このセクションでは、ドメイン名/IPアドレスの変更方法を説明します。

### 変更が必要なケース

1. **EC2インスタンスの再作成**: 新しいインスタンスで異なるIPアドレスが割り当てられる
2. **Elastic IPの変更**: Elastic IPを変更または削除した場合
3. **ドメイン名の設定**: Route 53などでドメイン名を設定した場合
4. **開発環境の移行**: 別のEC2インスタンスに環境を移行する場合

### 方法1: 初回セットアップ時に入力

`setup-from-scratch.sh` 実行時にドメイン名/IPアドレスを入力できます。

```bash
cd /root/aws.git/container/claudecode/CICD
./scripts/setup-from-scratch.sh

# ...
# [6/12] EC2ドメイン名/IPアドレスを設定中...
#
# EC2インスタンスのドメイン名またはIPアドレスを入力してください
# 例: ec2-xx-xx-xx-xx.compute-1.amazonaws.com
# 例: 192.168.1.100
#
# ※ 入力しない場合は自動検出します（EC2メタデータから取得）
#
# ドメイン名/IPアドレス: [ここに入力]
```

**入力例**:
```bash
# EC2パブリックDNS名
ec2-34-205-156-203.compute-1.amazonaws.com

# Elastic IP
54.123.456.789

# カスタムドメイン
cicd.example.com

# ローカル開発環境
192.168.1.100
```

### 方法2: 既存環境のドメイン名を更新

既に環境が稼働している場合、`update-passwords.sh` を使用して変更できます。

```bash
# ドメイン名/IPアドレスを更新
./scripts/utils/update-passwords.sh --ec2-host ec2-34-205-156-203.compute-1.amazonaws.com

# または
./scripts/utils/update-passwords.sh --ec2-host 54.123.456.789
```

**実行結果**:
```
【EC2 ドメイン名/IPアドレス】
  変数名: EC2_PUBLIC_IP
  新しい値: ec2-****

  ✓ 更新完了

✓ EC2ドメイン名/IPアドレスを更新しました: ec2-34-205-156-203.compute-1.amazonaws.com

⚠️ 変更後の確認方法:
  ./scripts/utils/show-credentials.sh

⚠️ コンテナの再起動は不要ですが、GitLabなどのURL設定が変わります
  sample-appのリモートURLも更新してください:
  cd sample-app
  git remote set-url origin http://ec2-34-205-156-203.compute-1.amazonaws.com:5003/root/sample-app.git
```

### 方法3: .envファイルを直接編集

```bash
# .envファイルを編集
vi .env

# EC2_PUBLIC_IPの値を変更
# 変更前: EC2_PUBLIC_IP=34.205.156.203
# 変更後: EC2_PUBLIC_IP=ec2-34-205-156-203.compute-1.amazonaws.com

# 保存して終了
```

### 変更後の確認

#### 1. 環境変数の確認

```bash
# 現在の設定を表示
./scripts/utils/update-passwords.sh --show

# または
cat .env | grep EC2_PUBLIC_IP
```

#### 2. 認証情報の確認

```bash
# すべてのサービスURLを確認
./scripts/utils/show-credentials.sh

# ファイルに出力して確認
./scripts/utils/show-credentials.sh --file
cat credentials.txt
rm credentials.txt
```

#### 3. サービスへのアクセス確認

```bash
# 新しいドメイン名/IPアドレスでアクセス確認
NEW_HOST="ec2-34-205-156-203.compute-1.amazonaws.com"

curl http://${NEW_HOST}:5003/  # GitLab
curl http://${NEW_HOST}:8082/  # Nexus
curl http://${NEW_HOST}:8000/  # SonarQube
curl http://${NEW_HOST}:5002/  # pgAdmin
```

### 関連設定の更新

#### GitLab sample-app リモートURL

```bash
cd sample-app

# 現在のリモートURLを確認
git remote -v

# リモートURLを更新
git remote set-url origin http://NEW_HOST:5003/root/sample-app.git

# 確認
git remote -v

# プッシュテスト
git push origin master
```

#### GitLab Runner の再登録

ドメイン名が変わった場合、GitLab Runnerの再登録が必要な場合があります。

```bash
# 既存のRunnerを削除
sudo gitlab-runner unregister --all-runners

# 新しいURLで再登録
sudo gitlab-runner register \
  --url http://NEW_HOST:5003 \
  --token YOUR_REGISTRATION_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

# Runner起動
sudo systemctl restart gitlab-runner
```

#### ブラウザのブックマーク更新

- GitLab: `http://NEW_HOST:5003`
- Nexus: `http://NEW_HOST:8082`
- SonarQube: `http://NEW_HOST:8000`
- pgAdmin: `http://NEW_HOST:5002`

### トラブルシューティング

#### ドメイン名が解決できない場合

```bash
# DNS解決確認
nslookup ec2-34-205-156-203.compute-1.amazonaws.com

# pingテスト
ping ec2-34-205-156-203.compute-1.amazonaws.com

# 名前解決できない場合は、IPアドレスを使用
./scripts/utils/update-passwords.sh --ec2-host 34.205.156.203
```

#### GitLabにアクセスできない場合

```bash
# セキュリティグループ確認
# AWS Console → EC2 → Security Groups
# インバウンドルールで以下のポートが開いているか確認:
# - 5003 (GitLab)
# - 8082 (Nexus)
# - 8000 (SonarQube)
# - 5002 (pgAdmin)

# GitLabコンテナの状態確認
podman ps | grep gitlab
podman logs cicd-gitlab | tail -20
```

#### CI/CDパイプラインが失敗する場合

```bash
# GitLab CI/CD環境変数のURLを確認
# GitLab → Settings → CI/CD → Variables

# .ci-settings.xml.template のURLは環境変数を使用するため、
# 自動的に更新されます（変更不要）
```

### ベストプラクティス

#### 1. Elastic IPの使用

IPアドレスが変わらないようにするため、Elastic IPを割り当てることを推奨します。

```bash
# AWS Console → EC2 → Elastic IPs
# 1. Elastic IPを割り当て
# 2. EC2インスタンスに関連付け
# 3. .envファイルを更新
./scripts/utils/update-passwords.sh --ec2-host YOUR_ELASTIC_IP
```

#### 2. Route 53でドメイン名を設定

覚えやすいドメイン名を使用することを推奨します。

```bash
# Route 53でAレコードを作成
# cicd.example.com → Elastic IP

# .envファイルを更新
./scripts/utils/update-passwords.sh --ec2-host cicd.example.com
```

#### 3. 変更履歴の記録

```bash
# .envファイルのバックアップ（自動作成）
# update-passwords.sh実行時に自動的にバックアップされます:
# .env.backup.YYYYMMDDHHMMSS

# バックアップファイルの一覧
ls -lt .env.backup.*

# 以前のドメイン名を確認
cat .env.backup.20260110120000 | grep EC2_PUBLIC_IP
```

---

## 🗄️ データベース認証情報

### PostgreSQL スキーマ別認証情報

このプロジェクトでは、PostgreSQLに複数のデータベースとユーザーが作成されます。

#### 1. cicddb（CICD環境用）

```bash
ホスト:       localhost（または EC2_PUBLIC_IP）
ポート:       5001
ユーザー名:   cicduser
パスワード:   Degital2026!
データベース: cicddb

# 接続コマンド
psql -h localhost -p 5001 -U cicduser -d cicddb
```

#### 2. gitlabhq（GitLab用）

```bash
ホスト:       postgres（コンテナ内）
ポート:       5432
ユーザー名:   gitlab
パスワード:   Degital2026!
データベース: gitlabhq

# 接続コマンド（pgAdminまたはコンテナ内から）
psql -h postgres -p 5432 -U gitlab -d gitlabhq
```

#### 3. sonarqube（SonarQube用）

```bash
ホスト:       postgres（コンテナ内）
ポート:       5432
ユーザー名:   sonar
パスワード:   Degital2026!
データベース: sonarqube

# 接続コマンド（pgAdminまたはコンテナ内から）
psql -h postgres -p 5432 -U sonar -d sonarqube
```

#### 4. sample_app（サンプルアプリ用）

```bash
ホスト:       postgres（コンテナ内）
ポート:       5432
ユーザー名:   sampleuser
パスワード:   Degital2026!
データベース: sample_app

# 接続コマンド（pgAdminまたはコンテナ内から）
psql -h postgres -p 5432 -U sampleuser -d sample_app
```

### データベースパスワードの変更方法

データベースのパスワードを変更する場合は、以下の手順で行います。

```bash
# 1. PostgreSQLコンテナに接続
podman exec -it cicd-postgres psql -U postgres

# 2. パスワードを変更（例: cicduser）
ALTER USER cicduser WITH PASSWORD '新しいパスワード';

# 3. 他のユーザーも同様に変更
ALTER USER gitlab WITH PASSWORD '新しいパスワード';
ALTER USER sonar WITH PASSWORD '新しいパスワード';
ALTER USER sampleuser WITH PASSWORD '新しいパスワード';

# 4. PostgreSQLから退出
\q

# 5. .env ファイルを更新
./scripts/utils/update-passwords.sh --postgres '新しいパスワード'
./scripts/utils/update-passwords.sh --sonar-db '新しいパスワード'
./scripts/utils/update-passwords.sh --sample-db '新しいパスワード'

# 6. コンテナを再起動
podman-compose down
podman-compose up -d
```

---

## 🔐 セキュリティベストプラクティス

### 1. パスワード管理

#### 強力なパスワードの使用

本番環境では、より強力なパスワードを設定してください：

- **最低12文字以上**
- **大文字、小文字、数字、記号を組み合わせる**
- **辞書に載っている単語を避ける**
- **推測されやすい情報（誕生日、名前など）を避ける**

例:
```bash
# 強力なパスワードに変更
./scripts/utils/update-passwords.sh --all 'Xk9#mP2$vL8@qR5!'
```

#### 定期的なパスワード変更

パスワードは定期的に変更してください（推奨: 90日ごと）。

```bash
# 定期的にすべてのパスワードを更新
./scripts/utils/update-passwords.sh --all '新しい強力なパスワード'
```

### 2. ファイル管理

#### .env ファイルのパーミッション

```bash
# 所有者のみ読み書き可能に設定
chmod 600 .env

# 確認
ls -la .env
# -rw------- 1 ec2-user ec2-user ... .env
```

#### credentials.txt の取り扱い

```bash
# 認証情報ファイルは確認後すぐに削除
./scripts/utils/show-credentials.sh --file
cat credentials.txt
rm credentials.txt

# または自動削除付きで表示
./scripts/utils/show-credentials.sh --file && cat credentials.txt && rm credentials.txt
```

#### .env のバックアップ暗号化

```bash
# バックアップを暗号化
gpg --symmetric --cipher-algo AES256 .env
# パスフレーズを入力

# .env.gpg が生成される

# 元のファイルを削除（任意）
rm .env

# 復号化
gpg --decrypt .env.gpg > .env
```

### 3. Git管理

#### .gitignore の確認

以下のファイルが `.gitignore` に含まれていることを確認：

```gitignore
# 認証情報ファイル
credentials.txt
.env.backup.*

# 環境変数（コメントアウトされている場合は注意）
# .env
```

#### 公開リポジトリでの注意

公開リポジトリにプッシュする場合：

```bash
# 1. .env を .gitignore に追加（コメントアウトを解除）
vi .gitignore
# .env の行のコメント '#' を削除

# 2. 既にコミットされている場合は履歴から削除
git rm --cached .env
git commit -m "Remove .env from repository"

# 3. .env.template を作成してコミット
cp .env .env.template
vi .env.template
# パスワードをプレースホルダーに置き換え（例: YOUR_PASSWORD_HERE）
git add .env.template
git commit -m "Add .env template"
```

### 4. アクセス制限

#### ファイアウォール設定

```bash
# 必要なポートのみ開放
sudo firewall-cmd --permanent --add-port=5003/tcp  # GitLab
sudo firewall-cmd --permanent --add-port=8082/tcp  # Nexus
sudo firewall-cmd --permanent --add-port=8000/tcp  # SonarQube
sudo firewall-cmd --reload

# データベースポートは内部のみ
# 5001/tcp は外部からのアクセスを制限
```

#### GitLab CI/CD環境変数

機密情報はGitLab CI/CD環境変数に設定し、マスク化：

```bash
# GitLab → Settings → CI/CD → Variables
#
# 設定する変数:
# - NEXUS_ADMIN_PASSWORD (Masked)
# - SONAR_TOKEN (Masked)
# - POSTGRES_PASSWORD (Masked, Optional)
```

### 5. 監査とログ

#### 認証試行の監視

```bash
# GitLabログの確認
podman logs cicd-gitlab | grep -i "authentication"

# Nexusログの確認
podman logs cicd-nexus | grep -i "login"

# SonarQubeログの確認
podman logs cicd-sonarqube | grep -i "authentication"
```

#### パスワード変更履歴

`.env.backup.*` ファイルで変更履歴を確認：

```bash
# バックアップファイルの一覧
ls -la .env.backup.*

# 特定のバックアップの内容を確認
cat .env.backup.20260110120000
```

---

## 📞 トラブルシューティング

### パスワードを忘れた場合

#### 1. .env ファイルから確認

```bash
cat .env | grep PASSWORD
```

#### 2. バックアップファイルから復元

```bash
# 最新のバックアップを確認
ls -lt .env.backup.* | head -1

# バックアップから復元
cp .env.backup.YYYYMMDDHHMMSS .env
```

#### 3. パスワードをリセット

```bash
# すべてのパスワードをデフォルトに戻す
./scripts/utils/update-passwords.sh --all 'Degital2026!'

# コンテナを再起動
podman-compose down
podman-compose up -d
```

### 認証エラーが発生する場合

```bash
# 1. .env ファイルの内容を確認
./scripts/utils/update-passwords.sh --show

# 2. サービスの再起動
podman-compose restart <service_name>

# 3. ログを確認
podman logs cicd-<service_name>

# 4. GitLab CI/CD環境変数を確認
# GitLab → Settings → CI/CD → Variables
```

---

## 📚 関連ドキュメント

- [README.md](README.md) - プロジェクト全体のガイド
- [QUICKSTART.md](QUICKSTART.md) - クイックスタートガイド
- [scripts/utils/show-credentials.sh](scripts/utils/show-credentials.sh) - 認証情報表示スクリプト
- [scripts/utils/update-passwords.sh](scripts/utils/update-passwords.sh) - パスワード更新スクリプト
- [scripts/setup-from-scratch.sh](scripts/setup-from-scratch.sh) - セットアップスクリプト

---

**最終更新日**: 2026-01-10
**バージョン**: 1.0.0
