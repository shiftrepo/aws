# 🚀 CI/CD ハンズオン チュートリアル

## 概要
このチュートリアルでは、GitLabからプロジェクトをクローンし、コードを修正してプッシュすることで、**CI/CDパイプラインが自動実行される流れ** を実際に体験します。

---

## 🔗 サービスアクセス情報

### 各サービスURL・ログイン情報

| サービス | URL | ユーザー名 | 用途 |
|----------|-----|------------|------|
| **GitLab** | http://${EC2_PUBLIC_IP}:5003 | `root` | ソースコード管理・CI/CD |
| **SonarQube** | http://${EC2_PUBLIC_IP}:8000 | `admin` | 品質・静的解析 |
| **Nexus Repository** | http://${EC2_PUBLIC_IP}:8082 | `admin` | 成果物・依存関係管理 |
| **pgAdmin** | http://${EC2_PUBLIC_IP}:5002 | `admin@example.com` | データベース管理UI |

### PostgreSQL データベース接続情報（pgAdmin用）

| データベース名 | ユーザー名 | 用途 | 接続ホスト |
|----------------|------------|------|------------|
| **cicddb** | `cicduser` | メインCI/CD DB | `${EC2_PUBLIC_IP}:5001` |
| **gitlabhq** | `gitlab` | GitLabデータ | `${EC2_PUBLIC_IP}:5001` |
| **sonardb** | `sonaruser` | SonarQube解析DB | `${EC2_PUBLIC_IP}:5001` |
| **sampledb** | `sampleuser` | サンプルアプリDB | `${EC2_PUBLIC_IP}:5001` |

> ⚠️ **注意**: pgAdminでDB接続時、ユーザーIDとパスワードの入力を求められた場合があります

### アプリケーションURL

| アプリケーション | URL | 説明 |
|------------------|-----|------|
| **Frontend App** | http://${EC2_PUBLIC_IP}:3000 | React組織管理システム |
| **Backend API** | http://${EC2_PUBLIC_IP}:8501 | Spring Boot REST API |
| **Swagger UI** | http://${EC2_PUBLIC_IP}:8501/swagger-ui.html | API仕様・テスト画面 |

> 💡 **Tip**: ブックマークに登録しておくと便利です！

> ⚠️ **現在の制限事項**:
> - CI/CDパイプラインからの自動デプロイは部分的対応のため、手動デプロイが必要
> - Frontend-Backend間のCORS設定等に不備があり、画面でAPIエラーが発生する場合があります

---

## 🎯 学習目標
- Git の基本操作（clone, commit, push）
- GitLab でのプロジェクト管理
- CI/CDパイプラインの実行・監視
- テスト実行・品質チェック・成果物管理の理解

---

## 📋 事前準備

### 1. 必要なツール
- **Git** - コマンドラインツール
- **テキストエディタ** - VS Code, IntelliJ, vim など
- **ブラウザ** - GitLab UI アクセス用

### 2. 環境情報の確認
```bash
# 環境変数の確認
echo $EC2_PUBLIC_IP

# サービスURL（ブラウザで開いて確認）
GitLab:    http://${EC2_PUBLIC_IP}:5003
Nexus:     http://${EC2_PUBLIC_IP}:8082
SonarQube: http://${EC2_PUBLIC_IP}:8000
```

### 3. GitLabアクセス確認
- URL: http://${EC2_PUBLIC_IP}:5003
- ユーザー: `root`

---

## 🏁 Step 1: 学習プロジェクトの確認

### 1.1 学習用プロジェクトを確認

1. **GitLab にアクセス**
   - ブラウザで `http://${EC2_PUBLIC_IP}:5003` を開く
   - ユーザー: `root` でログイン

2. **学習用プロジェクトを探す**
   - GitLab ホーム画面で "Your projects" セクションを確認
   - 以下のような名前のプロジェクトを見つけます：
     - `sample-app-frontend-YYYYMMDD-HHMMSS`
     - `sample-app-backend-YYYYMMDD-HHMMSS`

