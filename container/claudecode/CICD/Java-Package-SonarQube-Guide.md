# Javaマルチモジュール構成におけるパッケージ追加とSonarQube活用ガイド

## 1. Javaマルチモジュール構成の概要と特徴

### 1.1 マルチモジュール構成とは

マルチモジュール構成は、一つのプロジェクト内で複数の関連するモジュール（サブプロジェクト）を管理する構成です。各モジュールは独立したpom.xmlを持ち、親POMで全体を統括します。

**基本構造例：**
```
project-root/
├── pom.xml                    # 親POM（packaging=pom）
├── common/                    # 共通モジュール
│   ├── pom.xml
│   └── src/
├── backend/                   # バックエンドモジュール
│   ├── pom.xml
│   └── src/
└── frontend/                  # フロントエンドモジュール（オプション）
    ├── package.json
    └── src/
```

### 1.2 マルチモジュールの特徴とメリット

**特徴：**
- **依存関係の明確化**: モジュール間の依存関係が明示される
- **独立性**: 各モジュールが独立してビルド・テスト可能
- **再利用性**: 共通機能を別モジュールとして分離・再利用
- **段階的ビルド**: 依存関係順にビルドが実行される

**メリット：**
- コードの整理とメンテナンス性向上
- チーム開発での役割分担が明確
- 部分的なビルドによる開発効率向上
- マイクロサービス移行の準備段階としても有効

**デメリット：**
- 初期設定が複雑
- 依存関係管理の注意が必要
- IDE設定が複雑になる場合がある

### 1.3 典型的なモジュール構成パターン

**3層アーキテクチャパターン：**
- `common`: DTO、Entity、共通ユーティリティ
- `service`: ビジネスロジック層
- `web`: Webアプリケーション層（Controller）

**ドメイン駆動設計パターン：**
- `shared-kernel`: 共通ドメインモデル
- `user-domain`: ユーザードメイン
- `order-domain`: 注文ドメイン
- `infrastructure`: インフラストラクチャ層

## 2. パッケージを追加するときの留意点

### 2.1 新規モジュール追加手順

**Step 1: 親POMへのモジュール登録**
```xml
<!-- pom.xml（親POM） -->
<modules>
    <module>common</module>
    <module>backend</module>
    <module>new-module</module>  <!-- 新規モジュール追加 -->
</modules>
```

**Step 2: 新規モジュールのpom.xml作成**
```xml
<!-- new-module/pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- 親POMの継承 -->
    <parent>
        <groupId>com.example</groupId>
        <artifactId>sample-app-parent</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>

    <artifactId>new-module</artifactId>
    <packaging>jar</packaging>
    <name>New Module</name>

    <dependencies>
        <!-- 他モジュールへの依存 -->
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>common</artifactId>
        </dependency>
    </dependencies>
</project>
```

**Step 3: ディレクトリ構造作成**
```
new-module/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/
    │   │   └── com/example/newmodule/
    │   └── resources/
    └── test/
        ├── java/
        │   └── com/example/newmodule/
        └── resources/
```

### 2.2 依存関係管理の留意点

**循環依存の回避**
```xml
<!-- ❌ 循環依存になる例 -->
<!-- module-a が module-b に依存 -->
<!-- module-b が module-a に依存 -->
```

**適切な依存関係の例**
```xml
<!-- ✅ 正しい依存関係 -->
<!-- common ← service ← web の順序 -->
```

**dependencyManagementの活用**
```xml
<!-- 親POMでバージョン管理 -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>common</artifactId>
            <version>${project.version}</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 2.3 パッケージ命名規則

**推奨命名パターン：**
- `com.company.project.module.layer.functionality`
- 例：`com.example.ecommerce.user.service.UserService`

**モジュール別パッケージ例：**
```
common/
└── src/main/java/
    └── com/example/project/
        ├── dto/
        ├── entity/
        └── util/

backend/
└── src/main/java/
    └── com/example/project/backend/
        ├── controller/
        ├── service/
        └── repository/
```

## 3. Maven実行パターン

### 3.1 全体でのMaven実行

**プロジェクトルートでの実行**
```bash
# 全モジュールのクリーンビルド
mvn clean install

# 全モジュールのテスト実行
mvn clean test

# 全モジュールのパッケージング
mvn clean package

