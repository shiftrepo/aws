# Docker Kitchen リリース手順

Docker Kitchenプロジェクトのリリース手順を以下に説明します。

## 1. 前提条件

- Node.js 14.x以上がインストールされていること
- npmまたはyarnがインストールされていること
- 必要に応じてDockerがインストールされていること

## 2. インストール手順

### 2.1. リポジトリのクローン

```bash
git clone https://github.com/shiftrepo/aws.git
cd aws/container/claudecode/studyGIt/docker-kitchen
```

### 2.2. 依存パッケージのインストール

```bash
npm install
# または
yarn install
```

### 2.3. 開発サーバーの起動

```bash
npm run dev
# または
yarn dev
```

アプリケーションは通常、http://localhost:3000 で利用可能になります。

## 3. Docker Kitchenの使用方法

### 3.1. リソース可視化ダッシュボード

- CPU/メモリ使用量の可視化を確認
- コンテナとVMの比較表を参照
- アクティブなコンテナリストから選択して詳細を表示

### 3.2. Dockerfileビルダー

- ベースイメージを選択
- 必要なコマンドをセレクトボックスから選択し追加
- 生成されたDockerfileをプレビューしてコピー

### 3.3. コンテナ管理シミュレーター

- コンテナリストから対象を選択
- 起動/停止/再起動などのアクションを実行
- コンテナログと詳細情報を確認

## 4. 本番環境へのデプロイ

### 4.1. 静的ビルドの生成

```bash
npm run build
# または
yarn build
```

### 4.2. 静的ファイルのデプロイ

生成された`build`または`out`ディレクトリの内容をウェブサーバーにデプロイします。

### 4.3. Dockerを使用したデプロイ

```bash
# Dockerイメージをビルド
docker build -t docker-kitchen .

# コンテナを実行
docker run -p 8080:80 docker-kitchen
```

## 5. 注意事項

- このアプリケーションはデモ・教育目的であり、実際のDockerコンテナを操作するものではありません
- Dockerfileビルダーで生成されたファイルは、実際の環境で使用する前に検証してください
- パフォーマンスモニタリングのデータは模擬的なものであり、実際のシステム状況を反映していません

## 6. トラブルシューティング

### 6.1. アプリケーションが起動しない場合

```bash
# 依存関係のクリーンインストールを試す
rm -rf node_modules
npm install
npm run dev
```

### 6.2. 画面が正しく表示されない場合

- ブラウザのキャッシュをクリア
- 最新のChrome、Firefox、Safariなどのモダンブラウザを使用

## 7. 連絡先

問題や質問がある場合は、GitHub Issueを作成してください。

---

© 2025 Docker Kitchen Project - コンテナ技術を料理で学ぼう