3. **プロジェクト構造を理解**
   - **Frontend プロジェクト**: React アプリケーション
   - **Backend プロジェクト**: Spring Boot API

### 1.2 CI/CD パイプライン状況確認

各プロジェクトをクリックして以下を確認：

1. **CI/CD → Pipelines** をクリック
2. パイプライン実行履歴を確認
3. 各ステージ（install, lint, test等）の実行状況を観察

---

## 🔄 Step 2: Frontend プロジェクトの操作

### 2.1 プロジェクトをクローン

```bash
# 作業ディレクトリ作成
mkdir -p ~/learning-workspace
cd ~/learning-workspace

# Frontendプロジェクトをクローン（URLは上記の実行結果から取得）
git clone http://${EC2_PUBLIC_IP}:5003/root/sample-app-frontend-YYYYMMDD-HHMMSS.git frontend-project
# 認証が求められた場合、GitLabのユーザー名・パスワードを入力

# ディレクトリ移動
cd frontend-project

# ファイル構造確認
ls -la
```

**ファイル構造**:
```
├── .gitlab-ci.yml     # CI/CD パイプライン定義
├── package.json       # npm 依存関係
├── vite.config.js     # Vite 設定
├── src/               # ソースコード
│   ├── components/    # React コンポーネント
│   ├── pages/         # ページコンポーネント
│   └── App.jsx        # メインアプリ
└── public/            # 静的ファイル
```

### 2.2 パイプライン設定の確認

```bash
# CI/CD設定ファイル確認
cat .gitlab-ci.yml
```

**パイプライン構成**:
```yaml
stages:
  - install      # 依存関係インストール
  - lint         # ESLintによるコード品質チェック
  - test         # Jest単体テスト
  - sonar        # SonarQube品質分析
  - build        # Vite本番ビルド
  - nexus-deploy # Nexusに成果物アップロード
```

---

## ✏️ Step 3: コード修正体験

### 3.1 簡単な修正（メッセージ変更）

```bash
# メインページを編集
vim src/pages/Home.jsx
```

**修正例** - タイトルを変更:
```jsx
// 修正前
<h1>組織管理システム</h1>

// 修正後
<h1>組織管理システム - 学習版</h1>
```

### 3.2 テストケース修正

```bash
# テストファイル編集
vim src/components/__tests__/UserList.test.jsx
```

**修正例** - テストケース追加:
```javascript
// 既存のテストに追加
test('should display correct title', () => {
  render(<App />);
  expect(screen.getByText('組織管理システム - 学習版')).toBeInTheDocument();
});
```

### 3.3 ローカルでのテスト実行（任意）

```bash
# 依存関係インストール
npm ci

# テスト実行
npm run test

# Lint実行
npm run lint

# ビルド実行
npm run build
```

---

## 📤 Step 4: 変更をプッシュ

### 4.1 変更をコミット

```bash
# 変更ファイル確認
git status

# 変更をステージング
git add src/pages/Home.jsx
git add src/components/__tests__/UserList.test.jsx

# コミット
git commit -m "feat: タイトルを学習版に変更 + テスト追加

- メインページのタイトルに「学習版」を追加
- タイトル表示のテストケースを追加"

# プッシュ（認証が求められた場合、GitLabのユーザー名・パスワードを入力）
git push origin master
```

### 4.2 パイプライン実行の監視

1. **GitLab UI でパイプライン確認**
   ```
   http://${EC2_PUBLIC_IP}:5003/root/sample-app-frontend-YYYYMMDD-HHMMSS/-/pipelines
   ```

2. **各ステージの進行を観察**
   - install: 依存関係インストール
   - lint: ESLint実行
   - test: Jest テスト実行
   - sonar: SonarQube 品質分析
   - build: Vite ビルド
   - nexus-deploy: Nexus アップロード

---

## 📊 Step 5: 結果の確認

### 5.1 パイプライン結果確認

**各ステージの詳細確認**:
- ✅ **成功時**: 緑色のチェックマーク
- ❌ **失敗時**: 赤色のバツマーク（ログで原因確認）

**ログ確認方法**:
1. パイプラインページでステージをクリック
2. ジョブをクリックしてログ表示
3. エラーの原因を特定

