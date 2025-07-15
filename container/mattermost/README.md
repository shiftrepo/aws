# Mattermost & GitLab 連携コンテナ

## 概要
このリポジトリには、Mattermostをコンテナ化し、GitLabと連携するための設定が含まれています。
正常に動作するよう設定されたMattermostサーバー（バージョン9.5.1）とPostgreSQLデータベースを提供します。

## ファイル構成
- `Dockerfile`: Mattermostコンテナのビルド定義
- `config.json`: Mattermostの設定ファイル
- `podman-compose.yml`: コンテナオーケストレーション定義
- `root-entrypoint.sh`: コンテナ起動スクリプト

## 前提条件
- GitLabコンテナがすでに起動している（ホスト名: gitlab）
- podmanとpodman-composeがインストールされている
- ネットワーク接続に制限があり、運用環境ではダウンロード不可

## セットアップ手順

### 1. ネットワークの作成

```bash
# Mattermostネットワークの作成
podman network create mattermost-network

# GitLabネットワークが存在しない場合は作成
podman network create gitlab-network
```

### 2. コンテナのビルドと起動

```bash
cd /path/to/mattermost
podman-compose build
podman-compose up -d
```

### 3. Mattermostへのアクセス

ブラウザで`http://localhost:8001`にアクセスし、管理者アカウントを作成してください。

## GitLab連携の設定手順

### 1. GitLabでアプリケーションを作成

GitLabにログイン後、以下の手順でMattermost用のOAuthアプリケーションを作成します：

1. GitLabの管理者アカウントでログイン
2. 「Admin Area」（管理エリア）を選択
3. 「Applications」（アプリケーション）を選択
4. 「New Application」（新しいアプリケーション）をクリック
5. 以下の情報を入力：
   - Name: Mattermost
   - Redirect URI: 
     - `http://localhost:8001/signup/gitlab/complete`
     - `http://localhost:8001/login/gitlab/complete`
   - Scopes: api, read_user
6. 「Submit」（送信）をクリック
7. 表示される「Application ID」と「Secret」を記録（これらの値は後で必要）

### 2. SSH鍵の作成（GitLabリポジトリのクローン用）

```bash
# コンテナ内でSSH鍵を生成
podman exec -it mattermost-app bash
mkdir -p /opt/mattermost/.ssh
ssh-keygen -t rsa -b 4096 -C "mattermost@example.com" -f /opt/mattermost/.ssh/id_rsa -N ""

# 公開鍵の内容を表示（GitLabに登録するため）
cat /opt/mattermost/.ssh/id_rsa.pub
```

この公開鍵をGitLabの「Admin Area」→「Users」→該当ユーザー→「SSH Keys」に追加します。

### 3. Mattermostの設定変更

1. `config.json`ファイルの`GitLabSettings`セクションを編集：

```json
"GitLabSettings": {
  "Enable": true,
  "Secret": "GitLabで取得したSecret",
  "Id": "GitLabで取得したApplication ID",
  "Scope": "api read_user",
  "AuthEndpoint": "http://gitlab:3000/oauth/authorize",
  "TokenEndpoint": "http://gitlab:3000/oauth/token",
  "UserApiEndpoint": "http://gitlab:3000/api/v4/user",
  "DiscoveryEndpoint": ""
}
```

## コンテナの停止

```bash
cd /path/to/mattermost
podman-compose down
```

## GitLabプラグインの有効化

1. Mattermostの「System Console」→「Plugins」→「Management」に移動
2. GitLabプラグインを探して「Enable」をクリック
3. 「System Console」→「Plugins」→「GitLab」に移動
4. GitLabの設定を確認、必要に応じて修正
5. 設定を保存

## トラブルシューティング

### 一般的な問題

- ログの確認: `podman logs mattermost-app`
- コンテナ内でのデバッグ: `podman exec -it mattermost-app bash`

### Mattermostが起動しない場合

1. 環境変数PATHが正しく設定されているか確認：
   ```bash
   podman exec -it mattermost-app env | grep PATH
   ```

2. バイナリファイルの権限を確認：
   ```bash
   podman exec -it mattermost-app ls -la /opt/mattermost/bin/
   ```

### GitLab連携が機能しない場合

1. ネットワーク接続を確認：
   ```bash
   # pingコマンドのインストール
   podman exec -it mattermost-app apt-get update && podman exec -it mattermost-app apt-get install -y iputils-ping
   
   # GitLabへの疎通確認
   podman exec -it --privileged mattermost-app ping -c 2 gitlab
   ```

2. `podman-compose.yml`のネットワーク設定を確認