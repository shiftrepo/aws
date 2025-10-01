#!/bin/bash

# Python バージョンアップグレードスクリプト
# 現在のPython 3.9.19 から Python 3.11.11 へのアップグレード

echo "=== Python バージョンアップグレード開始 ==="

# 現在のバージョンを確認
echo "現在のPythonバージョン:"
python3 --version

# Python 3.11をインストール
echo -e "\nPython 3.11をインストール中..."
echo "y" | sudo dnf install python3.11

# インストール後のバージョン確認
echo -e "\nインストール後のバージョン確認:"
echo "python3: $(python3 --version)"
echo "python3.11: $(python3.11 --version)"

# alternativesでデフォルトを設定
echo -e "\nデフォルトのpython3を3.11に変更中..."
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 2

# 最終確認
echo -e "\n=== アップグレード完了 ==="
echo "新しいデフォルトのPythonバージョン:"
python3 --version

echo -e "\n利用可能なPythonバージョン:"
echo "python3 (デフォルト): $(python3 --version)"
echo "python3.9: $(python3.9 --version)"
echo "python3.11: $(python3.11 --version)"

python -m venv venv
source venv/bin/activate
pip install pandas fastapi mcp uv
npm install -g excel-mcp-server
claude mcp add-json excel-server '{"name":"excel-server","command":"uvx","args":["excel-mcp-server","stdio"]}'