### 5.2 品質レポート確認

**SonarQube レポート**:
```
http://${EC2_PUBLIC_IP}:8000/projects
```
- プロジェクト: `sample-app-frontend`
- カバレッジ率、品質評価を確認

**テスト結果**:
- GitLab の Test タブでテスト結果確認
- カバレッジレポート表示

### 5.3 成果物確認

**Nexus Repository**:
```
http://${EC2_PUBLIC_IP}:8082
```
- Browse → raw-hosted → frontend
- `frontend-latest.tar.gz` が作成されていることを確認

---

## 🔄 Step 6: Backend プロジェクトの操作

### 6.1 Backend プロジェクトクローン

```bash
cd ~/learning-workspace

# Backendプロジェクトをクローン
git clone http://${EC2_PUBLIC_IP}:5003/root/sample-app-backend-YYYYMMDD-HHMMSS.git backend-project
# 認証が求められた場合、GitLabのユーザー名・パスワードを入力

cd backend-project
ls -la
```

### 6.2 Java コード修正

```bash
# ユーザーサービス編集
vim backend/src/main/java/com/example/service/UserService.java
```

**修正例** - 新しいメソッド追加:
```java
/**
 * ユーザー数を取得
 */
public long countUsers() {
    return userRepository.count();
}
```

### 6.3 テストケース追加

```bash
# テストクラス編集
vim backend/src/test/java/com/example/service/UserServiceTest.java
```

**修正例**:
```java
@Test
void shouldCountUsersCorrectly() {
    // Given
    User user1 = new User();
    user1.setName("テストユーザー1");
    userRepository.save(user1);

    User user2 = new User();
    user2.setName("テストユーザー2");
    userRepository.save(user2);

    // When
    long count = userService.countUsers();

    // Then
    assertThat(count).isEqualTo(2);
}
```

### 6.4 変更をプッシュ

```bash
git add .
git commit -m "feat: ユーザー数取得機能とテストを追加

- UserService にユーザー数取得メソッド追加
- 対応するテストケース追加"

git push origin master
```

### 6.5 Backend パイプライン確認

```
http://${EC2_PUBLIC_IP}:5003/root/sample-app-backend-YYYYMMDD-HHMMSS/-/pipelines
```

**7ステージの進行確認**:
1. build: Maven コンパイル
2. test: JUnit テスト実行
3. coverage: JaCoCo カバレッジ
4. sonar: SonarQube 品質分析
5. package: JAR パッケージ作成
6. nexus-deploy: Nexus アップロード
7. container-deploy: アプリケーションデプロイ

---

## 🐛 Step 7: 意図的な失敗体験

### 7.1 テスト失敗を体験

```bash
# テストを失敗させる
vim backend/src/test/java/com/example/service/UserServiceTest.java
```

**失敗例**:
```java
@Test
void shouldFailIntentionally() {
    // 意図的に失敗するテスト
    assertThat(1).isEqualTo(2);
}
```

```bash
git add .
git commit -m "test: 意図的なテスト失敗で学習"
git push origin master
```

### 7.2 失敗時の対応学習

1. **パイプライン失敗確認**
   - 赤いバツマークの確認
   - ログでエラー内容確認

2. **修正・再実行**
```bash
# テストを修正
vim backend/src/test/java/com/example/service/UserServiceTest.java

# 修正版
@Test
void shouldPassAfterFix() {
    // 正しいテスト
    assertThat(1).isEqualTo(1);
}

git add .
git commit -m "fix: テストを修正"
git push origin master
```

---

## 🌐 Step 8: 実際のWebアプリケーション確認

### 8.1 デプロイされたアプリケーションの確認

CI/CDパイプラインで構築された実際のWebアプリケーションを確認しましょう。

**アプリケーションアクセス**:
```bash
# デプロイスクリプトでアプリケーション起動
cd /root/aws.git/container/claudecode/CICD
./scripts/deploy-applications.sh
```

### 8.2 組織管理システム（Frontend）

**アクセスURL**: http://${EC2_PUBLIC_IP}:3000

