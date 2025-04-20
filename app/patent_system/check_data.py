#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.patent_system.models import SessionLocal, Patent

def check_patent_data():
    """Check if patent data was successfully loaded in the database"""
    db = SessionLocal()
    try:
        # Count total patents
        patent_count = db.query(Patent).count()
        print(f"データベース内の特許数: {patent_count}")
        
        # Get all patents
        patents = db.query(Patent).all()
        
        # Display information about each patent
        print("\n--- 特許データの詳細 ---")
        for patent in patents:
            print(f"\n特許 ID: {patent.id}")
            print(f"出願番号: {patent.application_number}")
            print(f"タイトル: {patent.title}")
            print(f"出願日: {patent.application_date}")
            print(f"出願者: {', '.join([a.name for a in patent.applicants])}")
            print(f"発明者: {', '.join([i.name for i in patent.inventors])}")
            
            if patent.abstract:
                print(f"要約: {patent.abstract[:100]}...")
                
            print(f"IPCコード: {', '.join([ipc.code for ipc in patent.ipc_classifications])}")
            print(f"クレーム数: {len(patent.claims)}")
            print("=" * 50)
    finally:
        db.close()

if __name__ == "__main__":
    check_patent_data()
