# Docker Kitchen クイックスタートガイド

Docker Kitchenアプリケーションの起動方法をご紹介します。

## 前提条件

- Node.js (v14以上)
- npm または yarn

## インストール手順

1. リポジトリをクローンまたはダウンロードします：
   ```bash
   git clone https://github.com/yourusername/docker-kitchen.git
   cd docker-kitchen
   ```

2. 依存関係をインストールします：
   ```bash
   npm install
   # または
   yarn install
   ```

3. 開発サーバーを起動します：
   ```bash
   npm start
   # または
   yarn start
   ```

4. ブラウザで以下のURLにアクセスします：
   ```
   http://localhost:3000
   ```

## 機能ガイド

### 1. リソース可視化ダッシュボード

最初に表示されるメイン画面では、コンテナのリソース使用状況とアクティブなコンテナのリストを確認できます。また、コンテナと仮想マシンの比較表も表示されています。

### 2. Dockerfileビルダー

上部のナビゲーションから「Dockerfileビルダー」タブをクリックすると、インタラクティブなDockerfile作成ツールが表示されます。

- ベースイメージを選択
- コマンドをセレクトボックスから追加
- 作成されたDockerfileをリアルタイムでプレビュー

### 3. コンテナ管理シミュレーター

上部のナビゲーションから「コンテナ管理」タブをクリックすると、コンテナ管理シミュレーターが表示されます。

- コンテナの起動・停止・再起動などの操作
- コンテナ詳細情報の表示
- コンテナログの確認

## 開発者向け情報

ソースコードは以下のような構成になっています：

```
docker-kitchen/
├── src/
│   ├── components/       # UIコンポーネント
│   │   ├── Dashboard.js  # リソース可視化ダッシュボード
│   │   ├── DockerfileBuilder.js  # Dockerfileビルダー
│   │   └── ContainerManager.js   # コンテナ管理シミュレーター
│   ├── App.js           # メインアプリケーション
│   └── index.js         # エントリーポイント
└── public/              # 静的ファイル
```

## サポートとフィードバック

質問やフィードバックがある場合は、GitHubのイシュートラッカーで問題を報告してください。