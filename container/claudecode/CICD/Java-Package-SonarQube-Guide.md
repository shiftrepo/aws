# Javaマルチモジュール構成とSonarQube利用手順

## Javaの各パッケージの追加

### マルチモジュール構成をとっていることと特徴

本プロジェクトはMavenマルチモジュール構成を採用している。

**構成:**
```
project-root/
├── pom.xml          # 親POM (packaging=pom)
├── common/          # 共通モジュール
│   └── pom.xml
├── backend/         # バックエンドモジュール
│   └── pom.xml
└── frontend/        # フロントエンドモジュール
```

**特徴:**
- 親POMで全体の依存関係とバージョンを管理
- 各モジュールは独立してビルド・テスト可能
- モジュール間の依存関係を明示的に定義
- 段階的ビルド（依存関係順に実行）

### パッケージを追加するときの留意点

**1. 親POMへのモジュール登録**
```xml
<modules>
    <module>common</module>
    <module>backend</module>
    <module>new-module</module>  <!-- 新規追加 -->
</modules>
```

**2. 新規モジュールのpom.xml作成**
```xml
<parent>
    <groupId>com.example</groupId>
    <artifactId>sample-app-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</parent>
<artifactId>new-module</artifactId>
```

**3. 依存関係管理**
- 循環依存を避ける
- 親POMのdependencyManagementでバージョン統一
- モジュール間依存は必要最小限に抑える

### 全体と個別パッケージのmvn実行

**全体実行（プロジェクトルートで実行）**
```bash
mvn clean install          # 全モジュールビルド
mvn clean test            # 全モジュールテスト
mvn clean package         # 全モジュールパッケージング
```

**個別モジュール実行**
```bash
# 特定モジュールのみ
mvn clean install -pl backend

# 複数モジュール指定
mvn clean install -pl common,backend

# 依存モジュールも含めて実行
mvn clean install -pl backend -am

# モジュール内で実行
cd backend
mvn clean test
```

## SonarQubeの利用

### 基本方針

- **CI**: 定期的にプロジェクト全体に実施する
- **ローカル開発**: 各自各モジュール単位に適宜mvnもしくはsonar-scannerコマンドで実行する
- **IDE**: 無償プラグインで簡易的なチェックが可能。修正しやすい。Copilotとコピペなどで連携しやすい

### projectKey と projectName

**projectKey（固定値）**
- `courts`: CI用
- `RDX`: RDXさん用
- `TDC`: TDCさん用

**projectName（任意設定）**
- projectページの結果名になるので、後から見やすいように適宜設定する

### Maven経由での実行

**コマンド例:**
```bash
mvn clean verify sonar:sonar -Dsonar.projectKey=TDC -Dsonar.projectName="TDC PJ" -Dsonar.host.url=http://10.47.3.40:9000 -Dsonar.login=sqa_067386753555cfe95b2857ec8619dffed4588f2a
```

### sonar-scanner コマンドライン実行

**ダウンロード先:**
https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/scanners/sonarscanner

**sonar-project.properties設定:**
```properties
sonar.projectKey=courts
sonar.projectName=courts
sonar.sources=src
sonar.java.binaries=target/classes
sonar.host.url=http://10.47.3.40:9000
sonar.login=sqa_067386753555cfe95b2857ec8619dffed4588f2a
```

**実行:**
```bash
sonar-scanner
```

### IDE無償プラグイン

- **IntelliJ IDEA**: SonarLint プラグイン
- **Eclipse**: SonarLint プラグイン
- **VS Code**: SonarLint 拡張機能

リアルタイムでの品質チェックが可能。Copilotとの連携で効率的な修正が可能。