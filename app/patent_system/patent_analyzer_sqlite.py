#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.patent_system.models_sqlite import (
    Patent, Applicant, Inventor, IPCClassification,
    Claim, Description, SessionLocal
)
from app.patent_system.db_sqlite import SQLiteDBManager, init_sqlite_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class PatentAnalyzerSQLite:
    """Patent data analysis utilities for SQLite database"""
    
    def __init__(self, db_session=None):
        """Initialize with optional database session"""
        if db_session:
            self.db = db_session
        else:
            # Initialize database if needed
            init_sqlite_db()
            self.db = SessionLocal()  # Call the sessionmaker to create a session
    
    def __enter__(self):
        """Context manager entry"""
        # Use existing DB session if provided, otherwise create a new one
        if self.db is None:
            self.db = SessionLocal()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.db is not None:
            self.db.close()
    
    def analyze_technology_trends(self, years: int = 10, top_n: int = 10) -> Dict[str, Any]:
        """
        Analyze technology trends over time based on IPC classifications
        
        Args:
            years: Number of recent years to analyze
            top_n: Number of top technologies to include
            
        Returns:
            Dictionary with trend analysis results
        """
        try:
            # Get current year
            current_year = datetime.now().year
            start_year = current_year - years
            
            # SQL to get IPC trends over time - adapted for SQLite
            sql = text("""
                SELECT 
                    strftime('%Y', p.application_date) AS year,
                    ipc.code AS ipc_code,
                    COUNT(DISTINCT p.id) AS patent_count
                FROM patents p
                JOIN ipc_classifications ipc ON ipc.patent_id = p.id
                WHERE 
                    p.application_date IS NOT NULL AND
                    strftime('%Y', p.application_date) >= :start_year
                GROUP BY year, ipc_code
                ORDER BY year DESC, patent_count DESC
            """)
            
            # Execute query
            result = self.db.execute(sql, {"start_year": str(start_year)})
            rows = result.fetchall()
            
            # Process data
            trends_by_year = defaultdict(list)
            for row in rows:
                year = int(row[0])
                ipc_code = row[1]
                count = row[2]
                
                # Parse main IPC section and class
                # Format is typically like "G06F 16/00" - we extract "G06F"
                ipc_parts = ipc_code.split()
                ipc_section_class = ipc_parts[0] if len(ipc_parts) > 0 else ipc_code
                
                trends_by_year[year].append({
                    "ipc_code": ipc_code,
                    "ipc_section_class": ipc_section_class,
                    "count": count
                })
            
            # Get top technologies (IPC section+class) across all years
            all_ipc_counts = Counter()
            for year, technologies in trends_by_year.items():
                for tech in technologies:
                    all_ipc_counts[tech["ipc_section_class"]] += tech["count"]
            
            top_technologies = [item[0] for item in all_ipc_counts.most_common(top_n)]
            
            # Prepare yearly data for top technologies
            yearly_trends = []
            years_list = sorted(trends_by_year.keys())
            
            for year in years_list:
                year_data = {"year": year}
                
                # Get counts for each top technology
                tech_counts = defaultdict(int)
                for tech in trends_by_year[year]:
                    tech_counts[tech["ipc_section_class"]] += tech["count"]
                
                # Add counts for top technologies
                for tech in top_technologies:
                    year_data[tech] = tech_counts.get(tech, 0)
                
                yearly_trends.append(year_data)
            
            # Get IPC class descriptions
            ipc_descriptions = self._get_ipc_class_descriptions(top_technologies)
            
            return {
                "top_technologies": top_technologies,
                "technology_descriptions": ipc_descriptions,
                "yearly_trends": yearly_trends
            }
            
        except Exception as e:
            logger.error(f"Error in technology trend analysis: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def analyze_applicant_competition(self, top_n: int = 10) -> Dict[str, Any]:
        """
        Analyze applicant competition based on patent activity
        
        Args:
            top_n: Number of top applicants to analyze
            
        Returns:
            Dictionary with competitive analysis results
        """
        try:
            # Get top applicants by patent count using SQL (SQLite compatible)
            sql_top_applicants = text("""
                SELECT 
                    a.name AS applicant_name,
                    COUNT(DISTINCT a.patent_id) AS patent_count
                FROM applicants a
                GROUP BY a.name
                ORDER BY patent_count DESC
                LIMIT :limit
            """)
            
            # Execute query
            result = self.db.execute(sql_top_applicants, {"limit": top_n})
            top_applicants = [{"name": row[0], "patent_count": row[1]} for row in result]
            
            # Get technology focus for each top applicant
            applicant_data = []
            for applicant in top_applicants:
                # Get IPC classes for this applicant
                sql_tech_focus = text("""
                    SELECT 
                        ipc.code AS ipc_code,
                        COUNT(DISTINCT p.id) AS patent_count
                    FROM patents p
                    JOIN applicants a ON a.patent_id = p.id
                    JOIN ipc_classifications ipc ON ipc.patent_id = p.id
                    WHERE a.name = :applicant_name
                    GROUP BY ipc_code
                    ORDER BY patent_count DESC
                    LIMIT 5
                """)
                
                result = self.db.execute(sql_tech_focus, {"applicant_name": applicant["name"]})
                tech_focus = [{"ipc_code": row[0], "count": row[1]} for row in result]
                
                # Get patent activity by year - adapted for SQLite
                sql_yearly = text("""
                    SELECT 
                        strftime('%Y', p.application_date) AS year,
                        COUNT(DISTINCT p.id) AS patent_count
                    FROM patents p
                    JOIN applicants a ON a.patent_id = p.id
                    WHERE 
                        a.name = :applicant_name AND
                        p.application_date IS NOT NULL
                    GROUP BY year
                    ORDER BY year
                """)
                
                result = self.db.execute(sql_yearly, {"applicant_name": applicant["name"]})
                yearly_activity = [{"year": int(row[0]), "count": row[1]} for row in result]
                
                # Add to applicant data
                applicant_data.append({
                    "name": applicant["name"],
                    "total_patents": applicant["patent_count"],
                    "technology_focus": tech_focus,
                    "yearly_activity": yearly_activity
                })
            
            # Find technology overlap between top applicants
            overlap_matrix = []
            applicant_names = [a["name"] for a in applicant_data]
            
            for i, name1 in enumerate(applicant_names):
                overlap_row = []
                for j, name2 in enumerate(applicant_names):
                    if i == j:
                        overlap_row.append(100)  # 100% overlap with self
                    else:
                        # Calculate technology overlap
                        overlap_pct = self._calculate_applicant_overlap(name1, name2)
                        overlap_row.append(overlap_pct)
                
                overlap_matrix.append(overlap_row)
            
            return {
                "top_applicants": applicant_data,
                "applicant_names": applicant_names,
                "technology_overlap": overlap_matrix
            }
            
        except Exception as e:
            logger.error(f"Error in applicant competition analysis: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def analyze_patent_landscape(self, ipc_level: int = 3) -> Dict[str, Any]:
        """
        Analyze patent landscape by IPC classification hierarchy
        
        Args:
            ipc_level: Level of IPC hierarchy for grouping (1=section, 2=class, 3=subclass)
            
        Returns:
            Dictionary with patent landscape analysis results
        """
        try:
            # Get IPC classifications with counts
            result = self.db.execute(text("""
                SELECT 
                    ipc.code AS ipc_code,
                    COUNT(DISTINCT p.id) AS patent_count
                FROM patents p
                JOIN ipc_classifications ipc ON ipc.patent_id = p.id
                GROUP BY ipc_code
                ORDER BY patent_count DESC
            """))
            
            all_ipc = [{"code": row[0], "count": row[1]} for row in result]
            
            # Parse IPC codes and group by hierarchy level
            ipc_hierarchy = defaultdict(int)
            
            for item in all_ipc:
                ipc_code = item["code"]
                count = item["count"]
                
                # Parse IPC code to get the level requested
                prefix = self._parse_ipc_code(ipc_code, ipc_level)
                if prefix:
                    ipc_hierarchy[prefix] += count
            
            # Convert to list for output
            landscape = [{"category": k, "count": v} for k, v in ipc_hierarchy.items()]
            landscape.sort(key=lambda x: x["count"], reverse=True)
            
            # Get descriptions for the IPC categories
            ipc_descriptions = self._get_ipc_class_descriptions([item["category"] for item in landscape])
            
            # Calculate clusters of related technologies
            clusters = self._cluster_ipc_categories(landscape[:30])  # Top 30 for clustering
            
            return {
                "landscape": landscape,
                "ipc_descriptions": ipc_descriptions,
                "clusters": clusters
            }
            
        except Exception as e:
            logger.error(f"Error in patent landscape analysis: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def generate_analysis_report(self) -> str:
        """
        Generate a comprehensive patent analysis report
        
        Returns:
            Markdown formatted string with analysis report
        """
        try:
            # Get basic statistics
            patent_count = self.db.query(Patent).count()
            
            # Count distinct applicants
            applicant_count_result = self.db.execute(text("""
                SELECT COUNT(DISTINCT name) FROM applicants
            """))
            applicant_count = applicant_count_result.fetchone()[0]
            
            # Count distinct inventors
            inventor_count_result = self.db.execute(text("""
                SELECT COUNT(DISTINCT name) FROM inventors
            """))
            inventor_count = inventor_count_result.fetchone()[0]
            
            # Get date range of patents - adapted for SQLite
            earliest_date_query = self.db.execute(text("""
                SELECT application_date FROM patents
                WHERE application_date IS NOT NULL
                ORDER BY application_date ASC
                LIMIT 1
            """))
            earliest_date_row = earliest_date_query.fetchone()
            
            latest_date_query = self.db.execute(text("""
                SELECT application_date FROM patents
                WHERE application_date IS NOT NULL
                ORDER BY application_date DESC
                LIMIT 1
            """))
            latest_date_row = latest_date_query.fetchone()
            
            earliest_date = datetime.fromisoformat(earliest_date_row[0]) if earliest_date_row else None
            latest_date = datetime.fromisoformat(latest_date_row[0]) if latest_date_row else None
            
            # Get technology trends
            tech_trends = self.analyze_technology_trends(years=5, top_n=5)
            
            # Get top applicants
            competition = self.analyze_applicant_competition(top_n=5)
            
            # Build report markdown
            report = f"""
# 特許分析レポート

## 概要
- **総特許数**: {patent_count}
- **出願者数**: {applicant_count} 
- **発明者数**: {inventor_count}
- **期間**: {earliest_date.strftime('%Y-%m-%d') if earliest_date else 'N/A'} から {latest_date.strftime('%Y-%m-%d') if latest_date else 'N/A'}

## 技術トレンド分析

過去5年間の主要技術分野の推移:

"""
            # Add technology trends section
            if "error" not in tech_trends:
                for tech in tech_trends["top_technologies"][:5]:
                    desc = tech_trends["technology_descriptions"].get(tech, "")
                    report += f"- **{tech}**: {desc}\n"
                
                report += "\n### 年次技術トレンド\n\n"
                report += "| 年 |"
                for tech in tech_trends["top_technologies"][:5]:
                    report += f" {tech} |"
                report += "\n|" + "---|" * (len(tech_trends["top_technologies"][:5]) + 1) + "\n"
                
                for year_data in sorted(tech_trends["yearly_trends"], key=lambda x: x["year"]):
                    report += f"| {year_data['year']} |"
                    for tech in tech_trends["top_technologies"][:5]:
                        report += f" {year_data.get(tech, 0)} |"
                    report += "\n"
            
            report += "\n## 主要出願者分析\n\n"
            
            # Add competition analysis
            if "error" not in competition:
                for applicant in competition["top_applicants"][:5]:
                    report += f"### {applicant['name']}\n\n"
                    report += f"- **総特許数**: {applicant['total_patents']}\n"
                    report += "- **主要技術分野**:\n"
                    
                    for tech in applicant["technology_focus"][:3]:
                        report += f"  - {tech['ipc_code']}: {tech['count']} 件\n"
                    
                    report += "\n"
            
            report += """
## 分析結果の要約

このレポートから読み取れる主要なインサイト:

1. 特許データベースには多様な技術分野の特許が含まれています。
2. 上位の出願者は特定の技術分野に集中する傾向があります。
3. 技術トレンドは年々変化しており、新しい技術領域が出現しています。

## 推奨事項

- 成長している技術分野への注目
- 競合他社の特許活動のモニタリング
- 技術的な差別化ポイントの特定
- オープンイノベーションの機会検討
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating analysis report: {str(e)}", exc_info=True)
            return f"# エラー\n\nレポート生成中にエラーが発生しました: {str(e)}"
    
    def _calculate_applicant_overlap(self, applicant1: str, applicant2: str) -> int:
        """Calculate technology overlap percentage between two applicants"""
        try:
            # Get IPC classes for each applicant
            sql = text("""
                SELECT DISTINCT ipc.code
                FROM patents p
                JOIN applicants a ON a.patent_id = p.id
                JOIN ipc_classifications ipc ON ipc.patent_id = p.id
                WHERE a.name = :applicant_name
            """)
            
            result1 = self.db.execute(sql, {"applicant_name": applicant1})
            result2 = self.db.execute(sql, {"applicant_name": applicant2})
            
            ipc_set1 = {row[0] for row in result1}
            ipc_set2 = {row[0] for row in result2}
            
            # Calculate overlap
            if not ipc_set1 or not ipc_set2:
                return 0
            
            # Get intersection and calculate percentage overlap
            intersection = ipc_set1.intersection(ipc_set2)
            smaller_set = min(len(ipc_set1), len(ipc_set2))
            
            if smaller_set == 0:
                return 0
                
            overlap_pct = (len(intersection) / smaller_set) * 100
            return round(overlap_pct)
            
        except Exception as e:
            logger.error(f"Error calculating applicant overlap: {str(e)}")
            return 0
    
    def _parse_ipc_code(self, ipc_code: str, level: int) -> Optional[str]:
        """Parse IPC code and return prefix based on hierarchy level"""
        # Clean up and normalize IPC code
        ipc_code = ipc_code.strip()
        
        # Basic IPC pattern: section(1) + class(2-3) + subclass(4) + group + subgroup
        # e.g., "G06F 16/00" -> section=G, class=06, subclass=F
        pattern = re.compile(r'^([A-H])(\d{2})([A-Z])')
        match = pattern.match(ipc_code)
        
        if not match:
            return None
            
        section = match.group(1)  # e.g., "G"
        class_num = match.group(2)  # e.g., "06"
        subclass = match.group(3)  # e.g., "F"
        
        if level == 1:
            return section  # section only
        elif level == 2:
            return f"{section}{class_num}"  # section + class
        else:
            return f"{section}{class_num}{subclass}"  # section + class + subclass
    
    def _get_ipc_class_descriptions(self, ipc_codes: List[str]) -> Dict[str, str]:
        """Get descriptions for IPC classes/categories"""
        # This is a simplified version. In a real implementation, 
        # you would look these up from an official IPC database
        ipc_descriptions = {
            # Sections
            "A": "人間の必需品",
            "B": "処理操作、運輸",
            "C": "化学、冶金",
            "D": "繊維、紙",
            "E": "固定構造物",
            "F": "機械工学、照明、加熱、武器、爆破",
            "G": "物理学",
            "H": "電気",
            
            # Some common classes
            "G06": "計算、計数",
            "G06F": "電気的デジタルデータ処理",
            "G06N": "コンピュータ・システムであって、特定の計算モデルに基づくもの",
            "G06Q": "管理目的、商業目的、金融目的、経営目的、監督目的または予測目的に特に適合したデータ処理システム／方法",
            "H04": "電気通信技術",
            "H04L": "デジタル情報の伝送",
            "H04N": "画像通信",
            "H01": "基本的電気素子",
            "H01L": "半導体装置",
            "A61": "医学または獣医学；衛生学",
            "A61K": "医薬用、歯科用または化粧用製剤",
            "B60": "車両一般",
            "C07": "有機化学",
            "C12": "生化学；ビール；酒精；ぶどう酒；酢；微生物学；酵素学；突然変異または遺伝子工学"
        }
        
        result = {}
        for code in ipc_codes:
            # Try to find the most specific description, falling back to more general ones
            if code in ipc_descriptions:
                result[code] = ipc_descriptions[code]
            elif len(code) >= 3 and code[:3] in ipc_descriptions:
                result[code] = ipc_descriptions[code[:3]]
            elif len(code) >= 1 and code[0] in ipc_descriptions:
                result[code] = ipc_descriptions[code[0]]
            else:
                result[code] = "説明が利用できません"
        
        return result
    
    def _cluster_ipc_categories(self, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create clusters of related IPC categories"""
        # This is a simplified version. In a real implementation, you would
        # use more sophisticated clustering algorithms or predefined IPC relationships
        
        # Simple clustering based on IPC section
        clusters = defaultdict(list)
        
        for item in categories:
            category = item["category"]
            if not category:
                continue
                
            # Use first character (section) as cluster key
            section = category[0] if len(category) > 0 else "Other"
            clusters[section].append(item)
        
        # Format clusters for output
        result = []
        for section, items in clusters.items():
            # Get section description
            description = self._get_ipc_class_descriptions([section]).get(section, "")
            
            result.append({
                "name": f"Section {section}",
                "description": description,
                "items": items,
                "total_patents": sum(item["count"] for item in items)
            })
        
        # Sort by total patents
        result.sort(key=lambda x: x["total_patents"], reverse=True)
        
        return result


# Convenience function to create analyzer
def get_analyzer(db_session=None):
    """Create a patent analyzer instance"""
    return PatentAnalyzerSQLite(db_session)


if __name__ == "__main__":
    # Run some basic analysis
    analyzer = get_analyzer()
    
    # Get basic statistics
    with analyzer:
        patent_count = analyzer.db.query(Patent).count()
        print(f"Patent count: {patent_count}")
        
        # Generate a report if we have data
        if patent_count > 0:
            report = analyzer.generate_analysis_report()
            print("\nAnalysis Report Preview:\n")
            print(report[:500] + "...\n")
