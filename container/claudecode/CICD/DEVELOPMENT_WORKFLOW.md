# 開発ワークフローデモガイド

## 概要

このドキュメントでは、組織構成図機能の追加を例に、Issue作成からデプロイまでの完全な開発フローを自動化するデモスクリプトについて説明します。

## 開発フロー全体像

```
┌────────────────────────────────────────────────────────────────┐
│ 1. Issue作成 (GitHub)                                          │
│    ↓                                                            │
│ 2. 開発環境準備 (GitLab Working Directory)                     │
│    ↓                                                            │
│ 3. Backend実装 (OrganizationTree API)                          │
│    ↓                                                            │
│ 4. Backend テスト追加 (100%カバレッジ維持)                     │
│    ↓                                                            │
│ 5. Frontend実装 (OrganizationTree Component)                   │
│    ↓                                                            │
│ 6. ローカルビルド＆テスト                                       │
│    ↓                                                            │
│ 7. GitLabへプッシュ                                            │
│    ↓                                                            │
│ 8. CI/CDパイプライン自動実行 (6ステージ)                       │
│    ├─ build: Mavenコンパイル                                   │
│    ├─ test: ユニットテスト                                     │
│    ├─ coverage: JaCoCoカバレッジチェック                       │
│    ├─ sonarqube: 静的解析                                      │
│    ├─ package: JARパッケージング                               │
│    └─ deploy: Nexusへデプロイ                                  │
│    ↓                                                            │
│ 9. Merge Request作成 (GitLab)                                  │
│    ↓                                                            │
│ 10. 承認＆マージ                                               │
│    ↓                                                            │
│ 11. コンテナビルド＆デプロイ                                   │
│    ↓                                                            │
│ 12. 動作確認                                                   │
│    ↓                                                            │
│ 13. マスタリポジトリへ同期 (GitHub)                            │
│    ↓                                                            │
│ 14. 完了サマリー表示                                           │
└────────────────────────────────────────────────────────────────┘
```

## 前提条件

### 1. CI/CD環境の稼働

すべてのCI/CDサービスが稼働している必要があります：

```bash
# サービス起動
cd /root/aws.git/container/claudecode/CICD
sudo podman-compose up -d

# 起動確認
sudo podman ps
```

稼働中のサービス：
- **GitLab** (port 5003): バージョン管理・CI/CD
- **Nexus** (port 8082): Maven リポジトリ
- **SonarQube** (port 8000): 静的解析
- **PostgreSQL** (port 5001): データベース

### 2. GitLab Runnerの登録

GitLab Runnerが登録されている必要があります：

```bash
sudo gitlab-runner list
```

登録されていない場合：

```bash
sudo gitlab-runner register \
  --url http://YOUR_IP:5003 \
  --token YOUR_REGISTRATION_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

sudo systemctl enable --now gitlab-runner
```

### 3. 環境変数の設定

`.env`ファイルに以下の環境変数が設定されている必要があります：

- `GITLAB_ROOT_PASSWORD`: GitLab rootパスワード
- `EC2_PUBLIC_IP`: EC2インスタンスのパブリックIP/ドメイン
- `NEXUS_ADMIN_PASSWORD`: Nexus adminパスワード
- `SONARQUBE_ADMIN_PASSWORD`: SonarQube adminパスワード

## 使用方法

### 基本的な実行

```bash
cd /root/aws.git/container/claudecode/CICD

# 開発ワークフロー全体を自動実行
./scripts/demo-development-workflow.sh
```

### 実行される処理

#### STEP 1: 環境確認
すべてのCI/CDサービス（GitLab, Nexus, SonarQube, PostgreSQL）の稼働状態を確認します。

#### STEP 2: GitLab作業ディレクトリ準備
- `/tmp/gitlab-sample-app` の存在確認（setup-sample-app.sh で作成済み）
- 最新のmasterブランチを取得
- フィーチャーブランチ作成: `feature/organization-tree-view`

#### STEP 3: Backend実装
以下のファイルを自動生成：
- `common/src/main/java/com/example/common/dto/OrganizationTreeDto.java`
- `common/src/main/java/com/example/common/dto/DepartmentTreeNode.java`
- `backend/src/main/java/com/example/backend/service/OrganizationService.java` (メソッド追加)
- `backend/src/main/java/com/example/backend/controller/OrganizationController.java` (エンドポイント追加)

新規エンドポイント: `GET /api/organizations/{id}/tree`

