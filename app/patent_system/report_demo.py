#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDFレポート生成機能のデモスクリプト

このスクリプトは、新しく追加されたPDFレポート生成機能をデモンストレーションします。
主な機能：
1. 特許分類別の出願数を表した年別の棒グラフの生成
2. 特許査定、拒絶査定、その他査定の比率を表した円グラフの生成
3. 上記チャートを含めたPDF形式の特許分析レポートの生成
4. 複数の出願人を比較するレポートの生成
"""

import os
import sys
import logging
import base64
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("patent-report-demo")

# モジュール探索のため、親ディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Print debug info
logger.info(f"Python path: {sys.path}")
logger.info(f"Current working directory: {os.getcwd()}")

# パス調整後にインポート
try:
    from app.patent_system.report_generator import PatentReportGenerator
    logger.info("Successfully imported PatentReportGenerator")
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    try:
        # 直接モジュール自体をインポート
        import app.patent_system.mock_analyzer as mock_analyzer
        from app.patent_system.report_generator import PatentReportGenerator
        logger.info("Successfully imported PatentReportGenerator after module adjustment")
    except ImportError as e:
        logger.error(f"Import error after path adjustment: {str(e)}")
        logger.error("Failed to import PatentReportGenerator. Using simple mock implementation for demo purposes.")
        
        # デモ用の簡易実装
        class PatentReportGenerator:
            """デモ用の簡易実装"""
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
            
            def generate_classification_trend_chart(self, years=10, top_n=5):
                print(f"[MOCK] 分類別トレンドグラフ生成（{years}年分、上位{top_n}分類）")
                return "モックデータ（実際の実装ではBase64画像）"
            
            def generate_assessment_ratio_chart(self, applicant_name=None):
                name = applicant_name if applicant_name else "全体"
                print(f"[MOCK] 査定比率グラフ生成（{name}）")
                return "モックデータ（実際の実装ではBase64画像）"
            
            def generate_pdf_report(self, output_path, applicant_name=None, years=10, top_n=5):
                name = applicant_name if applicant_name else "全体"
                print(f"[MOCK] PDFレポート生成（{name}、{output_path}）")
                return True
            
            def generate_applicant_comparison_report(self, applicants, output_path):
                print(f"[MOCK] 出願人比較レポート生成（{', '.join(applicants)}、{output_path}）")
                return True

def print_separator(title=None):
    """Print a separator with an optional title."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()

def save_base64_to_file(base64_data, output_path):
    """
    Base64エンコードされたデータをファイルに保存する
    
    Args:
        base64_data (str): Base64エンコードされた文字列
        output_path (str): 出力先ファイルパス
    
    Returns:
        bool: 成功したかどうか
    """
    try:
        # Base64をデコード
        binary_data = base64.b64decode(base64_data)
        
        # ファイルに書き込み
        with open(output_path, 'wb') as f:
            f.write(binary_data)
        
        return True
    except Exception as e:
        print(f"ファイル保存エラー: {str(e)}")
        return False

def run_classification_trend_chart_demo():
    """特許分類別の年次出願数トレンドグラフ生成デモ"""
    print_separator("特許分類別の年次出願数トレンドグラフ生成")
    
    with PatentReportGenerator() as generator:
        print("グラフを生成しています...")
        
        # 5年分、上位3分類でグラフを生成
        chart_data = generator.generate_classification_trend_chart(years=5, top_n=3)
        
        # 画像をファイルに保存
        output_path = "classification_trend_chart.png"
        success = save_base64_to_file(chart_data, output_path)
        
        if success:
            print(f"チャートを {output_path} に保存しました")
        else:
            print("チャート保存に失敗しました")

def run_assessment_ratio_chart_demo():
    """査定比率円グラフ生成デモ"""
    print_separator("特許査定比率円グラフ生成")
    
    with PatentReportGenerator() as generator:
        # 全体の査定比率グラフ
        print("全体の査定比率グラフを生成しています...")
        chart_data = generator.generate_assessment_ratio_chart()
        output_path = "overall_assessment_chart.png"
        success = save_base64_to_file(chart_data, output_path)
        
        if success:
            print(f"全体の査定比率チャートを {output_path} に保存しました")
        else:
            print("チャート保存に失敗しました")
        
        # 特定の出願人の査定比率グラフ
        applicant_name = "テック株式会社"
        print(f"{applicant_name}の査定比率グラフを生成しています...")
        chart_data = generator.generate_assessment_ratio_chart(applicant_name)
        output_path = f"{applicant_name}_assessment_chart.png"
        success = save_base64_to_file(chart_data, output_path)
        
        if success:
            print(f"{applicant_name}の査定比率チャートを {output_path} に保存しました")
        else:
            print("チャート保存に失敗しました")

