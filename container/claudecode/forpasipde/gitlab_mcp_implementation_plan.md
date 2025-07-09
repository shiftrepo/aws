# GitLab MCP実装計画

## 調査結果サマリー

GitLab MCPの設定と実装に関する調査を行いました。GitHub MCPからGitLab MCPへの移行に必要な情報は以下の通りです。

### 主な調査結果

1. **利用可能なパッケージ**:
   - 公式: `@modelcontextprotocol/server-gitlab` (バージョン: 2025.4.25)
   - サードパーティ: `@zereight/mcp-gitlab`、`@therealchristhomas/gitlab-mcp-server`

2. **必要な認証情報**:
   - 環境変数 `GITLAB_PERSONAL_ACCESS_TOKEN` にGitLabのアクセストークンを設定する必要がある

3. **設定方法**:
   - Claude CodeのMCP設定は、`claude mcp add-json`コマンドでJSON設定ファイルを使って行う

4. **GitHub MCPとの主な違い**:
   - 認証用の環境変数名が異なる（`GITHUB_PERSONAL_ACCESS_TOKEN` → `GITLAB_PERSONAL_ACCESS_TOKEN`）
   - APIエンドポイントの構造とパラメータが異なる
   - PRの代わりにMerge Request(MR)を使用

## 実装計画

### フェーズ1: 環境セットアップ (推定所要時間: 1日)

1. **GitLabアカウント設定**:
   - GitLabアカウントの作成（既に存在する場合はスキップ）
   - APIアクセストークンの生成（スコープ: api, read_repository, write_repository）

2. **ローカル環境設定**:
   - 環境変数 `GITLAB_API_TOKEN` の設定
   - `@modelcontextprotocol/server-gitlab` のインストール
   - MCP設定ファイルの作成と適用

### フェーズ2: 基本機能テスト (推定所要時間: 2-3日)

1. **リポジトリ操作のテスト**:
   - リポジトリ作成
   - ファイル読み込み
   - コードの検索
   - ファイル作成・更新

2. **Issue管理のテスト**:
   - Issue作成
   - Issue更新
   - コメント追加

3. **Merge Request操作のテスト**:
   - ブランチ作成
   - MR作成
   - レビュー追加
   - マージ操作

### フェーズ3: 本番環境への移行 (推定所要時間: 1-2日)

1. **設定ファイルの更新**:
   - `setup.sh` の更新
   - 必要に応じて `setup_gitlab_mcp.sh` を統合

2. **デプロイとテスト**:
   - 本番環境でのインストールと設定
   - 基本機能の動作確認

3. **ドキュメント更新**:
   - 移行ガイドの最終化
   - トラブルシューティングセクションの充実

### フェーズ4: モニタリングと最適化 (推定所要時間: 継続的)

1. **パフォーマンスモニタリング**:
   - API呼び出しの速度と効率性の確認
   - エラー発生率の監視

2. **フィードバックと改善**:
   - ユーザーフィードバックの収集
   - 必要に応じた設定の最適化

## 必要なリソース

1. **アクセス権限**:
   - GitLabアカウント
   - GitLab APIトークン（適切なスコープ付き）
   - リポジトリへのアクセス権限

2. **ソフトウェア環境**:
   - Node.js と npm
   - Claude Code
   - Git

3. **ドキュメント**:
   - GitLab API リファレンス
   - MCP設定リファレンス

## リスク評価

1. **技術的リスク**:
   - GitLab MCPの機能がGitHub MCPと完全に同等でない可能性
   - APIの仕様変更によるトラブル

2. **セキュリティリスク**:
   - トークンの適切な管理（環境変数、シェル履歴）
   - 権限設定の適切な範囲設定

3. **運用リスク**:
   - チームメンバーの習熟度の差
   - 移行中のダウンタイム

## 次のステップ

1. GitLabアカウントの設定と権限確認
2. テスト環境での`setup_gitlab_mcp.sh`の実行と検証
3. 基本機能テストの実施とフィードバック収集

## 参考資料

- NPMパッケージ: [@modelcontextprotocol/server-gitlab](https://www.npmjs.com/package/@modelcontextprotocol/server-gitlab)
- GitLab API: [GitLab API Documentation](https://docs.gitlab.com/ee/api/)
- Model Context Protocol: [MCP公式サイト](https://modelcontextprotocol.io/)