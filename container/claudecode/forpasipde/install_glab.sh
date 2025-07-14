#!/bin/bash
# GitLab CLI (glab) インストールスクリプト

echo "GitLab CLI (glab) のインストールを開始します..."

# OSの種類を検出
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "OSの検出に失敗しました。対応OSは Amazon Linux, Ubuntu, Debian, Alpineです。"
    exit 1
fi

case $OS in
    "amzn")
        # Amazon Linux用のインストール
        echo "Amazon Linux向けにglabをインストールします..."
        curl -s https://raw.githubusercontent.com/profclems/glab/trunk/scripts/install.sh | sudo bash
        ;;
    "ubuntu"|"debian")
        # Ubuntu/Debian用のインストール
        echo "Debian/Ubuntu向けにglabをインストールします..."
        curl -s https://raw.githubusercontent.com/profclems/glab/trunk/scripts/install.sh | sudo bash
        ;;
    "alpine")
        # Alpine用のインストール
        echo "Alpine Linux向けにglabをインストールします..."
        GLAB_VERSION=$(curl -s https://api.github.com/repos/profclems/glab/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
        GLAB_VERSION=${GLAB_VERSION#v}
        wget -O glab.tar.gz https://github.com/profclems/glab/releases/download/v${GLAB_VERSION}/glab_${GLAB_VERSION}_Linux_x86_64.tar.gz
        tar -xzf glab.tar.gz
        sudo mv bin/glab /usr/local/bin/
        rm -rf bin glab.tar.gz
        ;;
    *)
        echo "対応していないOSです: $OS"
        exit 1
        ;;
esac

# インストールの確認
if command -v glab &> /dev/null; then
    echo "GitLab CLI (glab) インストール成功！"
    glab --version
else
    echo "GitLab CLI (glab) のインストールに失敗しました。"
    exit 1
fi

# グローバル設定
echo "GitLab CLI (glab) の基本設定を行います..."
glab config set -g editor "vim"
glab config set -g browser "chrome"

echo "GitLab CLI (glab) セットアップ完了！"