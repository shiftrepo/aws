#!/bin/bash

echo "🚀 チームスケジューラー - 起動スクリプト"
echo "================================================"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Dockerが見つかりません。Dockerをインストールしてください。"
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Composeを使用して起動します..."

    echo "📦 コンテナをビルドしています..."
    docker-compose build

    echo "🚀 アプリケーションを起動しています..."
    docker-compose up -d

    echo "📊 サービス状態を確認しています..."
    docker-compose ps

    echo ""
    echo "🎉 チームスケジューラーが起動しました！"
    echo "📱 ブラウザで以下のURLにアクセスしてください:"
    echo "   👉 http://localhost"
    echo ""
    echo "👤 デモアカウント:"
    echo "   - admin / admin123"
    echo "   - user1 / admin123"
    echo "   - user2 / admin123"
    echo ""
    echo "🛑 停止するには: docker-compose down"
    echo ""

else
    echo "⚠️  Docker Composeが見つかりません。"
    echo "💡 手動でコンテナを起動する場合："
    echo ""
    echo "1. バックエンドを起動:"
    echo "   cd app/backend"
    echo "   docker build -t team-scheduler-backend ."
    echo "   docker run -d -p 5000:5000 --name backend team-scheduler-backend"
    echo ""
    echo "2. フロントエンドを起動:"
    echo "   cd app/frontend"
    echo "   docker build -t team-scheduler-frontend ."
    echo "   docker run -d -p 3000:80 --name frontend team-scheduler-frontend"
    echo ""
    echo "3. ブラウザでアクセス: http://localhost:3000"
    echo ""
fi