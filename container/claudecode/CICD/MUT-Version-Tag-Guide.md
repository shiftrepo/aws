# MUTのバージョンタグ管理ガイド

## 1. バージョン管理の基本方針

### 1.1 バージョン付与ルール

**基本設計書に基づくバージョン構成**
- **メジャーバージョン**: 大きな機能追加・変更
- **マイナーバージョン**: 機能追加・改修
- **リビジョン**: 任意のタイミングでの内部用管理

**運用ルール**
```
基本運用: メジャー.マイナー (例: 1.0, 0.2)
内部管理: メジャー.マイナー.リビジョン (例: 1.0.1, 0.2.3)
```

### 1.2 セマンティックバージョニングとの関係

**標準的なセマンティックバージョニング**
```
MAJOR.MINOR.PATCH
- MAJOR: 互換性のない変更
- MINOR: 後方互換性のある機能追加
- PATCH: 後方互換性のあるバグ修正
```

**MUTプロジェクトでの適用**
```
メジャー.マイナー.リビジョン
- メジャー: プロジェクトの大きな節目
- マイナー: 機能・フェーズの完成
- リビジョン: 内部的な進捗管理（オプション）
```

## 2. MUTプロジェクトのバージョンロードマップ

### 2.1 開発フェーズ別バージョン計画

| バージョン | 完成目標 | 主要マイルストーン | CI/CD戦略 |
|-----------|---------|------------------|-----------|
| **0.1.0** | JavaのCI化 | - Mavenビルド自動化<br>- JUnit テスト実行<br>- JaCoCo カバレッジ取得<br>- SonarQube 品質チェック | 定期実行のみ<br>プッシュトリガー無効 |
| **0.2.0** | JavaScriptのCI化 | - Node.js ビルド自動化<br>- Jest テスト実行<br>- ESLint 静的解析<br>- フロントエンド品質チェック | 定期実行のみ<br>プッシュトリガー無効 |
| **0.3.0** | 基本ルートの登録 | - REST API エンドポイント実装<br>- フロントエンド画面実装<br>- 統合テスト実装<br>- E2Eテスト基盤 | 定期実行のみ<br>手動実行可能 |
| **0.4.0** | 実行環境デプロイと起動確認 | - コンテナ化対応<br>- デプロイメント自動化<br>- 環境構築スクリプト<br>- 動作確認テスト | 定期実行<br>デプロイテスト有効 |
| **0.5.0** | IT向けCICD完全版 | - ArgoCDとの統合<br>- GitOps ワークフロー<br>- 本格的なデプロイメントパイプライン<br>- インフラ as Code | 完全自動化<br>プッシュトリガー有効 |
| **1.0.0** | 最終納品向けCIクリア版 | - 全品質ゲート通過<br>- ドキュメント完成<br>- 納品準備完了<br>- 本番運用可能 | 本番レベルCI/CD<br>完全品質保証 |

### 2.2 各フェーズの詳細説明

#### 0.1.0: JavaのCI化フェーズ

**達成目標**
- Maven ベースの自動化ビルド基盤の確立
- バックエンドコードの品質保証体制構築

**技術的成果物**
```xml
<!-- Maven 設定完成 -->
- pom.xml の多モジュール構成
- JaCoCo カバレッジ設定
- SonarQube Maven プラグイン設定
- Surefire テストプラグイン設定
```

**品質指標**
- JUnit テストカバレッジ: 70% 以上
- SonarQube 品質ゲート: 通過
- ビルド成功率: 95% 以上

**CI/CD 設定**
```yaml
# CI定期実行のみ（プッシュトリガー無効）
schedule: "0 2 * * *"  # 毎日深夜2時実行
trigger_on_push: false
```

#### 0.2.0: JavaScriptのCI化フェーズ

**達成目標**
- フロントエンド開発の自動化基盤確立
- JavaScript/TypeScript コードの品質保証

**技術的成果物**
```json
{
  "scripts": {
    "build": "vite build",
    "test": "jest --coverage",
    "lint": "eslint src/",
    "sonar": "sonar-scanner"
  }
}
```

**品質指標**
- Jest テストカバレッジ: 70% 以上
- ESLint エラー: 0件
- TypeScript コンパイルエラー: 0件

#### 0.3.0: 基本ルート登録フェーズ

**達成目標**
- アプリケーションの基本機能実装
- フロントエンド・バックエンドの連携確立

**機能的成果物**
```
API エンドポイント:
- GET  /api/organizations
- POST /api/organizations
- GET  /api/users
- POST /api/users

フロントエンド画面:
- 組織一覧画面
- ユーザー一覧画面
- 基本的なCRUD操作
```

**統合テスト**
- API結合テスト
- E2Eテスト基盤（Playwright/Cypress）

#### 0.4.0: 実行環境デプロイフェーズ

**達成目標**
- コンテナベースのデプロイメント実現
- 実行環境での動作確認体制確立

**技術的成果物**
```dockerfile
# アプリケーションコンテナ化
FROM openjdk:17-jre
COPY target/*.jar app.jar
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
```

**デプロイメント**
- Docker/Podman コンテナ対応
- 環境別設定管理
- ヘルスチェック機能

#### 0.5.0: IT向けCICD完全版フェーズ

**達成目標**
- エンタープライズレベルのCI/CD基盤完成
- GitOpsによる運用自動化

**技術的成果物**
```yaml
# ArgoCD Application設定
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mut-application
spec:
  project: default
  source:
    repoURL: https://git.example.com/mut
    path: k8s/
    targetRevision: HEAD
  destination:
    server: https://kubernetes.default.svc
    namespace: production
```

