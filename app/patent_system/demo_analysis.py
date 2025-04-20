#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
特許分析機能のデモスクリプト

このスクリプトは、新しく追加された特許分析機能をデモンストレーションします。
主な機能：
1. 技術トレンド分析
2. 出願者（企業）間の競争分析
3. 特許ランドスケープ分析
4. 包括的な特許分析レポートの生成
"""

import os
import json
import logging
import sys
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("patent-analyzer-demo")

# Import the patent analyzer
try:
    # Print debug info
    import sys
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Try absolute import
    from app.patent_system.patent_analyzer import PatentAnalyzer
    logger.info("Successfully imported PatentAnalyzer using absolute import")
except ImportError as e:
    logger.error(f"Absolute import error: {str(e)}")
    
    # Try relative import
    try:
        from .patent_analyzer import PatentAnalyzer
        logger.info("Successfully imported PatentAnalyzer using relative import")
    except ImportError as e:
        logger.error(f"Relative import error: {str(e)}")
        
        # Try local import
        try:
            from patent_analyzer import PatentAnalyzer
            logger.info("Successfully imported PatentAnalyzer using local import")
        except ImportError as e:
            logger.error(f"Local import error: {str(e)}")
            logger.error("Failed to import PatentAnalyzer. Make sure you're running the script from the project root.")
            sys.exit(1)

def print_separator(title=None):
    """Print a separator with an optional title."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()

def export_result_to_markdown(data, filename):
    """Export a result dictionary to a markdown file."""
    
    # Generate file content
    content = []
    
    if filename.endswith("_trends.md"):
        content.append("# 特許技術トレンド分析\n")
        
        # Top technologies section
        content.append("## 主要技術分野\n")
        
        for tech in data["top_technologies"]:
            desc = data["technology_descriptions"].get(tech, "")
            content.append(f"- **{tech}**: {desc}")
        
        # Yearly trends section
        content.append("\n## 年次トレンド\n")
        
        content.append("| 年 |" + " ".join([f" {tech} |" for tech in data["top_technologies"][:5]]))
        content.append("|" + "---|" * (len(data["top_technologies"][:5]) + 1))
        
        for year_data in sorted(data["yearly_trends"], key=lambda x: x["year"]):
            row = [f"| {year_data['year']}"]
            for tech in data["top_technologies"][:5]:
                row.append(f" {year_data.get(tech, 0)} |")
            content.append("".join(row))
    
    elif filename.endswith("_competition.md"):
        content.append("# 特許出願者競争分析\n")
        
        # Top applicants section
        content.append("## 主要出願者\n")
        
        for applicant in data["top_applicants"]:
            content.append(f"### {applicant['name']}\n")
            content.append(f"- **総特許数**: {applicant['total_patents']}")
            
            # Technology focus
            content.append("- **主要技術分野**:")
            for tech in applicant["technology_focus"][:3]:
                content.append(f"  - {tech['ipc_code']}: {tech['count']} 件")
            
            content.append("")  # Empty line
        
        # Overlap matrix
        content.append("## 技術オーバーラップ行列\n")
        content.append("以下の行列は、各出願者間の技術的な重複度（%）を示しています。")
        content.append("値が大きいほど、二社間の技術分野の重複が大きいことを意味します。\n")
        
        content.append("| 出願者 |" + "".join([f" {name[:10]}... |" for name in data["applicant_names"]]))
        content.append("|" + "---|" * (len(data["applicant_names"]) + 1))
        
        for i, name in enumerate(data["applicant_names"]):
            row = [f"| {name[:10]}..."]
            for j in range(len(data["applicant_names"])):
                overlap = data["technology_overlap"][i][j]
                row.append(f" {overlap}% |")
            content.append("".join(row))
    
    elif filename.endswith("_landscape.md"):
        content.append("# 特許ランドスケープ分析\n")
        
        # Top categories section
        content.append("## 主要特許分類カテゴリー\n")
        
        for item in data["landscape"][:15]:
            category = item["category"]
            count = item["count"]
            desc = data["ipc_descriptions"].get(category, "説明なし")
            
            content.append(f"- **{category}** ({count}件): {desc}")
        
        # Clusters section
        if data["clusters"]:
            content.append("\n## 特許分類クラスター\n")
            
            for cluster in data["clusters"]:
                content.append(f"### {cluster['name']} - {cluster['description']}\n")
                content.append(f"総特許数: {cluster['total_patents']}件\n")
                
                content.append("主要カテゴリー:")
                for item in sorted(cluster["items"], key=lambda x: x["count"], reverse=True)[:5]:
                    content.append(f"- {item['category']}: {item['count']}件")
                
                content.append("")  # Empty line
    
    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    
    logger.info(f"Exported results to {filename}")