# 依存関係付きでのコンパイル
mvn clean compile dependency:resolve

# 全モジュールのデプロイ
mvn clean deploy
```

**並列ビルド（高速化）**
```bash
# 4スレッドで並列実行
mvn clean install -T 4

# CPUコア数で自動並列実行
mvn clean install -T 1C
```

### 3.2 個別モジュールでのMaven実行

**特定モジュールのみ実行**
```bash
# プロジェクトルートから特定モジュールのみ
mvn clean install -pl backend

# 複数モジュールを指定
mvn clean install -pl common,backend

# 依存モジュールも含めて実行
mvn clean install -pl backend -am

# 特定モジュール以外を実行
mvn clean install -pl !frontend
```

**モジュール内での実行**
```bash
# モジュールディレクトリ内で実行
cd backend
mvn clean test

# 親POMのプロファイルを使用
mvn clean test -P development
```

### 3.3 高度な実行パターン

**条件付きビルド**
```bash
# テストスキップ
mvn clean install -DskipTests

# 特定テストクラスのみ実行
mvn test -Dtest=UserServiceTest

# プロファイル指定
mvn clean install -P production

# システムプロパティ指定
mvn clean install -Dspring.profiles.active=local
```

**トラブルシューティング**
```bash
# 詳細ログ出力
mvn clean install -X

# 依存関係ツリー表示
mvn dependency:tree

# 有効なプロファイル表示
mvn help:active-profiles

# 依存関係の競合チェック
mvn dependency:analyze
```

## 4. SonarQubeの効果的な利用方法

### 4.1 SonarQubeの活用戦略

**CI/CDでの定期実行**
- プロジェクト全体に対して定期的（nightly build等）に実行
- 全体的な品質トレンドの監視
- 新規バグ・脆弱性の早期発見

**開発時のローカル実行**
- 個別モジュール単位での迅速なチェック
- 開発サイクル内での品質確保
- コードレビュー前の事前チェック

**IDE連携**
- 無償プラグインによるリアルタイムチェック
- Copilotやコード補完との連携
- 修正提案の即座適用

### 4.2 Maven経由でのSonarQube実行

**基本的な実行コマンド**
```bash
# プロジェクト全体の分析
mvn clean verify sonar:sonar \
  -Dsonar.projectKey=my-project \
  -Dsonar.projectName="My Project" \
  -Dsonar.host.url=http://sonarqube-server:9000 \
  -Dsonar.token=sqa_xxxxxxxxxx

# 個別モジュールの分析
cd backend
mvn clean verify sonar:sonar \
  -Dsonar.projectKey=my-project-backend \
  -Dsonar.projectName="My Project Backend"

# JaCoCo カバレッジ込みの分析
mvn clean test jacoco:report sonar:sonar
```

**プロファイルを使った設定**
```xml
<!-- pom.xmlでのプロファイル設定 -->
<profiles>
    <profile>
        <id>sonar</id>
        <properties>
            <sonar.host.url>http://localhost:9000</sonar.host.url>
            <sonar.projectKey>my-project</sonar.projectKey>
            <sonar.projectName>My Project</sonar.projectName>
        </properties>
    </profile>
</profiles>
```

```bash
# プロファイル使用
mvn clean verify sonar:sonar -P sonar -Dsonar.token=sqa_xxxxxxxxxx
```

### 4.3 sonar-scannerコマンドライン実行

**sonar-scanner インストール**
1. [SonarQube Scanner](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/scanners/sonarscanner)からダウンロード
2. PATHに追加
3. sonar-project.propertiesファイルを作成

**sonar-project.propertiesの設定例**
```properties
# プロジェクト基本情報
sonar.projectKey=courts
sonar.projectName=courts
sonar.projectVersion=1.0.0