#### STEP 4: Backend テスト追加
`OrganizationServiceTest.java` に以下のテストケースを追加：
- 組織階層構造取得 - 正常系
- 組織階層構造取得 - 組織が存在しない
- 組織階層構造取得 - 部門が存在しない
- 組織階層構造取得 - 3階層構造

#### STEP 5: Frontend実装
以下のファイルを自動生成：
- `frontend/src/components/OrganizationTree.jsx`: 組織構成図コンポーネント
- `frontend/src/components/TreeNode.jsx`: ツリーノードコンポーネント
- `frontend/src/styles/OrganizationTree.css`: 構成図スタイル
- `frontend/src/styles/TreeNode.css`: ノードスタイル
- `frontend/src/App.jsx` (ルート追加)
- `frontend/src/components/OrganizationList.jsx` (構成図ボタン追加)

#### STEP 6: ローカルビルド＆テスト
Maven ビルドとテストを実行：
```bash
mvn clean install
mvn test
mvn jacoco:report
```

JaCoCo カバレッジレポート: `backend/target/site/jacoco/index.html`

#### STEP 7: GitLabへコミット＆プッシュ
変更内容をGitLabのフィーチャーブランチへプッシュします。

#### STEP 8: CI/CDパイプライン実行監視
GitLab CI/CDパイプラインが自動実行されます。以下の6ステージが実行されます：

1. **build**: Mavenコンパイル
2. **test**: ユニットテスト実行
3. **coverage**: JaCoCoカバレッジチェック（70%以上）
4. **sonarqube**: SonarQube静的解析
5. **package**: JARパッケージング
6. **deploy**: Nexusリポジトリへデプロイ

パイプラインURL: `http://YOUR_IP:5003/root/sample-app/-/pipelines`

#### STEP 9: Merge Request作成
GitLab APIを使用してMerge Requestを自動作成します。

#### STEP 10: 承認＆マージ
Merge Requestを自動承認し、masterブランチへマージします。

#### STEP 11: コンテナビルド＆デプロイ
- Backend コンテナビルド: `sample-backend:latest`
- Frontend + Nginx コンテナビルド: `nginx-frontend:latest`
- 既存コンテナ停止
- 新しいコンテナ起動

#### STEP 12: 動作確認
APIエンドポイントの動作確認：
- `GET /api/organizations`: 組織一覧取得
- `GET /api/organizations/1/tree`: 組織階層構造取得

フロントエンド確認URL：
- 組織一覧: `http://YOUR_IP:5006/`
- 組織構成図: `http://YOUR_IP:5006/organizations/1/tree`

#### STEP 13: マスタリポジトリへ同期
GitLab作業ディレクトリからマスタリポジトリへrsyncで同期：
- 隠しファイルを含む完全同期
- 生成ファイル（target/, node_modules/）を除外
- Git追跡対象として登録
- GitHubへプッシュ

#### STEP 14: サマリー表示
開発ワークフロー全体の実行結果をサマリー表示します。

## スクラッチビルドからの実行手順

EC2インスタンスを新規作成した場合やクリーンな状態から実行する手順：

### 1. CI/CD環境のセットアップ

```bash
cd /root/aws.git/container/claudecode/CICD

# 初回セットアップ（12ステップ）
./scripts/setup-from-scratch.sh

# GitLab Runner登録
sudo gitlab-runner register \
  --url http://YOUR_IP:5003 \
  --token YOUR_REGISTRATION_TOKEN \
  --executor shell \
  --description "CICD Shell Runner"

sudo systemctl enable --now gitlab-runner
```

### 2. CI/CD環境設定

```bash
# CI/CD環境変数設定（sudo必須）
sudo ./scripts/setup-cicd.sh
```

このスクリプトは以下を実行します：
- GitLab CI/CD変数の自動設定
- 環境変数の検証

### 3. sample-appプロジェクトの初期化

```bash
# sample-appプロジェクトをGitLabへ登録（通常ユーザー）
./scripts/setup-sample-app.sh
```

このスクリプトは以下を実行します：
- `sample-app/` を `/tmp/gitlab-sample-app/` へコピー
- Git初期化とGitLabリモート設定
- 初回コミット＆プッシュ
- CI/CDパイプライン自動実行

### 4. 開発ワークフローデモの実行

```bash
# 組織構成図機能の開発フロー実演（通常ユーザー）
./scripts/demo-development-workflow.sh
```

**重要**: 上記の順序（1→2→3→4）は必須です。特に、demo-development-workflow.sh は setup-sample-app.sh の実行後に /tmp/gitlab-sample-app が存在することを前提としています。

## トラブルシューティング

### エラー: GitLab接続不可

