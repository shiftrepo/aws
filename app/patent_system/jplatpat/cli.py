#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import subprocess
import pkg_resources
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.patent_system.jplatpat.importer import Importer
from app.patent_system.jplatpat.analyzer import PatentAnalyzer
from app.patent_system.jplatpat.models import Patent


def import_patent_data(args):
    """
    Import patent data from J-PlatPat based on command-line arguments
    
    Args:
        args: Parsed command-line arguments
    """
    importer = Importer()
    
    # Display database stats before import
    stats_before = importer.get_database_stats()
    print(f"現在のデータベース状況:")
    print(f"  特許数: {stats_before['patent_count']}")
    print(f"  データベースパス: {stats_before['database_path']}")
    print()
    
    # Import based on specified type
    if args.company:
        print(f"企業名「{args.company}」で検索し、特許をインポートします...")
        count = importer.import_by_company(args.company, args.limit)
        print(f"成功: {count}件の特許をインポートしました")
    
    elif args.technology:
        print(f"技術分野「{args.technology}」で検索し、特許をインポートします...")
        count = importer.import_by_technology(args.technology, args.limit)
        print(f"成功: {count}件の特許をインポートしました")
    
    elif args.query:
        print(f"検索クエリ「{args.query}」で検索し、特許をインポートします...")
        count = importer.import_from_search(args.query, args.limit)
        print(f"成功: {count}件の特許をインポートしました")
    
    elif args.json_file:
        print(f"JSONファイル「{args.json_file}」から特許をインポートします...")
        count = importer.import_from_json_file(args.json_file)
        print(f"成功: {count}件の特許をインポートしました")
        
    elif args.application_numbers:
        numbers = args.application_numbers.split(',')
        print(f"出願番号「{args.application_numbers}」の特許をインポートします...")
        count = importer.import_by_numbers(numbers, is_application_numbers=True)
        print(f"成功: {count}件の特許をインポートしました")
    
    elif args.publication_numbers:
        numbers = args.publication_numbers.split(',')
        print(f"公開番号「{args.publication_numbers}」の特許をインポートします...")
        count = importer.import_by_numbers(numbers, is_application_numbers=False)
        print(f"成功: {count}件の特許をインポートしました")
    
    else:
        print("エラー: インポートソースが指定されていません")
        print("企業名(--company)、技術分野(--technology)、検索クエリ(--query)、JSONファイル(--json)、")
        print("出願番号(--application)または公開番号(--publication)を指定してください")
        return
    
    # Display updated stats
    stats_after = importer.get_database_stats()
    print(f"\nインポート後のデータベース状況:")
    print(f"  特許数: {stats_after['patent_count']}")
    
    print("\nインポートが完了しました。analysis コマンドを使用して分析できます。")


def analyze_patents(args):
    """
    Analyze patent data based on command-line arguments
    
    Args:
        args: Parsed command-line arguments
    """
    # Create analyzer instance
    analyzer = PatentAnalyzer()
    
    with analyzer:
        # Get the total patent count
        patent_count = analyzer.db.query(Patent).count()
        
        if patent_count == 0:
            print("エラー: データベースに特許がありません")
            print("まず import コマンドを使用して特許データをインポートしてください")
            return

        print(f"データベースには {patent_count} 件の特許があります")
        
        # Run the requested analysis
        if args.type == "trend":
            print(f"\n技術トレンド分析を実行中...")
            result = analyzer.analyze_technology_trends(years=args.years, top_n=args.top_n)
            
            if "error" in result:
                print(f"分析エラー: {result['error']}")
                return
                
            print(f"\n== 過去{args.years}年間のトップ{args.top_n}技術 ==\n")
            
            for tech in result["top_technologies"]:
                desc = result["technology_descriptions"].get(tech, "")
                print(f"  {tech}: {desc}")
            
            print("\n== 年次トレンド ==\n")
            print("年  | " + " | ".join(result["top_technologies"][:5]))
            print("----|" + "|".join("-" * 10 for _ in range(min(5, len(result["top_technologies"])))))
            
            for year_data in sorted(result["yearly_trends"], key=lambda x: x["year"]):
                line = f"{year_data['year']} |"
                for tech in result["top_technologies"][:5]:
                    line += f" {year_data.get(tech, 0):8d} |"
                print(line)
                
        elif args.type == "applicant":
            print(f"\n出願者競争分析を実行中...")
            result = analyzer.analyze_applicant_competition(top_n=args.top_n)
            
            if "error" in result:
                print(f"分析エラー: {result['error']}")
                return
                
            print(f"\n== トップ{args.top_n}出願者 ==\n")
            
            for applicant in result["top_applicants"]:
                print(f"  {applicant['name']}: {applicant['total_patents']}件の特許")
                print(f"    主要技術分野:")
                for tech in applicant["technology_focus"][:3]:
                    print(f"      - {tech['ipc_code']}: {tech['count']}件")
                print()
                
        elif args.type == "landscape":
            print(f"\n特許ランドスケープ分析を実行中...")
            result = analyzer.analyze_patent_landscape(ipc_level=args.ipc_level)
            
            if "error" in result:
                print(f"分析エラー: {result['error']}")
                return
                
            print(f"\n== 特許ランドスケープ (IPC階層レベル {args.ipc_level}) ==\n")
            
            # Show top 10 categories
            for item in result["landscape"][:10]:
                category = item["category"]
                count = item["count"]
                desc = result["ipc_descriptions"].get(category, "")
                print(f"  {category}: {count}件 - {desc}")
                
            # Show clusters
            print("\n== 技術クラスター ==\n")
            
            for cluster in result["clusters"]:
                print(f"  {cluster['name']}: {cluster['description']}")
                print(f"    合計特許数: {cluster['total_patents']}")
                print()
                
        elif args.type == "report":
            print(f"\n特許分析レポートを生成中...")
            report = analyzer.generate_analysis_report()
            
            # Save to file
            report_file = args.output if args.output else f"patent_analysis_report_{datetime.now().strftime('%Y%m%d')}.md"
            
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
                
            print(f"\n特許分析レポートをファイルに保存しました: {report_file}")
            print(f"ファイルの最初の数行:")
            
            # Print first few lines
            lines = report.split("\n")[:10]
            for line in lines:
                print(line)


