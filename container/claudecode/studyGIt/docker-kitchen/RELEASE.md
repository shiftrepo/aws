# Docker Kitchen リリース情報

## アクセス方法

Docker Kitchenは現在ローカル環境で実行可能な状態です。以下の手順に従ってアクセスしてください。

## 実行方法

### 通常の実行方法（Node.js）

1. リポジトリのルートディレクトリに移動します：
   ```bash
   cd /root/aws.git/container/claudecode/studyGIt/docker-kitchen
   ```

2. 依存関係をインストールします：
   ```bash
   npm install
   ```

3. アプリケーションを起動します：
   ```bash
   npm start
   ```

4. 以下のURLにアクセスします：
   ```
   http://localhost:3000
   ```

### Docker Composeでの実行方法（推奨）

1. リポジトリのルートディレクトリに移動します：
   ```bash
   cd /root/aws.git/container/claudecode/studyGIt/docker-kitchen
   ```

2. Docker Composeでビルドと実行を行います：
   ```bash
   docker-compose up --build
   ```
   
   バックグラウンドで実行する場合：
   ```bash
   docker-compose up -d
   ```

3. 以下のURLにアクセスします：
   ```
   http://localhost:3000
   ```

4. アプリケーションを停止するには：
   ```bash
   docker-compose down
   ```

詳細な使い方については `DOCKER_COMPOSE_GUIDE.md` を参照してください。

## 現在実装済みの機能

### 1. アプリケーション全体
- タブベースのナビゲーションシステム（ダッシュボード、Dockerfileビルダー、コンテナ管理）
- 共通のデザインテーマとインターフェース

### 2. リソース可視化ダッシュボード
- CPU、メモリ、ディスク使用量のプログレスバー表示
- アクティブなコンテナのリスト表示
- コンテナとVMの比較表
- コンテナ統計情報の表示

### 3. Dockerfileビルダー
- ベースイメージの選択機能
- Dockerコマンドのセレクトボックスによる追加
- コマンド値の選択と変更機能
- Dockerfileのリアルタイムプレビュー
- 基本操作（クリア、コピー、生成）
- Dockerfileコマンドの基本ガイド表示

### 4. コンテナ管理シミュレーター
- コンテナリストの表示と選択機能
- コンテナの詳細情報表示
- コンテナ操作（起動・停止・再起動）ボタン
- コンテナログの表示

## 既知の制限事項

1. バックエンド連携は未実装のため、データはフロントエンドのモックデータを使用
2. 一部の機能（コンテナの新規作成、削除など）は視覚的に表示されていますが実際の動作は制限されています
3. コンテナの状態変更は一時的なもので、ページのリロード時にリセットされます

## スクリーンショット

スクリーンショットは `screenshots` ディレクトリに保存されています。主要画面は以下の通りです：

1. `dashboard.png` - リソース可視化ダッシュボード
2. `dockerfile-builder.png` - Dockerfileビルダー
3. `container-manager.png` - コンテナ管理シミュレーター