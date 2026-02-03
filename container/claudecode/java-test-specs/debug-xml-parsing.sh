#!/bin/bash

echo "=== Real JaCoCo XML Structure Analysis ==="
echo

# XMLの基本構造を確認
echo "1. パッケージ構造:"
grep -o '<package name="[^"]*"' debug-real-jacoco.xml | sed 's/<package name="/  - /' | sed 's/"//'

echo
echo "2. クラス構造:"
grep -o '<class name="[^"]*"' debug-real-jacoco.xml | sed 's/<class name="/  - /' | sed 's/"//'

echo
echo "3. メソッド構造:"
grep -o '<method name="[^"]*"' debug-real-jacoco.xml | sed 's/<method name="/  - /' | sed 's/"//'

echo
echo "4. クラス名抽出テスト:"
echo "jp/go/courts/addressbook/batch/service/HelloService → HelloService"
echo "jp/go/courts/addressbook/batch/controller/HelloController → HelloController"
echo "jp/go/courts/addressbook/batch/AddressbookApplication → AddressbookApplication"

echo
echo "5. 期待される14個のCoverageInfo:"
echo "HelloService: 6メソッド (<init>, hello, selectTest, insertTest, updateTest, lambda\$updateTest\$0)"
echo "HelloController: 6メソッド (<init>, hello, select, insert, insertjson, updatejson)"
echo "AddressbookApplication: 2メソッド (<init>, main)"
echo "合計: 6 + 6 + 2 = 14メソッド"

echo
echo "=== Analysis Complete ==="