**確認できる機能**:
- 📋 **組織一覧表示** - テクノロジー株式会社、ビジネスソリューションズ
- 🏢 **組織詳細情報** - 企業説明、作成日時等
- ➕ **管理UI** - 追加・編集・削除のインターフェース
- 📱 **レスポンシブデザイン** - PC・モバイル対応

### 8.3 REST API（Backend）

**アクセスURL**:
- API: http://${EC2_PUBLIC_IP}:8501
- Swagger UI: http://${EC2_PUBLIC_IP}:8501/swagger-ui.html

**API エンドポイント例**:
```bash
# 組織一覧取得
curl http://${EC2_PUBLIC_IP}:8501/api/organizations

# ヘルスチェック
curl http://${EC2_PUBLIC_IP}:8501/actuator/health
```

### 8.4 現在の制限事項と学習ポイント

**⚠️ 現在の状況**:
- **デプロイ**: CI/CDパイプライン → Nexus → 手動デプロイスクリプト
- **表示**: Reactアプリは正常表示されるが、APIエラーが発生する場合あり
- **原因**: CORS設定、環境変数、ネットワーク設定等の統合課題

**💡 学習ポイント**:
- CI/CDパイプラインによる成果物生成プロセス
- Frontend（React）とBackend（Spring Boot）の分離アーキテクチャ
- 実際の統合時に発生する課題（CORS、環境設定等）
- 段階的なデプロイとテストの重要性

---

## 📚 Step 9: 学習の振り返り

### 9.1 学んだ内容のチェック

- [ ] Gitの基本操作（clone, add, commit, push）
- [ ] GitLab でのプロジェクト管理
- [ ] CI/CDパイプラインの実行・監視
- [ ] テストの重要性・失敗時の対応
- [ ] 品質チェック（ESLint, SonarQube）
- [ ] 成果物管理（Nexus）

- [ ] 実際のWebアプリケーション動作確認
- [ ] アプリケーション統合課題の理解（CORS等）

### 9.2 次のステップ提案

**初級**:
- [ ] 他のコンポーネントに機能追加
- [ ] テストカバレッジを90%以上に向上
- [ ] ESLint ルール違反の修正

**中級**:
- [ ] 新しいページ・API エンドポイント追加
- [ ] データベースマイグレーション作成
- [ ] パフォーマンステスト実装

**上級**:
- [ ] セキュリティテスト実装
- [ ] パイプライン設定のカスタマイズ
- [ ] マイクロサービス分離設計

---

## 🚨 よくあるトラブルと対処法

### パイプライン失敗
```bash
# ローカルでテスト実行
npm test  # Frontend
mvn test  # Backend

# エラー修正後再プッシュ
git add .
git commit -m "fix: テストエラーを修正"
git push origin master
```

### Git 認証エラー
```bash
# リモートURL確認・設定
git remote -v
git remote set-url origin http://${EC2_PUBLIC_IP}:5003/root/project-name.git

# 認証が求められた場合、ユーザー名・パスワードを入力
```

### Merge Conflict
```bash
# 最新をプル
git pull origin master

# コンフリクト解決後
git add .
git commit -m "resolve: マージコンフリクト解決"
git push origin master
```

---

## 🎉 完了！

おめでとうございます！CI/CDパイプラインの基本的な流れを体験できました。

**次の学習**:
- `CICD_LEARNING_GUIDE.md` の Phase 3 以降に進んで、より実践的な開発を体験
- 実際のWebアプリケーション（http://${EC2_PUBLIC_IP}:3000）で組織管理システムを確認
- デプロイスクリプト（`./scripts/deploy-applications.sh`）でアプリケーション環境構築体験

---

## 📖 参考資料

- **GitLab CI/CD**: http://${EC2_PUBLIC_IP}:5003/help/ci/README.md
- **Jest テスト**: https://jestjs.io/docs/getting-started
- **JUnit 5**: https://junit.org/junit5/docs/current/user-guide/
- **Spring Boot**: https://spring.io/projects/spring-boot#learn
- **React**: https://react.dev/learn