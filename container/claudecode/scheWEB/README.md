# 📅 チームスケジューラー (Team Scheduler)

チームメンバーの空き時間を簡単に管理し、全員が参加可能な会議時間を見つけるためのWebアプリケーションです。

## ✨ 特徴

- 🎨 **ポップで親しみやすいUI**: 淡いパステルカラーとスムーズなアニメーション
- 🖱️ **マウスフレンドリー**: ドラッグ&ドロップによる直感的な時間入力
- 👥 **チーム管理**: 最大30名までのユーザー管理
- ⏰ **空き時間検索**: 全メンバー共通の空き時間を自動検出
- 🔒 **Basic認証**: 内部利用に適したシンプルなセキュリティ
- 🐳 **Docker対応**: ワンコマンドでの簡単デプロイ

## 🚀 クイックスタート

### 前提条件

- Docker
- docker-compose

### 起動方法

1. **リポジトリをクローン**
   ```bash
   git clone <repository-url>
   cd scheWEB
   ```

2. **コンテナをビルド・起動**
   ```bash
   docker-compose up --build
   ```

3. **ブラウザでアクセス**
   ```
   http://localhost
   ```

### デモアカウント

初期データとして以下のアカウントが利用可能です：

| ユーザー名 | パスワード | 勤務時間 |
|-----------|----------|-----------|
| admin     | admin123 | 09:00-18:00 |
| user1     | admin123 | 09:30-17:30 |
| user2     | admin123 | 08:30-17:00 |

## 📋 機能一覧

### 🔐 認証機能
- ✅ ユーザー登録（ユーザー名、パスワード、勤務時間）
- ✅ ログイン・ログアウト
- ✅ JWT トークンベース認証

### 👥 ユーザー管理
- ✅ ユーザー一覧表示
- ✅ 勤務時間設定
- ✅ プロフィール情報表示

### ⏰ スケジュール管理
- ✅ 曜日別空き時間入力
- ✅ 複数時間帯対応
- ✅ マウス操作による簡単編集
- ✅ リアルタイム更新

### 🤝 会議調整
- ✅ 全員共通の空き時間検索
- ✅ 曜日別空き時間表示
- ✅ 統計情報ダッシュボード

## 🛠️ 技術スタック

### バックエンド
- **Python 3.11**: プログラミング言語
- **Flask 3.0**: Webフレームワーク
- **SQLite 3**: データベース
- **JWT**: 認証トークン
- **bcrypt**: パスワードハッシュ化

### フロントエンド
- **HTML5**: マークアップ
- **CSS3**: スタイリング（カスタムプロパティ、アニメーション）
- **Vanilla JavaScript**: インタラクション
- **Inter Font**: タイポグラフィ

### インフラ
- **Docker**: コンテナ化
- **nginx**: リバースプロキシ
- **docker-compose**: オーケストレーション

## 📊 システム構成

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     nginx       │    │     Frontend     │    │    Backend      │
│  (Port: 80)     │────│   (HTML/CSS/JS)  │────│  (Flask API)    │
│                 │    │                  │    │  (Port: 5000)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │    SQLite DB    │
                                                │   (Volume)      │
                                                └─────────────────┘
```

## 🎨 UI/UX デザイン

### カラーパレット（淡い色基調）
- **プライマリ**: #A8D5E2 (Soft Sky Blue)
- **セカンダリ**: #C9E4CA (Mint Green)
- **アクセント**: #FFB5A7 (Coral Pink)
- **背景**: #FAFCFF (Very Light Blue-White)

### アニメーション
- **フェードイン**: 要素の表示
- **スライドイン**: サイドバーやモーダル
- **バウンス**: ボタンやアイコン
- **パルス**: 読み込み状態
- **シマー**: ローディングプレースホルダー

## 📁 プロジェクト構造

```
scheWEB/
├── docker-compose.yml          # Docker構成
├── nginx.conf                  # nginx設定
├── app/
│   ├── backend/               # バックエンドアプリ
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py            # メインアプリケーション
│   │   └── init_db.py        # データベース初期化
│   └── frontend/              # フロントエンドアプリ
│       ├── Dockerfile
│       ├── index.html        # メインHTML
│       ├── styles.css        # スタイルシート
│       └── app.js           # JavaScript アプリ
└── README.md
```

## 🔧 開発・運用

### 開発モード

```bash
# ログ確認
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f backend

# データベースリセット
docker-compose down -v
docker-compose up --build
```

### 本番環境設定

本番環境では以下の設定を変更してください：

1. **環境変数** (`docker-compose.yml`)
   ```yaml
   environment:
     - FLASK_ENV=production
     - FLASK_DEBUG=0
     - SECRET_KEY=your-production-secret-key
   ```

2. **SSL証明書** (`nginx.conf`)
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
   }
   ```

### バックアップ

SQLiteデータベースのバックアップ：

```bash
# データベースファイルをコピー
docker cp $(docker-compose ps -q backend):/app/data/scheduler.db ./backup_$(date +%Y%m%d).db
```

## 📈 パフォーマンス

### 目標値
- **API応答時間**: < 500ms (p95)
- **ページ読み込み**: < 3秒
- **同時ユーザー**: 30名対応
- **稼働率**: 99.5%

### 最適化
- SQLite WALモード有効化
- インデックス最適化
- 静的ファイルキャッシュ
- gzip圧縮

## 🐛 トラブルシューティング

### よくある問題

1. **ポート競合エラー**
   ```bash
   # 使用中のポートを確認
   lsof -i :80
   lsof -i :5000

   # docker-compose.ymlでポートを変更
   ports:
     - "8080:80"  # 80 → 8080に変更
   ```

2. **データベース初期化失敗**
   ```bash
   # ボリュームをクリア
   docker-compose down -v
   docker volume prune -f
   docker-compose up --build
   ```

3. **認証エラー**
   ```bash
   # JWT秘密鍵を確認
   docker-compose exec backend env | grep SECRET_KEY
   ```

### ログ確認

```bash
# 全サービスのログ
docker-compose logs

# エラーのみ表示
docker-compose logs | grep ERROR

# リアルタイム監視
docker-compose logs -f --tail=100
```

## 📞 サポート

### 連絡先
- 開発者: [Your Name]
- メール: [your-email@example.com]
- GitHub Issues: [repository-url]/issues

### ドキュメント
- API仕様: `/docs/api-specification.md`
- システム設計: `/docs/architecture/`
- UI/UXガイド: `/docs/frontend/`

---

## 🎉 おめでとうございます！

チームスケジューラーが正常にセットアップされました。
効率的なチーム会議の調整を始めましょう！

**楽しいスケジューリングを！** 📅✨