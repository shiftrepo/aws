# CICD環境 クイックスタートガイド

## 📦 スクラップビルド対応完了

この環境は完全なスクラップビルド（ゼロからの再構築）に対応しています。

## 🚀 使い方

### 1. 新しいEC2インスタンスでゼロからセットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd CICD

# セットアップ実行
chmod +x scripts/*.sh
./scripts/setup-from-scratch.sh
```

### 2. 現在の環境をバックアップ

```bash
./scripts/utils/backup-all.sh
```

バックアップされるもの:
- ✅ 全設定ファイル（docker-compose.yml、.env など）
- ✅ GitLab リポジトリ（sample-app）
- ✅ GitLab データベース
- ✅ GitLab Runner 設定
- ✅ Maven 設定
- ✅ 環境情報

バックアップは以下に保存されます:
- ディレクトリ: `backup-YYYYMMDD-HHMMSS/`
- アーカイブ: `backup-YYYYMMDD-HHMMSS.tar.gz`

### 3. バックアップから復元

```bash
# バックアップアーカイブを展開
tar xzf backup-20260110-075148.tar.gz

# 復元実行
./scripts/utils/restore-all.sh backup-20260110-075148
```

### 4. 完全クリーンアップ

```bash
./scripts/cleanup-all.sh
```

削除されるもの:
- 全コンテナ
- 全ボリューム
- ネットワーク
- GitLab Runner設定
- Maven設定（オプション）

### 5. ワンクリック再デプロイ

バックアップ → クリーンアップ → セットアップを一括実行:

```bash
./scripts/utils/deploy-oneclick.sh
```

## 📋 スクリプト一覧

| スクリプト | 説明 |
|----------|------|
| `setup-from-scratch.sh` | ゼロから完全環境セットアップ |
| `utils/backup-all.sh` | 現在の環境を完全バックアップ |
| `utils/restore-all.sh` | バックアップから復元 |
| `cleanup-all.sh` | 環境を完全クリーンアップ |
| `utils/deploy-oneclick.sh` | ワンクリック再デプロイ |

## 🔧 セットアップ後の初期設定

### Nexus
```
URL: http://YOUR_IP:8082
初期パスワード: Degital2026!
```

### SonarQube
```
URL: http://YOUR_IP:8000
デフォルト: admin / admin
```

### GitLab
```
URL: http://YOUR_IP:5003
rootパスワードは初回アクセス時に設定
```

### GitLab Runner登録
```bash
sudo gitlab-runner register \
  --url http://YOUR_IP:5003 \
  --token YOUR_REGISTRATION_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"
```

## 📦 バックアップファイルの構造

```
backup-YYYYMMDD-HHMMSS/
├── config/                    # 全設定ファイル
│   ├── gitlab/
│   ├── nexus/
│   ├── sonarqube/
│   ├── postgres/
│   ├── pgadmin/
│   ├── gitlab-runner/
│   ├── maven/
│   ├── runner-config.toml
│   ├── maven-settings.xml
│   ├── maven-settings-root.xml
│   └── maven-settings-runner.xml
├── volumes/
│   └── gitlab-backup.tar      # GitLabデータベースバックアップ
├── repos/
│   ├── sample-app.bundle      # Gitリポジトリ
│   └── sample-app-files.tar.gz # ソースファイル
├── scripts/                   # 全運用スクリプト
├── docker-compose.yml
├── .env
├── .gitignore
├── README.md
└── environment-info.txt       # 環境情報
```

## 🌐 サービスURL

| サービス | URL |
|---------|-----|
| GitLab | http://YOUR_IP:5003 |
| Nexus | http://YOUR_IP:8082 |
| SonarQube | http://YOUR_IP:8000 |
| pgAdmin | http://YOUR_IP:5002 |
| Mattermost | http://YOUR_IP:5004 |

## ✅ 動作確認

```bash
# コンテナ状態確認
podman ps

# サービス接続確認
curl http://localhost:5003/  # GitLab
curl http://localhost:8082/  # Nexus
curl http://localhost:8000/  # SonarQube

# パイプライン実行確認
cd sample-app
git push origin master
```

## 🎯 スクラップビルドシナリオ

### シナリオ1: 新EC2インスタンスへの移行

1. 旧環境でバックアップ実行
```bash
./scripts/utils/backup-all.sh
```

2. バックアップファイルを新環境にコピー
```bash
scp backup-YYYYMMDD-HHMMSS.tar.gz ec2-user@NEW_IP:/root/
```

3. 新環境でセットアップ実行
```bash
ssh ec2-user@NEW_IP
cd /root
tar xzf backup-YYYYMMDD-HHMMSS.tar.gz
cd CICD
./scripts/setup-from-scratch.sh
./scripts/utils/restore-all.sh ../backup-YYYYMMDD-HHMMSS
```

### シナリオ2: 定期バックアップの自動化

cronで毎日自動バックアップ:
```bash
# /etc/cron.d/cicd-backup
0 3 * * * ec2-user ./scripts/utils/backup-all.sh
```

### シナリオ3: 災害復旧

1. バックアップアーカイブを持つ
2. 新環境を準備
3. `setup-from-scratch.sh` → `restore-all.sh`
4. 5-10分で完全復旧

---

**作成日**: 2026-01-10
**バージョン**: 1.0.0