def run_pdf_report_demo():
    """PDFレポート生成デモ"""
    print_separator("PDF特許分析レポート生成")
    
    with PatentReportGenerator() as generator:
        # 全体の特許分析レポート
        print("全体の特許分析レポートを生成しています...")
        output_path = "overall_patent_report.pdf"
        success = generator.generate_pdf_report(output_path)
        
        if success:
            print(f"レポートを {output_path} に保存しました")
        else:
            print("レポート生成に失敗しました")
        
        # 特定の出願人の特許分析レポート
        applicant_name = "テック株式会社"
        print(f"{applicant_name}の特許分析レポートを生成しています...")
        output_path = f"{applicant_name}_patent_report.pdf"
        success = generator.generate_pdf_report(output_path, applicant_name=applicant_name)
        
        if success:
            print(f"レポートを {output_path} に保存しました")
        else:
            print("レポート生成に失敗しました")

def run_comparison_report_demo():
    """出願人比較レポート生成デモ"""
    print_separator("出願人比較レポート生成")
    
    with PatentReportGenerator() as generator:
        # 複数の出願人の比較レポート
        applicants = ["テック株式会社", "イノベーション製造", "未来技研"]
        print(f"{', '.join(applicants)} の比較レポートを生成しています...")
        output_path = "applicant_comparison_report.pdf"
        success = generator.generate_applicant_comparison_report(applicants, output_path)
        
        if success:
            print(f"比較レポートを {output_path} に保存しました")
        else:
            print("レポート生成に失敗しました")

def demo_mcp_integration():
    """MCP統合のデモ（情報表示のみ）"""
    print_separator("MCPサーバーとの統合デモ（情報表示のみ）")
    
    print("""
MCP サーバーは以下の新しいPDFレポート生成ツールを提供します:

1. generate_pdf_report: 特許分類別の出願数推移と査定比率を含むPDFレポートを生成
   - 引数:
     - applicant_name: 出願人名（オプション。指定しない場合は全体の分析）
     - years: トレンド分析する年数 (デフォルト: 10)
     - top_n: 表示する分類数 (デフォルト: 5)

2. generate_comparison_report: 複数の出願人の査定比率を比較するPDFレポートを生成
   - 引数:
     - applicants: 比較する出願人名のリスト（1～5社）

ClaudeなどのAIアシスタントからこれらのツールを利用するには:

<use_mcp_tool>
<server_name>patent-applicant-analyzer</server_name>
<tool_name>generate_pdf_report</tool_name>
<arguments>
{
  "applicant_name": "テック株式会社",
  "years": 10,
  "top_n": 5
}
</arguments>
</use_mcp_tool>

または複数出願人の比較:

<use_mcp_tool>
<server_name>patent-applicant-analyzer</server_name>
<tool_name>generate_comparison_report</tool_name>
<arguments>
{
  "applicants": ["テック株式会社", "イノベーション製造", "未来技研"]
}
</arguments>
</use_mcp_tool>

出力はBase64エンコードされたPDFデータでブラウザで開くことやファイルとして保存することができます。
企業の情報要求に対して素早く視覚的な分析資料を提供するのに役立ちます。
""")

def main():
    """Main demo function."""
    print("\n特許分析PDFレポート生成機能デモ\n")
    print("このデモでは、新しく追加された特許分析PDFレポート生成機能を紹介します。")
    
    try:
        # Run all demos
        run_classification_trend_chart_demo()
        run_assessment_ratio_chart_demo()
        run_pdf_report_demo()
        run_comparison_report_demo()
        demo_mcp_integration()
        
        print_separator("デモ完了")
        print("各グラフとPDFファイルは現在のディレクトリに保存されました:")
        print("- classification_trend_chart.png: 特許分類別のトレンドグラフ")
        print("- overall_assessment_chart.png: 全体の査定比率グラフ")
        print("- テック株式会社_assessment_chart.png: 特定企業の査定比率グラフ")
        print("- overall_patent_report.pdf: 全体の特許分析レポート")
        print("- テック株式会社_patent_report.pdf: 特定企業の特許分析レポート")
        print("- applicant_comparison_report.pdf: 複数出願人の比較レポート")
        
    except Exception as e:
        logger.error(f"デモの実行中にエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
