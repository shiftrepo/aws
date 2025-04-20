#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mock PatentAnalyzer for demonstration purposes
"""

from datetime import datetime, timedelta
import random

class MockPatentAnalyzer:
    """Mock implementation of PatentAnalyzer for demo purposes"""
    
    def __init__(self):
        """Initialize with mock data"""
        self.ipc_descriptions = {
            "G06F": "電気的デジタルデータ処理",
            "H04L": "デジタル情報の伝送",
            "G06Q": "管理目的、商業目的、金融目的などに特に適合したデータ処理システム",
            "G06N": "コンピュータ・システムであって、特定の計算モデルに基づくもの",
            "H04N": "画像通信",
            "H01L": "半導体装置",
            "A61K": "医薬用、歯科用または化粧用製剤",
            "G01N": "材料の化学的または物理的性質の検出による材料の調査または分析",
            "G02B": "光学要素、光学系、または光学装置",
            "B60W": "車両の複合的な制御",
            "G": "物理学",
            "H": "電気",
            "A": "人間の必需品",
            "B": "処理操作、運輸"
        }
        
        self.top_tech = ["G06F", "H04L", "G06Q", "G06N", "H04N", "H01L", "A61K", "G01N", "G02B", "B60W"]
        
        self.applicants = [
            {"name": "テック株式会社", "total_patents": 1250},
            {"name": "イノベーション製造", "total_patents": 980},
            {"name": "未来技研", "total_patents": 870},
            {"name": "データシステムズ", "total_patents": 790},
            {"name": "AIソリューションズ", "total_patents": 610}
        ]
        
    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
    
    def analyze_technology_trends(self, years=10, top_n=10):
        """Generate mock technology trend data"""
        # Generate yearly trends
        current_year = datetime.now().year
        yearly_trends = []
        
        # Select top N technologies
        top_technologies = self.top_tech[:top_n]
        
        # Generate data for each year
        for i in range(years):
            year = current_year - years + i + 1
            year_data = {"year": year}
            
            # Add counts for each technology
            for tech in top_technologies:
                # Generate increasing trend with some randomness
                base = 50 + (i * 8)  # Base count increases each year
                variation = random.randint(-10, 20)  # Random variation
                year_data[tech] = max(1, base + variation)  # Ensure minimum of 1
            
            yearly_trends.append(year_data)
        
        # Create technology descriptions
        tech_descriptions = {}
        for tech in top_technologies:
            tech_descriptions[tech] = self.ipc_descriptions.get(tech, f"{tech}に関する技術")
        
        return {
            "top_technologies": top_technologies,
            "technology_descriptions": tech_descriptions,
            "yearly_trends": yearly_trends
        }
    
    def analyze_applicant_competition(self, top_n=10):
        """Generate mock applicant competition data"""
        # Get top applicants
        top_applicants = self.applicants[:top_n]
        
        # Generate technology focus for each applicant
        for applicant in top_applicants:
            # Randomly select 3-5 technologies
            num_techs = random.randint(3, 5)
            selected_techs = random.sample(self.top_tech, num_techs)
            
            tech_focus = []
            for tech in selected_techs:
                tech_focus.append({
                    "ipc_code": tech,
                    "count": random.randint(50, 200)
                })
            
            # Sort by count descending
            tech_focus.sort(key=lambda x: x["count"], reverse=True)
            applicant["technology_focus"] = tech_focus
            
            # Add yearly activity
            current_year = datetime.now().year
            yearly_activity = []
            for i in range(5):
                year = current_year - 5 + i + 1
                yearly_activity.append({
                    "year": year,
                    "count": random.randint(20, 100)
                })
            applicant["yearly_activity"] = yearly_activity
        
        # Generate overlap matrix
        applicant_names = [a["name"] for a in top_applicants]
        overlap_matrix = []
        
        for i in range(len(applicant_names)):
            row = []
            for j in range(len(applicant_names)):
                if i == j:
                    row.append(100)  # 100% overlap with self
                else:
                    # Random overlap between 10% and 70%
                    row.append(random.randint(10, 70))
            overlap_matrix.append(row)
        
        return {
            "top_applicants": top_applicants,
            "applicant_names": applicant_names,
            "technology_overlap": overlap_matrix
        }
    
    def analyze_patent_landscape(self, ipc_level=3):
        """Generate mock patent landscape data"""
        # Create landscape data
        landscape = []
        
        # Sections for level 1
        if ipc_level == 1:
            categories = ["A", "B", "C", "D", "E", "F", "G", "H"]
        # Classes for level 2
        elif ipc_level == 2:
            categories = ["G06", "H04", "A61", "B60", "C07", "G01", "H01", "G02"]
        # Subclasses for level 3
        else:
            categories = self.top_tech
        
        for category in categories:
            landscape.append({
                "category": category,
                "count": random.randint(100, 1000)
            })
        
        # Sort by count descending
        landscape.sort(key=lambda x: x["count"], reverse=True)
        
        # Generate clusters
        clusters = []
        if ipc_level == 1:
            cluster_bases = ["A", "B", "G", "H"]
        elif ipc_level == 2:
            cluster_bases = ["G06", "H04", "A61", "B60"]
        else:
            cluster_bases = ["G06F", "H04L", "G06Q", "H01L"]
        
        for base in cluster_bases:
            # Get relevant categories
            items = [item for item in landscape if item["category"].startswith(base)]
            
            if items:
                clusters.append({
                    "name": f"Section {base[0]}",
                    "description": self.ipc_descriptions.get(base[0], base),
                    "items": items,
                    "total_patents": sum(item["count"] for item in items)
                })
        
        # Sort clusters by total patents
        clusters.sort(key=lambda x: x["total_patents"], reverse=True)
        
        return {
            "landscape": landscape,
            "ipc_descriptions": self.ipc_descriptions,
            "clusters": clusters
        }
    
    def generate_analysis_report(self):
        """Generate a mock comprehensive analysis report"""
        # Get trend and competition data
        trends = self.analyze_technology_trends(years=5, top_n=5)
        competition = self.analyze_applicant_competition(top_n=5)
        
        # Build report markdown
        report = f"""
# 特許分析レポート

## 概要
- **総特許数**: 12,345
- **出願者数**: 987
- **発明者数**: 2,345
- **期間**: 2015-01-15 から {datetime.now().strftime('%Y-%m-%d')}

## 技術トレンド分析

過去5年間の主要技術分野の推移:

"""
        # Add technology trends section
        for tech in trends["top_technologies"][:5]:
            desc = trends["technology_descriptions"].get(tech, "")
            report += f"- **{tech}**: {desc}\n"
        
        report += "\n### 年次技術トレンド\n\n"
        report += "| 年 |"
        for tech in trends["top_technologies"][:5]:
            report += f" {tech} |"
        report += "\n|" + "---|" * (len(trends["top_technologies"][:5]) + 1) + "\n"
        
        for year_data in sorted(trends["yearly_trends"], key=lambda x: x["year"]):
            report += f"| {year_data['year']} |"
            for tech in trends["top_technologies"][:5]:
                report += f" {year_data.get(tech, 0)} |"
            report += "\n"
        
        report += "\n## 主要出願者分析\n\n"
        
        # Add competition analysis
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
