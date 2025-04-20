#!/usr/bin/env python3
import os
import argparse
import logging
import json
from datetime import datetime
import time

from app.patent_system.models import init_db
from app.patent_system.db_manager import PatentDBManager
from app.patent_system.j_platpat_scraper import JPlatPatClient
from app.patent_system.data_importer import PatentDataImporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("patent-system-init")

def initialize_database():
    """Initialize database tables"""
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Database initialization complete!")

def import_sample_data():
    """Import sample patent data"""
    # Check for JPlatPat credentials
    username = os.environ.get("JPLATPAT_USERNAME")
    password = os.environ.get("JPLATPAT_PASSWORD")
    
    if not username or not password:
        logger.warning("J-PlatPat credentials not found. Importing sample data only.")
        
    # Create an importer
    importer = PatentDataImporter()
    
    # Import from sample JSON file if available
    sample_file = os.path.join(os.path.dirname(__file__), "sample_patents.json")
    
    if os.path.exists(sample_file):
        logger.info(f"Importing patents from sample file: {sample_file}")
        count = importer.import_from_json_file(sample_file)
        logger.info(f"Imported {count} patents from sample file")
    else:
        # Create sample data manually
        logger.info("Sample file not found. Creating sample patents manually...")
        sample_patents = create_sample_patent_data()
        
        with PatentDBManager() as db_manager:
            count = db_manager.store_patents_batch(sample_patents)
            logger.info(f"Added {count} sample patents manually")
    
    # Check for PDF files in doc directory to import
    doc_dir = os.path.join(os.path.dirname(__file__), "..", "graphRAG", "doc")
    if os.path.exists(doc_dir):
        for file in os.listdir(doc_dir):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(doc_dir, file)
                logger.info(f"Importing data from PDF: {pdf_path}")
                importer.import_from_pdf(pdf_path)

def create_sample_patent_data():
    """Create sample patent data for demonstration"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    return [
        {
            "applicationNumber": "2023-123456",
            "applicationDate": "2023-03-15",
            "publicationNumber": "JP2023-123456A",
            "publicationDate": current_date,
            "title": "自然言語処理を用いた特許文書の自動分析システム",
            "abstract": "本発明は、機械学習と自然言語処理技術を用いて特許文書を自動的に分析し、関連性の高い情報を抽出するシステムに関する。このシステムは、特許文書からキーワード、請求項、図面情報を抽出し、検索可能なデータベースに格納する。また、類似特許の特定や技術トレンド分析も自動で行う。",
            "applicants": [
                {"name": "AIテクノロジー株式会社", "address": "東京都千代田区1-1-1"}
            ],
            "inventors": [
                {"name": "山田太郎", "address": "東京都新宿区2-2-2"},
                {"name": "佐藤花子", "address": "東京都渋谷区3-3-3"}
            ],
            "ipcClassifications": [
                {"code": "G06N 20/00", "description": "機械学習"}
            ],
            "claims": [
                {"claim_number": 1, "text": "自然言語処理モデルと機械学習アルゴリズムを用いて特許文書から情報を抽出し、分類するシステム。"},
                {"claim_number": 2, "text": "請求項1において、前記システムはさらに抽出した情報に基づいて類似特許を検索する機能を有する。"}
            ],
            "descriptions": [
                {"section_title": "技術分野", "text": "本発明は特許文書解析技術、特に自然言語処理と機械学習を用いた特許文書の自動分析システムに関する。"},
                {"section_title": "背景技術", "text": "従来の特許分析は多くの人的リソースを必要とし、時間がかかる作業である。そこで、AIを活用した特許解析の自動化が求められている。"}
            ]
        },
        {
            "applicationNumber": "2023-789012",
            "applicationDate": "2023-05-20",
            "publicationNumber": "JP2023-789012A",
            "publicationDate": current_date,
            "title": "分散データベースを用いた特許情報管理システム",
            "abstract": "本発明は、ブロックチェーン技術を活用した分散型データベースを用いて特許情報を安全かつ効率的に管理するシステムに関する。このシステムにより、特許情報の改ざんを防止しつつ、素早い検索と更新が可能になる。",
            "applicants": [
                {"name": "データセキュリティ株式会社", "address": "大阪府大阪市北区4-4-4"}
            ],
            "inventors": [
                {"name": "鈴木一郎", "address": "大阪府吹田市5-5-5"},
                {"name": "田中実", "address": "大阪府豊中市6-6-6"}
            ],
            "ipcClassifications": [
                {"code": "G06F 16/27", "description": "分散データベース"},
                {"code": "H04L 9/06", "description": "暗号化プロトコル"}
            ],
            "claims": [
                {"claim_number": 1, "text": "ブロックチェーン技術を用いた分散型データベースにより特許情報を管理するシステム。"},
                {"claim_number": 2, "text": "請求項1において、前記システムは特許情報の改ざんを検出する機能を有する。"}
            ],
            "descriptions": [
                {"section_title": "技術分野", "text": "本発明は特許情報管理システム、特にブロックチェーン技術を活用した分散型データベースによる特許情報管理に関する。"},
                {"section_title": "背景技術", "text": "従来の集中型データベースでは、データ改ざんのリスクや単一障害点の問題がある。ブロックチェーン技術の発展により、これらの問題を解決できる可能性が出てきた。"}
            ]
        },
        {
            "applicationNumber": "2023-345678",
            "applicationDate": "2023-07-10",
            "publicationNumber": "JP2023-345678A",
            "publicationDate": current_date,
            "title": "AIを活用した特許明細書自動生成システム",
            "abstract": "本発明は、人工知能技術を用いて発明の概念から特許明細書を自動的に生成するシステムに関する。発明者の入力した発明概要から、特許出願に必要な明細書の構成要素を自動的に生成し、特許取得プロセスを効率化する。",
            "applicants": [
                {"name": "特許テクノロジー株式会社", "address": "福岡県福岡市中央区7-7-7"}
            ],
            "inventors": [
                {"name": "高橋健太", "address": "福岡県博多区8-8-8"}
            ],
            "ipcClassifications": [
                {"code": "G06N 3/00", "description": "コンピュータシステムに基づく人工知能"}
            ],
            "claims": [
                {"claim_number": 1, "text": "発明の概念に基づいて人工知能が特許明細書を自動的に生成するシステム。"},
                {"claim_number": 2, "text": "請求項1において、前記システムは過去の特許文書から学習したデータを利用する。"}
            ],
            "descriptions": [
                {"section_title": "技術分野", "text": "本発明は特許明細書作成支援技術、特にAIを用いた特許明細書の自動生成システムに関する。"},
                {"section_title": "背景技術", "text": "特許明細書の作成は、技術的知識と法的知識の両方を必要とする専門的な作業である。AI技術の発展により、この作業の自動化が可能になりつつある。"}
            ]
        }
    ]

def print_usage_instructions():
    """Print instructions for using the MCP server"""
    logger.info("\n" + "="*80)
    logger.info("PATENT SYSTEM SETUP COMPLETE!")
    logger.info("="*80)
    logger.info("\nYou can now use the natural language query capabilities through the MCP server.")
    logger.info("\nExample MCP tool usages:")
    
    # Example 1: Query patents
    example1 = {
        "server_name": "bedrock-patent-query",
        "tool_name": "query_patents",
        "arguments": {
            "query": "AIを活用した特許管理システムについて教えてください"
        }
    }
    logger.info("\nExample 1 - Query patents by topic:")
    logger.info(f"""