**CI/CD 完全自動化**
- プッシュトリガーによる自動デプロイ
- 段階的リリース（Blue-Green, Canary）
- 自動ロールバック機能

#### 1.0.0: 最終納品版フェーズ

**達成目標**
- 本番運用レベルの品質・安定性確保
- 完全なドキュメンテーション

**品質指標**
- テストカバレッジ: 90% 以上
- SonarQube 品質ゲート: すべて通過
- セキュリティスキャン: クリティカル脆弱性 0件
- パフォーマンステスト: 要件クリア

**運用準備**
- 運用手順書完成
- 障害対応手順書
- 監視・アラート設定
- バックアップ・リストア手順

## 3. CI/CD実行戦略

### 3.1 フェーズ別CI/CD実行方針

**0.4.0まで（開発・検証フェーズ）**
```yaml
CI実行戦略:
  定期実行: 有効（毎日実施）
  プッシュトリガー: 無効
  手動実行: 有効

品質チェック方法:
  - 各自でローカルJaCoCo実行
  - 各自でローカルSonarQube分析
  - 定期CIのcourtsプロジェクト結果確認
```

**0.5.0以降（IT統合・本番フェーズ）**
```yaml
CI実行戦略:
  定期実行: 有効
  プッシュトリガー: 有効（自動デプロイ）
  PR/MRトリガー: 有効

品質チェック方法:
  - 自動品質ゲートチェック
  - 自動デプロイメント
  - 自動テスト実行
```

### 3.2 品質保証戦略

**段階的品質基準**

| フェーズ | カバレッジ目標 | 品質ゲート | デプロイ条件 |
|---------|--------------|-----------|-------------|
| 0.1.0-0.2.0 | 70% | Warning可 | 手動のみ |
| 0.3.0-0.4.0 | 80% | エラー不可 | 手動のみ |
| 0.5.0 | 85% | すべて通過 | 自動可能 |
| 1.0.0 | 90% | すべて通過 | 完全自動 |

**品質チェックポイント**
```bash
# 各フェーズでの品質確認コマンド例

# 0.1.0: Java品質チェック
mvn clean test jacoco:report
mvn sonar:sonar -Dsonar.projectKey=courts

# 0.2.0: JavaScript品質チェック
npm test -- --coverage
npm run lint
sonar-scanner -Dsonar.projectKey=courts-frontend

# 0.3.0以降: 統合品質チェック
mvn clean verify sonar:sonar
npm run test:e2e
```

## 4. バージョンタグ運用手順

### 4.1 タグ作成手順

**基本的なタグ作成**
```bash
# 開発完了時のタグ作成
git tag -a v0.1.0 -m "Java CI化完成"
git push origin v0.1.0

# リビジョンタグ（内部管理用）
git tag -a v0.1.1 -m "バグ修正・設定調整"
git push origin v0.1.1
```

**タグとブランチ戦略**
```bash
# フィーチャーブランチでの開発
git checkout -b feature/java-ci-implementation

# 開発完了後、メインブランチにマージ
git checkout main
git merge feature/java-ci-implementation

# マイルストーン達成時にタグ作成
git tag -a v0.1.0 -m "Java CI化完成 - Maven自動化、JUnit、JaCoCo、SonarQube統合"
git push origin v0.1.0
```

### 4.2 リリースノート管理

**各バージョンのリリースノートテンプレート**
```markdown
# Release v0.1.0 - Java CI化完成

## 📋 主な変更内容
- Maven マルチモジュール構成の確立
- JUnit 自動テスト実行基盤の構築
- JaCoCo カバレッジレポート生成
- SonarQube 品質チェック統合

## 🔧 技術的な改善
- CI/CD パイプライン定期実行対応
- 品質ゲート設定（カバレッジ70%以上）
- 静的コード解析の自動化

## 📊 品質指標
- テストカバレッジ: 75.3%
- SonarQube品質ゲート: 通過
- ビルド成功率: 98.2%

## 🔄 次バージョン予定
- v0.2.0: JavaScript CI化対応
- フロントエンド品質保証体制構築
```

### 4.3 バージョン間の互換性管理

**後方互換性の考慮**
```
0.x.x → 1.0.0: 互換性保持不要（大幅変更可能）
1.x.x 内: API互換性保持が望ましい
メジャーアップデート: 破壊的変更可能
```

**データマイグレーション**
```sql
-- バージョンアップ時のDBマイグレーション例
-- V0.3.0__add_user_roles.sql
ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'USER';

-- V0.4.0__add_audit_fields.sql
ALTER TABLE organizations ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE organizations ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

## 5. 運用監視とフィードバック

### 5.1 バージョン別監視指標

**開発フェーズ監視（0.1.0-0.4.0）**
- CI/CD実行成功率
- コードカバレッジトレンド
- SonarQube品質指標
- 開発速度（コミット頻度）

**統合フェーズ監視（0.5.0-1.0.0）**
- デプロイメント成功率
- アプリケーション稼働率
- パフォーマンス指標
- セキュリティスキャン結果

### 5.2 継続的改善サイクル

**バージョンアップ判断基準**
1. **機能要件の達成**: 計画された機能の完成
2. **品質基準のクリア**: カバレッジ・品質ゲート通過
3. **安定性の確保**: CI/CD実行の安定化
4. **ドキュメントの整備**: 必要な文書の完成

**フィードバックループ**
```
週次: 開発進捗とCI結果のレビュー
月次: 品質トレンドと技術的負債の評価
マイルストーン: バージョンアップの可否判断
```

このバージョン管理戦略により、MUTプロジェクトの段階的発展と品質保証の両立を実現します。各フェーズでの明確な目標設定により、開発チームの方向性を統一し、効率的なプロジェクト推進が可能になります。