**原因**: GitLabサービスが起動していない

**解決方法**:
```bash
cd /root/aws.git/container/claudecode/CICD
sudo podman-compose up -d
sudo podman logs -f gitlab
```

### エラー: GitLab Runner not found

**原因**: GitLab Runnerが登録されていない

**解決方法**:
```bash
sudo gitlab-runner list
sudo gitlab-runner register --url http://YOUR_IP:5003 --token TOKEN --executor shell
sudo systemctl restart gitlab-runner
```

### エラー: Permission denied (.git/objects)

**原因**: `.git/` ディレクトリの所有者が不一致

**解決方法**:
```bash
sudo chown -R ec2-user:ec2-user /root/aws.git/.git/
```

### エラー: Maven build failure (401 Unauthorized)

**原因**: Nexus認証情報が不正

**解決方法**:
```bash
# .envファイルのパスワードを確認
cat .env | grep NEXUS_ADMIN_PASSWORD

# Maven設定ファイルを確認
cat config/maven/settings.xml
```

### エラー: Pipeline failed (coverage threshold)

**原因**: JaCoCoカバレッジが70%未満

**解決方法**:
```bash
# ローカルでカバレッジレポート確認
cd /tmp/gitlab-sample-app
mvn clean test jacoco:report
open backend/target/site/jacoco/index.html
```

## 成果物の確認

### 1. GitHub Issue

- URL: `https://github.com/shiftrepo/aws/issues/117`
- タイトル: `feat: 組織構成図の木構造表示機能追加`
- ステータス: Open → Closed（デプロイ完了後）

### 2. GitLab Merge Request

- URL: `http://YOUR_IP:5003/root/sample-app/-/merge_requests/N`
- ソースブランチ: `feature/organization-tree-view`
- ターゲットブランチ: `master`
- ステータス: Merged

### 3. GitLab CI/CD Pipeline

- URL: `http://YOUR_IP:5003/root/sample-app/-/pipelines`
- ステージ: build → test → coverage → sonarqube → package → deploy
- ステータス: Passed

### 4. Nexus Repository

- URL: `http://YOUR_IP:8082/#browse/browse:maven-snapshots`
- アーティファクト: `com/example/sample-app-backend/1.0.0-SNAPSHOT/`

### 5. SonarQube Analysis

- URL: `http://YOUR_IP:8000/dashboard?id=sample-org-management`
- カバレッジ: 70%以上
- バグ: 0件
- コードスメル: 最小限

### 6. デプロイ済みアプリケーション

- 組織一覧: `http://YOUR_IP:5006/`
- 組織構成図: `http://YOUR_IP:5006/organizations/1/tree`
- API: `http://YOUR_IP:5006/api/organizations/1/tree`

### 7. GitHub Repository

- URL: `https://github.com/shiftrepo/aws`
- ブランチ: `main`
- コミット: `feat: 組織構成図機能実装完了 - GitLabからマスタへ同期 (#117)`

## 開発フローの教育的価値

このデモスクリプトは以下の開発プラクティスを実演します：

1. **Issue Driven Development**: GitHubのIssueから開発開始
2. **Feature Branch Workflow**: フィーチャーブランチで独立した開発
3. **Test Driven Development**: テストカバレッジ70%維持
4. **Continuous Integration**: 全変更でCI/CDパイプライン実行
5. **Code Review Process**: Merge Requestによるレビュー
6. **Automated Deployment**: 承認後の自動デプロイ
7. **Repository Synchronization**: GitLab（開発） → GitHub（マスタ）同期

## カスタマイズ

### Issue番号の変更

スクリプト内の`ISSUE_NUMBER`変数を変更：

```bash
ISSUE_NUMBER="117"  # 任意のIssue番号に変更
```

### フィーチャーブランチ名の変更

```bash
FEATURE_BRANCH="feature/your-feature-name"
```

### デプロイ先ポートの変更

`nginx/nginx.conf` のプロキシ設定を変更：

```nginx
location /api/ {
    proxy_pass http://sample-backend:8080/api/;
}
```

## まとめ

このデモスクリプトにより、スクラッチビルドから以下のステップで完全な開発フローを再現できます：

1. **環境構築**: `setup-from-scratch.sh` → CI/CD環境完成
2. **初期化**: `run-sample-app-pipeline.sh` → GitLabプロジェクト作成
3. **開発デモ**: `demo-development-workflow.sh` → Issue → 実装 → CI/CD → デプロイ

このワークフローは、新しいメンバーへのオンボーディングやCI/CDデモンストレーションに最適です。