def check_requirements():
    """
    Check if required packages are installed and install them if needed
    """
    # Get the directory of the current script
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    requirements_file = current_dir / "requirements.txt"
    
    if not requirements_file.exists():
        logger.warning("requirements.txtファイルが見つかりません")
        return False
        
    # Read requirements
    with open(requirements_file, "r") as f:
        requirements = [line.strip() for line in f if line.strip()]
    
    # Check installed packages
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = []
    
    for package in requirements:
        # Remove version specifier if present
        package_name = package.split('==')[0].split('>')[0].split('<')[0].strip()
        if package_name.lower() not in installed_packages:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"必要なライブラリ {len(missing_packages)} 件がインストールされていません:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
            
        response = input("これらのライブラリをインストールしますか？ [y/N]: ")
        if response.lower() == 'y':
            try:
                print("ライブラリをインストール中...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
                print("インストールが完了しました。")
                return True
            except subprocess.CalledProcessError:
                print("ライブラリのインストールに失敗しました。")
                print("手動でインストールするには以下のコマンドを実行してください:")
                print(f"pip install -r {requirements_file}")
                return False
        else:
            print("ライブラリのインストールをスキップします。")
            print("必要なライブラリをインストールするには以下のコマンドを実行してください:")
            print(f"pip install -r {requirements_file}")
            return False
    
    return True

def main():
    """Main entry point for command-line interface"""
    # Check dependencies
    check_requirements()
    
    # Create the main parser
    parser = argparse.ArgumentParser(description='J-PlatPat 特許分析システム')
    subparsers = parser.add_subparsers(dest='command', help='使用するサブコマンド')
    
    # Create the parser for the "import" command
    import_parser = subparsers.add_parser('import', help='J-PlatPatから特許データをインポート')
    import_source = import_parser.add_mutually_exclusive_group(required=True)
    import_source.add_argument('--company', help='企業名でインポート')
    import_source.add_argument('--technology', help='技術分野でインポート')
    import_source.add_argument('--query', help='検索クエリでインポート')
    import_source.add_argument('--json', dest='json_file', help='JSONファイルからインポート')
    import_source.add_argument('--application', dest='application_numbers', help='カンマ区切りの出願番号からインポート（例: 2022-100000,2022-100001）')
    import_source.add_argument('--publication', dest='publication_numbers', help='カンマ区切りの公開番号からインポート（例: JP2022-100000A,JP2022-100001A）')
    import_parser.add_argument('--limit', type=int, default=100, help='インポートする特許の最大数')
    
    # Create the parser for the "analyze" command
    analyze_parser = subparsers.add_parser('analyze', help='特許データを分析')
    analyze_parser.add_argument('type', choices=['trend', 'applicant', 'landscape', 'report'], 
                              help='分析タイプ')
    analyze_parser.add_argument('--years', type=int, default=10, help='分析する年数')
    analyze_parser.add_argument('--top-n', type=int, default=10, help='表示するトップエントリの数')
    analyze_parser.add_argument('--ipc-level', type=int, choices=[1, 2, 3], default=3, 
                              help='IPCの階層レベル (1=セクション, 2=クラス, 3=サブクラス)')
    analyze_parser.add_argument('--output', help='レポート出力ファイル名')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == 'import':
        import_patent_data(args)
    elif args.command == 'analyze':
        analyze_patents(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