# ソースコード設定
sonar.sources=src
sonar.java.binaries=target/classes
sonar.java.libraries=target/dependency/*.jar

# テスト設定
sonar.tests=src/test
sonar.junit.reportPaths=target/surefire-reports

# カバレッジ設定
sonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml

# SonarQubeサーバー設定
sonar.host.url=http://10.47.3.40:9000
sonar.token=sqa_067386753555cfe95b2857ec8619dffed4588f2a

# 除外設定
sonar.exclusions=**/*Test.java,**/target/**
sonar.coverage.exclusions=**/dto/**,**/entity/**
```

**実行コマンド**
```bash
# sonar-project.propertiesを使用
sonar-scanner

# コマンドラインで直接指定
sonar-scanner \
  -Dsonar.projectKey=my-project \
  -Dsonar.sources=src \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=sqa_xxxxxxxxxx
```

### 4.4 プロジェクトキーとプロジェクト名の管理

**プロジェクトキーの命名規則**
```bash
# 環境別キー例
courts-dev      # 開発環境
courts-staging  # ステージング環境
courts-prod     # 本番環境

# チーム別キー例
RDX            # RDXチーム用
TDC            # TDCチーム用
courts         # CI用（共通）

# モジュール別キー例
courts-backend    # バックエンドモジュール
courts-frontend   # フロントエンドモジュール
courts-common     # 共通モジュール
```

**プロジェクト名の設定例**
```bash
# 分かりやすい表示名を設定
-Dsonar.projectName="Courts Project - Backend"
-Dsonar.projectName="TDC Development Environment"
-Dsonar.projectName="RDX Integration Testing"
```

### 4.5 IDEプラグインの活用

**IntelliJ IDEA SonarLint**
1. Plugins → SonarLint で検索・インストール
2. Connected Mode でSonarQubeサーバーと連携
3. リアルタイムでの品質チェック
4. Quick Fix による自動修正提案

**Eclipse SonarLint**
1. Help → Eclipse Marketplace → SonarLint で検索・インストール
2. Window → Preferences → SonarLint でサーバー設定
3. Project Properties → SonarLint でプロジェクト紐付け

**VS Code SonarLint**
1. Extensions → SonarLint で検索・インストール
2. Settings → SonarLint でサーバー設定
3. Problems パネルでの問題確認

### 4.6 カバレッジとJaCoCoとの連携

**JaCoCoレポートの生成**
```bash
# テスト実行とカバレッジレポート生成
mvn clean test jacoco:report

# カバレッジファイルの確認
ls target/site/jacoco/

# HTML レポート確認
open target/site/jacoco/index.html
```

**SonarQubeでのカバレッジ表示**
```xml
<!-- pom.xmlでの設定 -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <configuration>
        <excludes>
            <!-- DTO/Entityを除外 -->
            <exclude>**/dto/**</exclude>
            <exclude>**/entity/**</exclude>
        </excludes>
    </configuration>
</plugin>
```

### 4.7 品質ゲート設定のベストプラクティス

**段階的な品質基準**
```
開発初期: カバレッジ 50%、重大バグ 0
安定期  : カバレッジ 70%、重大バグ 0、コードスメル < 100
リリース: カバレッジ 80%、重大バグ 0、コードスメル < 50
```

**品質ゲート失敗時の対応**
1. SonarQubeダッシュボードで詳細確認
2. 優先度の高い問題から対応
3. テストカバレッジの不足分を追加
4. 再分析で品質改善を確認

## 5. 開発フローでの活用例

### 5.1 日常開発での活用

**朝の開発開始時**
```bash
# 最新コードの取得と全体ビルド
git pull origin main
mvn clean install

# 昨日のCI結果確認
curl -u admin:token http://sonarqube:9000/api/projects/search
```

**機能開発中**
```bash
# 対象モジュールのローカルテスト
cd backend
mvn clean test -Dtest=*UserService*

# SonarLintでのリアルタイムチェック（IDE）
# 修正後のローカル分析
mvn clean verify sonar:sonar -Dsonar.projectKey=local-dev
```

**コミット前**
```bash
# 全モジュールのテストとカバレッジチェック
mvn clean test jacoco:report
mvn jacoco:check

# SonarQube分析（ローカル）
mvn sonar:sonar -Dsonar.projectKey=pre-commit-check
```

### 5.2 チーム開発での活用

**プルリクエスト時**
- SonarQube PR Decoration機能でコードレビュー支援
- 新規コードのみの品質チェック
- レビュワーへの品質情報提供

**定期的な品質会議**
- プロジェクト全体の品質トレンド確認
- 技術的負債の可視化と対応計画
- 品質ゲート基準の見直し

これらの手順に従うことで、マルチモジュール構成でのJava開発における品質管理を効率的に実施できます。特に、SonarQubeの段階的活用により、開発速度を保ちながら高品質なコードの維持が可能になります。