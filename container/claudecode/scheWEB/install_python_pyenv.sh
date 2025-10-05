#!/bin/bash
# pyenvを使用したPython最新版インストールスクリプト
# 作成日: 2025-10-05

set -e  # エラー時に終了

echo "🐍 pyenv使用 Python最新版インストールスクリプト開始"

# 変数設定
PYTHON_VERSION="3.13.7"
PYENV_ROOT="$HOME/.pyenv"

# 現在のPythonバージョン確認
echo "📋 現在のPythonバージョン:"
python3 --version || echo "python3 not found"
python --version || echo "python not found"

# pyenvのインストール確認
if [ ! -d "$PYENV_ROOT" ]; then
    echo "📦 pyenvをインストール中..."
    curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

    # PATH設定を追加
    echo "🛣️ pyenv PATH設定を追加中..."
    cat >> ~/.bashrc << 'EOF'

# pyenv設定
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOF

    # 現在のセッションでPATH設定を有効化
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
else
    echo "✅ pyenvは既にインストールされています"
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
fi

# pyenvアップデート
echo "🔄 pyenvをアップデート中..."
pyenv update || echo "⚠️ pyenv update failed, continuing..."

# 利用可能なPythonバージョンを確認
echo "📋 利用可能なPython ${PYTHON_VERSION}を確認中..."
if ! pyenv install --list | grep -q "${PYTHON_VERSION}"; then
    echo "❌ Python ${PYTHON_VERSION} が利用できません。利用可能なバージョンを表示:"
    pyenv install --list | grep "3\.13\." | tail -5
    # 利用可能な最新3.13系を取得
    PYTHON_VERSION=$(pyenv install --list | grep -E '^\s*3\.13\.' | tail -1 | sed 's/^\s*//')
    echo "✅ 代わりに ${PYTHON_VERSION} を使用します"
fi

# Python最新版のインストール
echo "⬇️ Python ${PYTHON_VERSION} をインストール中..."
if ! pyenv versions | grep -q "${PYTHON_VERSION}"; then
    pyenv install "${PYTHON_VERSION}"
else
    echo "✅ Python ${PYTHON_VERSION} は既にインストールされています"
fi

# グローバルバージョン設定
echo "🔗 Python ${PYTHON_VERSION} をグローバルデフォルトに設定中..."
pyenv global "${PYTHON_VERSION}"

# システムのpythonシンボリックリンクを更新
echo "🔗 システムのpythonリンクを更新中..."
sudo ln -sf "$PYENV_ROOT/shims/python3" /usr/local/bin/python3
sudo ln -sf "$PYENV_ROOT/shims/python3" /usr/local/bin/python
sudo ln -sf "$PYENV_ROOT/shims/pip3" /usr/local/bin/pip3
sudo ln -sf "$PYENV_ROOT/shims/pip3" /usr/local/bin/pip

# PATHを更新（現在のセッション用）
export PATH="$PYENV_ROOT/shims:$PATH"

# pipアップグレード
echo "📦 pipをアップグレード中..."
python -m pip install --upgrade pip

# インストール確認
echo "✅ インストール完了！バージョンを確認中..."
echo "Python version: $(python --version)"
echo "Python3 version: $(python3 --version)"
echo "Pip version: $(pip --version)"

# pyenvの状態確認
echo ""
echo "📊 pyenv状態:"
pyenv versions
echo ""
echo "🎉 Python ${PYTHON_VERSION} のインストールが完了しました！"
echo "📝 使用方法:"
echo "   新しいターミナルを開くか、以下を実行してください:"
echo "   source ~/.bashrc"
echo ""
echo "   または直接実行:"
echo "   $PYENV_ROOT/shims/python3 --version"