<use_mcp_tool>
<server_name>{example1['server_name']}</server_name>
<tool_name>{example1['tool_name']}</tool_name>
<arguments>
{json.dumps(example1['arguments'], indent=2, ensure_ascii=False)}
</arguments>
</use_mcp_tool>
    """)
    
    # Example 2: Search patents
    example2 = {
        "server_name": "bedrock-patent-query",
        "tool_name": "search_patents",
        "arguments": {
            "query": "ブロックチェーン技術を用いた特許システム",
            "limit": 5
        }
    }
    logger.info("\nExample 2 - Search patents by similarity:")
    logger.info(f"""
<use_mcp_tool>
<server_name>{example2['server_name']}</server_name>
<tool_name>{example2['tool_name']}</tool_name>
<arguments>
{json.dumps(example2['arguments'], indent=2, ensure_ascii=False)}
</arguments>
</use_mcp_tool>
    """)
    
    # Example 3: Get patent stats
    example3 = {
        "server_name": "bedrock-patent-query",
        "tool_name": "get_patent_stats",
        "arguments": {}
    }
    logger.info("\nExample 3 - Get patent statistics:")
    logger.info(f"""
<use_mcp_tool>
<server_name>{example3['server_name']}</server_name>
<tool_name>{example3['tool_name']}</tool_name>
<arguments>
{json.dumps(example3['arguments'], indent=2, ensure_ascii=False)}
</arguments>
</use_mcp_tool>
    """)
    
    logger.info("\n" + "="*80)

def main():
    """Main function to initialize database and import sample data"""
    parser = argparse.ArgumentParser(description='Initialize patent database and import sample data')
    parser.add_argument('--skip-init', action='store_true', help='Skip database initialization')
    parser.add_argument('--skip-import', action='store_true', help='Skip sample data import')
    
    args = parser.parse_args()
    
    if not args.skip_init:
        initialize_database()
    
    if not args.skip_import:
        import_sample_data()
    
    print_usage_instructions()

if __name__ == "__main__":
    main()