def run_technology_trends_analysis():
    """Run technology trends analysis."""
    print_separator("技術トレンド分析")
    
    with PatentAnalyzer() as analyzer:
        # Analyze technology trends
        print("特許技術トレンドを分析しています...")
        trends_data = analyzer.analyze_technology_trends(years=10, top_n=10)
        
        if "error" in trends_data:
            print(f"エラー: {trends_data['error']}")
            return
        
        # Display results
        print("主要技術分野:")
        for tech in trends_data["top_technologies"]:
            desc = trends_data["technology_descriptions"].get(tech, "")
            print(f"- {tech}: {desc}")
        
        # Export to markdown
        export_result_to_markdown(trends_data, "technology_trends.md")
        
        return trends_data

def run_applicant_competition_analysis():
    """Run applicant competition analysis."""
    print_separator("出願者競争分析")
    
    with PatentAnalyzer() as analyzer:
        # Analyze applicant competition
        print("特許出願者間の競争状況を分析しています...")
        competition_data = analyzer.analyze_applicant_competition(top_n=5)
        
        if "error" in competition_data:
            print(f"エラー: {competition_data['error']}")
            return
        
        # Display results
        print("主要出願者:")
        for applicant in competition_data["top_applicants"]:
            print(f"- {applicant['name']}: {applicant['total_patents']}件")
        
        # Export to markdown
        export_result_to_markdown(competition_data, "applicant_competition.md")
        
        return competition_data

def run_patent_landscape_analysis():
    """Run patent landscape analysis."""
    print_separator("特許ランドスケープ分析")
    
    with PatentAnalyzer() as analyzer:
        # Analyze patent landscape
        print("特許ランドスケープを分析しています...")
        landscape_data = analyzer.analyze_patent_landscape(ipc_level=3)
        
        if "error" in landscape_data:
            print(f"エラー: {landscape_data['error']}")
            return
        
        # Display results
        print("主要特許分類カテゴリー（上位10件）:")
        for item in landscape_data["landscape"][:10]:
            category = item["category"]
            count = item["count"]
            desc = landscape_data["ipc_descriptions"].get(category, "説明なし")
            
            print(f"- {category} ({count}件): {desc}")
        
        # Export to markdown
        export_result_to_markdown(landscape_data, "patent_landscape.md")
        
        return landscape_data

def run_analysis_report():
    """Generate a comprehensive analysis report."""
    print_separator("包括的特許分析レポート")
    
    with PatentAnalyzer() as analyzer:
        # Generate analysis report
        print("包括的な特許分析レポートを生成しています...")
        report = analyzer.generate_analysis_report()
        
        # Save the report to a file
        with open("patent_analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"レポートを patent_analysis_report.md に保存しました。")

def demo_mcp_integration():
    """Demonstrate how the MCP integration works."""
    print_separator("MCPサーバーとの統合デモ（情報表示のみ）")
    
    print("""
MCP サーバーは以下の新しい分析ツールを提供します:

1. analyze_technology_trends: 技術トレンドの分析
   - 引数:
     - years: 分析する年数 (デフォルト: 10)
     - top_n: 表示する上位技術の数 (デフォルト: 10)

2. analyze_applicant_competition: 出願者（企業）間の競争分析
   - 引数:
     - top_n: 分析する上位出願者の数 (デフォルト: 10)

3. analyze_patent_landscape: 特許ランドスケープ分析
   - 引数:
     - ipc_level: IPCの階層レベル (1=セクション, 2=クラス, 3=サブクラス, デフォルト: 3)

4. generate_analysis_report: 包括的な特許分析レポートの生成
   - 引数: なし

ClaudeなどのAIアシスタントからこれらのツールを利用するには:

<use_mcp_tool>
<server_name>bedrock-patent-query</server_name>
<tool_name>analyze_technology_trends</tool_name>
<arguments>
{
  "years": 10,
  "top_n": 5
}
</arguments>
</use_mcp_tool>
""")

def main():
    """Main demo function."""
    print("\n特許分析機能デモ\n")
    print("このデモでは、新しく追加された特許分析機能を紹介します。")
    
    try:
        # Run all demos
        trends_data = run_technology_trends_analysis()
        competition_data = run_applicant_competition_analysis()
        landscape_data = run_patent_landscape_analysis()
        run_analysis_report()
        demo_mcp_integration()
        
        print_separator("デモ完了")
        print("各分析結果はMarkdownファイルに保存されています:")
        print("- technology_trends.md: 技術トレンド分析")
        print("- applicant_competition.md: 出願者競争分析")
        print("- patent_landscape.md: 特許ランドスケープ分析")
        print("- patent_analysis_report.md: 包括的分析レポート")
        
    except Exception as e:
        logger.error(f"デモの実行中にエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
