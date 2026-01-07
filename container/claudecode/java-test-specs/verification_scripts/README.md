# 検証スクリプト

このディレクトリには、Java Test Specification Generatorの動作検証に使用したPythonスクリプトが含まれています。

## スクリプト一覧

### Coverageシート検証
- `check_coverage_sheet.py` - Coverageシートの基本チェック
- `check_fixed_coverage.py` - 修正後のCoverageシート確認
- `display_coverage_sheet.py` - Coverageシートの内容表示
- `display_final_coverage.py` - 最終版Coverageシートの詳細表示
- `final_check_coverage.py` - 最終確認用スクリプト
- `read_coverage_sheet.py` - Coverageシート読み込みツール

### アノテーション検証
- `verify_annotations.py` - テストケースアノテーション抽出の検証

## 使用方法

```bash
# 例: Coverageシートの内容を表示
python verification_scripts/display_final_coverage.py

# 例: アノテーション抽出を検証
python verification_scripts/verify_annotations.py
```

## 必要なパッケージ

```bash
pip install openpyxl
```

## 備考

これらのスクリプトは開発・検証目的で作成されたもので、本番環境での使用は想定していません。
検証完了後は削除可能です。

---
作成日: 2026-01-07