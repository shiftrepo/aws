# Docker Kitchen

Docker Kitchenは料理メタファーを用いてDockerコンテナ技術を学ぶインタラクティブウェブアプリケーションです。

## プロジェクト概要

Docker Kitchenは、Dockerのコンテナ技術を初心者にも分かりやすく学べるインタラクティブな教育ツールです。
コンテナの利点（レシピ）、コンテナとVMの比較（フードトラックvsレストラン）、ホストとコンテナの関係（フードコート）という3つの主要な概念を料理の世界に例えて直感的に学ぶことができます。

## 技術スタック

- フロントエンド: React + TypeScript
- UIフレームワーク: Tailwind CSS
- アニメーション: Framer Motion
- 状態管理: React Context API

## 主な機能

1. **リソース可視化ダッシュボード**
   - CPU・メモリ・ディスク使用状況の視覚的表示
   - アクティブコンテナのリスト表示と監視
   - コンテナとVMの比較表によるリソース効率の説明

2. **インタラクティブDockerfileビルダー**
   - セレクトボックスによるDockerコマンドの選択と構築
   - リアルタイムDockerfileプレビュー機能
   - 主要コマンドの解説と使用例

3. **コンテナ管理シミュレーター**
   - コンテナの起動・停止・再起動などの基本操作
   - コンテナの詳細情報とログの表示
   - フードコート（ホストOS）とテナント（コンテナ）の関係可視化

## 開発環境構築

### ローカル開発

```bash
# 依存関係のインストール
npm install

# 開発サーバーの起動
npm start

# ビルド
npm run build
```

### Docker Composeによる実行

```bash
# Docker Composeでビルドして起動
docker-compose up --build

# バックグラウンドで起動
docker-compose up -d

# コンテナの停止
docker-compose down

# Podmanを使用する場合
podman-compose up --build
```

## プロジェクト構造

```
docker-kitchen/
├── src/
│   ├── components/        # UIコンポーネント
│   ├── context/           # React Context
│   ├── models/            # データモデル
│   ├── hooks/             # カスタムフック
│   ├── utils/             # ユーティリティ関数
│   ├── App.tsx            # メインアプリケーション
│   └── index.tsx          # エントリーポイント
├── public/                # 静的ファイル
├── Dockerfile             # Dockerイメージビルド設定
└── docker-compose.yml     # Docker Compose設定
```

## 使い方

1. テナント（コンテナ）の作成
   - 「出店申込」パネルから店舗タイプを選択
   - 店舗名を入力し、リソース割り当てを設定
   - 「出店開始」ボタンをクリックして作成

2. テナント（コンテナ）の管理
   - 「営業中テナント」リストからコンテナを操作
   - 開始・停止・削除などの基本的な操作が可能

3. リソース使用状況の確認
   - 「リソース使用状況」パネルでシステム全体のリソース使用量を確認

## Dockerコマンドとの対応関係

| シミュレーター操作 | 対応するDockerコマンド |
|------------------|---------------------|
| 出店申込 | `docker create` / `docker run -d` |
| 営業開始 | `docker start` |
| 一時休業 | `docker stop` |
| 撤退 | `docker rm` |
| リソース割り当て | `docker run --memory` / `docker run --cpu-shares` |