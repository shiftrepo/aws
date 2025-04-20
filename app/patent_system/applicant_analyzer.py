#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Specialized patent applicant analyzer for patent examiners
"""

from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import numpy as np
from .mock_analyzer import MockPatentAnalyzer

class ApplicantAnalyzer:
    """Specialized analyzer for applicant-focused patent examination"""
    
    def __init__(self):
        """Initialize with base patent analyzer"""
        self.base_analyzer = MockPatentAnalyzer()
        
        # Define possible patent statuses
        self.patent_statuses = ["granted", "rejected", "pending", "withdrawn", "appealed"]
        
        # Define technical domains beyond IPC codes
        self.technical_domains = {
            "AI": ["G06N", "G06F16", "G06F17"],
            "IoT": ["H04L29", "H04W4", "G08C17"],
            "Quantum Computing": ["G06N10", "H01L39"],
            "Blockchain": ["G06Q20", "H04L9"],
            "Renewable Energy": ["H02J3", "H01L31", "F03D"],
            "Autonomous Vehicles": ["G05D1", "B60W30", "G08G1"],
            "Biotechnology": ["C12N", "C07K", "A61K38"],
            "AR/VR": ["G06T19", "G02B27", "H04N13"],
            "5G Communication": ["H04W72", "H04B7", "H04L5"],
            "Advanced Materials": ["C01B", "C22C", "B82Y"]
        }

    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass

    def get_applicant_summary(self, applicant_name):
        """
        Generate a comprehensive summary for a specified patent applicant
        
        Args:
            applicant_name (str): Name of the applicant to analyze
            
        Returns:
            dict: Comprehensive summary data
        """
        # Find or generate applicant data
        applicant = self._get_or_create_applicant(applicant_name)
        
        # Generate assessment statistics
        assessment_stats = self._generate_assessment_statistics(applicant)
        
        # Generate application history
        application_history = self._generate_application_history(applicant)
        
        # Generate technical field distribution
        tech_distribution = self._generate_technical_distribution(applicant)
        
        # Generate examiner insights
        examiner_insights = self._generate_examiner_insights(applicant, assessment_stats)
        
        # Include comparison with industry
        industry_comparison = self._generate_industry_comparison(applicant)
        
        return {
            "applicant": applicant,
            "assessment_statistics": assessment_stats,
            "application_history": application_history,
            "technical_distribution": tech_distribution,
            "examiner_insights": examiner_insights,
            "industry_comparison": industry_comparison
        }

    def generate_visual_report(self, applicant_name):
        """
        Generate visual report for a specified applicant
        
        Args:
            applicant_name (str): Name of the applicant
            
        Returns:
            dict: Report with embedded visualizations
        """
        # Get applicant summary data
        summary = self.get_applicant_summary(applicant_name)
        
        # Generate visualizations
        visualizations = {
            "assessment_chart": self._create_assessment_ratio_chart(summary["assessment_statistics"]),
            "application_trend": self._create_application_trend_chart(summary["application_history"]),
            "tech_distribution": self._create_tech_distribution_chart(summary["technical_distribution"]),
            "industry_comparison": self._create_industry_comparison_chart(summary["industry_comparison"])
        }
        
        # Format markdown report
        markdown_report = self._format_markdown_report(summary, visualizations)
        
        return {
            "summary": summary,
            "visualizations": visualizations,
            "markdown_report": markdown_report
        }
    
    def analyze_assessment_ratios(self, applicant_name):
        """
        Analyze the assessment ratios (granted, rejected, etc.) for a specific applicant
        
        Args:
            applicant_name (str): Name of the applicant
            
        Returns:
            dict: Assessment ratio data and visualization
        """
        # Get applicant data
        applicant = self._get_or_create_applicant(applicant_name)
        
        # Generate assessment statistics
        stats = self._generate_assessment_statistics(applicant)
        
        # Create visualization
        visualization = self._create_assessment_ratio_chart(stats)
        
        return {
            "applicant_name": applicant_name,
            "total_patents": applicant["total_patents"],
            "assessment_data": stats,
            "visualization": visualization
        }
    
    def analyze_technical_fields(self, applicant_name):
        """
        Analyze the technical fields distribution for a specific applicant
        
        Args:
            applicant_name (str): Name of the applicant
            
        Returns:
            dict: Technical field distribution data and visualization
        """
        # Get applicant data
        applicant = self._get_or_create_applicant(applicant_name)
        
        # Generate technical distribution
        tech_dist = self._generate_technical_distribution(applicant)
        
        # Create visualization
        visualization = self._create_tech_distribution_chart(tech_dist)
        
        # Add domain analysis
        domain_analysis = self._analyze_technical_domains(tech_dist)
        
        return {
            "applicant_name": applicant_name,
            "total_patents": applicant["total_patents"],
            "technical_fields": tech_dist,
            "domain_analysis": domain_analysis,
            "visualization": visualization
        }
    
    def compare_with_competitors(self, applicant_name, num_competitors=3):
        """
        Compare the applicant with top competitors
        
        Args:
            applicant_name (str): Name of the applicant
            num_competitors (int): Number of competitors to compare with
            
        Returns:
            dict: Competitor comparison data
        """
        # Get applicant data
        applicant = self._get_or_create_applicant(applicant_name)
        
        # Get or generate competitor data
        competitors_data = []
        for i in range(num_competitors):
            competitor_name = f"Competitor {i+1}"
            competitor = self._get_or_create_applicant(competitor_name)
            
            # Generate assessment stats for competitor
            assessment_stats = self._generate_assessment_statistics(competitor)
            
            # Generate tech distribution for competitor
            tech_dist = self._generate_technical_distribution(competitor)
            
            competitors_data.append({
                "name": competitor_name,
                "total_patents": competitor["total_patents"],
                "assessment_stats": assessment_stats,
                "tech_distribution": tech_dist
            })
        
        # Generate comparative visualizations
        assessment_comparison = self._create_comparative_assessment_chart(applicant, competitors_data)
        field_comparison = self._create_comparative_field_chart(applicant, competitors_data)
        
        return {
            "applicant": {
                "name": applicant_name,
                "total_patents": applicant["total_patents"]
            },
            "competitors": competitors_data,
            "assessment_comparison": assessment_comparison,
            "field_comparison": field_comparison
        }

    def _get_or_create_applicant(self, applicant_name):
        """
        Get or create applicant data
        
        Args:
            applicant_name (str): Name of the applicant
            
        Returns:
            dict: Applicant data
        """
        # Check if the applicant is one of the defaults from the base analyzer
        for applicant in self.base_analyzer.applicants:
            if applicant["name"] == applicant_name:
                return applicant
        
        # Create a new applicant with mock data
        return {
            "name": applicant_name,
            "total_patents": random.randint(100, 2000)
        }

    def _generate_assessment_statistics(self, applicant):
        """
        Generate assessment statistics for an applicant
        
        Args:
            applicant (dict): Applicant data
            
        Returns:
            dict: Assessment statistics
        """
        total_patents = applicant["total_patents"]
        
        # Generate random percentages for different statuses
        granted_pct = random.uniform(0.4, 0.7)
        rejected_pct = random.uniform(0.1, 0.3)
        pending_pct = random.uniform(0.1, 0.2)
        other_pct = 1 - granted_pct - rejected_pct - pending_pct
        
        # Calculate counts
        granted_count = int(total_patents * granted_pct)
        rejected_count = int(total_patents * rejected_pct)
        pending_count = int(total_patents * pending_pct)
        withdrawn_count = int(total_patents * other_pct * 0.7)
        appealed_count = total_patents - granted_count - rejected_count - pending_count - withdrawn_count
        
        # Calculate average processing time (in days)
        avg_processing_time = random.randint(18, 36) * 30
        
        # Calculate average number of office actions
        avg_office_actions = random.uniform(1.5, 4.0)
        
        # Calculate grant rate over time
        current_year = datetime.now().year
        grant_rate_over_time = []
        for i in range(5):
            year = current_year - 5 + i + 1
            rate = granted_pct + random.uniform(-0.1, 0.1)
            # Make sure rate is between 0 and 1
            rate = max(0, min(1, rate))
            grant_rate_over_time.append({
                "year": year,
                "rate": rate
            })
        
        return {
            "total_patents": total_patents,
            "status_distribution": {
                "granted": granted_count,
                "rejected": rejected_count,
                "pending": pending_count,
                "withdrawn": withdrawn_count,
                "appealed": appealed_count
            },
            "grant_rate": granted_pct,
            "rejection_rate": rejected_pct,
            "average_processing_time_days": avg_processing_time,
            "average_office_actions": avg_office_actions,
            "grant_rate_over_time": grant_rate_over_time
        }

    def _generate_application_history(self, applicant):
        """
        Generate application history for an applicant
        
        Args:
            applicant (dict): Applicant data
            
        Returns:
            dict: Application history data
        """
        total_patents = applicant["total_patents"]
        current_year = datetime.now().year
        
        # Generate yearly data for the past 10 years
        yearly_data = []
        remaining_count = total_patents
        
        for i in range(10):
            year = current_year - 10 + i + 1
            
            # Generate count with an increasing trend
            if i == 9:  # Last year
                count = remaining_count
            else:
                base_count = total_patents / 15  # Average patents per year
                growth_factor = 1 + (i * 0.1)  # Increase over time
                variation = random.uniform(0.8, 1.2)  # Random variation
                count = int(base_count * growth_factor * variation)
                count = min(count, remaining_count)
                remaining_count -= count
            
            yearly_data.append({
                "year": year,
                "count": count
            })
        
        # Generate quarterly data for the current year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        quarterly_data = []
        
        last_year_count = yearly_data[-1]["count"]
        remaining_count = last_year_count
        
        for i in range(4):
            quarter = i + 1
            
            if quarter > current_quarter:
                # Future quarter, no data
                count = 0
            elif quarter == current_quarter:
                # Current quarter, partial data
                progress = (datetime.now().month - ((quarter - 1) * 3)) / 3
                count = int(last_year_count / 4 * progress)
                remaining_count -= count
            else:
                # Past quarter, complete data
                if quarter == 4:
                    count = remaining_count
                else:
                    base_count = last_year_count / 4
                    variation = random.uniform(0.8, 1.2)
                    count = int(base_count * variation)
                    count = min(count, remaining_count)
                    remaining_count -= count
            
            quarterly_data.append({
                "year": current_year,
                "quarter": quarter,
                "count": count
            })
        
        return {
            "yearly_data": yearly_data,
            "quarterly_data": quarterly_data
        }

    def _generate_technical_distribution(self, applicant):
        """
        Generate technical field distribution for an applicant
        
        Args:
            applicant (dict): Applicant data
            
        Returns:
            list: Technical field distribution
        """
        total_patents = applicant["total_patents"]
        
        # Select 5-8 random IPC codes
        num_codes = random.randint(5, 8)
        selected_codes = random.sample(self.base_analyzer.top_tech, num_codes)
        
        # Generate distribution
        remaining = total_patents
        distribution = []
        
        for i, code in enumerate(selected_codes):
            if i == len(selected_codes) - 1:
                # Last code, assign remaining count
                count = remaining
            else:
                # Generate a random count
                max_count = remaining - (len(selected_codes) - i - 1)
                # Ensure max_count is at least 10
                if max_count < 10:
                    count = max_count
                else:
                    count = random.randint(10, max_count)
                remaining -= count
            
            distribution.append({
                "ipc_code": code,
                "description": self.base_analyzer.ipc_descriptions.get(code, f"{code}に関する技術"),
                "count": count,
                "percentage": (count / total_patents) * 100
            })
        
        # Sort by count in descending order
        distribution.sort(key=lambda x: x["count"], reverse=True)
        
        return distribution

    def _generate_examiner_insights(self, applicant, stats):
        """
        Generate examiner insights for an applicant
        
        Args:
            applicant (dict): Applicant data
            stats (dict): Assessment statistics
            
        Returns:
            list: Examiner insights
        """
        # Generate insights based on the statistics
        grant_rate = stats["grant_rate"]
        rejection_rate = stats["rejection_rate"]
        avg_office_actions = stats["average_office_actions"]
        
        insights = []
        
        # Grant rate insight
        if grant_rate > 0.6:
            insights.append({
                "type": "grant_rate",
                "level": "high",
                "description": f"高い特許査定率 ({grant_rate:.1%}) は、この出願人の特許戦略が効果的であることを示唆しています。",
                "recommendation": "同様の技術分野の他の出願を参照することで、高品質な特許の特徴を理解できる可能性があります。"
            })
        elif grant_rate < 0.4:
            insights.append({
                "type": "grant_rate",
                "level": "low",
                "description": f"低い特許査定率 ({grant_rate:.1%}) は、この出願人の出願の質または新規性に課題があることを示唆しています。",
                "recommendation": "拒絶理由を分析し、一般的な拒絶パターンがないか確認することをお勧めします。"
            })
        else:
            insights.append({
                "type": "grant_rate",
                "level": "average",
                "description": f"平均的な特許査定率 ({grant_rate:.1%}) は、この出願人が業界標準に沿った特許戦略を持っていることを示唆しています。",
                "recommendation": "特定の技術分野での査定率の違いを分析すると、有益な洞察が得られる可能性があります。"
            })
        
        # Office actions insight
        if avg_office_actions > 3.0:
            insights.append({
                "type": "office_actions",
                "level": "high",
                "description": f"平均オフィスアクション数が多い ({avg_office_actions:.1f}) ことは、出願の明確さまたは新規性に課題がある可能性を示唆しています。",
                "recommendation": "過去のオフィスアクションでの一般的な拒絶理由を分析し、パターンを特定することが有用かもしれません。"
            })
        elif avg_office_actions < 2.0:
            insights.append({
                "type": "office_actions",
                "level": "low",
                "description": f"平均オフィスアクション数が少ない ({avg_office_actions:.1f}) ことは、明確で十分に記述された出願である可能性を示唆しています。",
                "recommendation": "これらの出願の特徴を分析し、高品質な出願の要素を特定すると良いでしょう。"
            })
        
        # Add technical field insight
        insights.append({
            "type": "technical_focus",
            "level": "information",
            "description": f"この出願人は主に {applicant.get('technology_focus', [{'ipc_code': 'G06F'}])[0]['ipc_code']} の分野に集中しています。",
            "recommendation": "この技術分野での先行技術を十分に理解することで、より効果的な審査が可能になります。"
        })
        
        return insights

    def _generate_industry_comparison(self, applicant):
        """
        Generate industry comparison for an applicant
        
        Args:
            applicant (dict): Applicant data
            
        Returns:
            dict: Industry comparison data
        """
        # Generate industry averages
        industry_grant_rate = 0.55  # 55% grant rate
        industry_avg_office_actions = 2.5
        industry_avg_processing_time = 730  # days
        
        # Generate applicant stats
        applicant_stats = self._generate_assessment_statistics(applicant)
        applicant_grant_rate = applicant_stats["grant_rate"]
        applicant_avg_office_actions = applicant_stats["average_office_actions"]
        applicant_avg_processing_time = applicant_stats["average_processing_time_days"]
        
        # Calculate differences
        grant_rate_diff = applicant_grant_rate - industry_grant_rate
        office_actions_diff = applicant_avg_office_actions - industry_avg_office_actions
        processing_time_diff = applicant_avg_processing_time - industry_avg_processing_time
        
        # Determine comparison level
        get_level = lambda diff: "above" if diff > 0 else "below" if diff < 0 else "average"
        
        return {
            "industry_averages": {
                "grant_rate": industry_grant_rate,
                "avg_office_actions": industry_avg_office_actions,
                "avg_processing_time_days": industry_avg_processing_time
            },
            "applicant_values": {
                "grant_rate": applicant_grant_rate,
                "avg_office_actions": applicant_avg_office_actions,
                "avg_processing_time_days": applicant_avg_processing_time
            },
            "comparisons": {
                "grant_rate": {
                    "difference": grant_rate_diff,
                    "percentage_difference": (grant_rate_diff / industry_grant_rate) * 100,
                    "level": get_level(grant_rate_diff)
                },
                "avg_office_actions": {
                    "difference": office_actions_diff,
                    "percentage_difference": (office_actions_diff / industry_avg_office_actions) * 100,
                    "level": get_level(office_actions_diff)
                },
                "avg_processing_time": {
                    "difference": processing_time_diff,
                    "percentage_difference": (processing_time_diff / industry_avg_processing_time) * 100,
                    "level": get_level(processing_time_diff)
                }
            }
        }

    def _analyze_technical_domains(self, tech_distribution):
        """
        Analyze the technical domains based on IPC codes
        
        Args:
            tech_distribution (list): Technical field distribution
            
        Returns:
            dict: Domain analysis
        """
        # Map IPC codes to domains
        domain_counts = {}
        unmapped_codes = []
        
        for item in tech_distribution:
            code = item["ipc_code"]
            count = item["count"]
            
            # Try to map to domains
            mapped = False
            for domain, codes in self.technical_domains.items():
                for domain_code in codes:
                    if code.startswith(domain_code):
                        if domain not in domain_counts:
                            domain_counts[domain] = 0
                        domain_counts[domain] += count
                        mapped = True
                        break
                
                if mapped:
                    break
            
            if not mapped:
                unmapped_codes.append({
                    "code": code,
                    "count": count
                })
        
        # Convert to list of domains
        domains = []
        total_count = sum([item["count"] for item in tech_distribution])
        
        for domain, count in domain_counts.items():
            domains.append({
                "name": domain,
                "count": count,
                "percentage": (count / total_count) * 100 if total_count > 0 else 0
            })
        
        # Sort domains by count
        domains.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "domains": domains,
            "unmapped_codes": unmapped_codes
        }

    def _create_assessment_ratio_chart(self, stats):
        """
        Create an assessment ratio chart as base64 encoded image
        
        Args:
            stats (dict): Assessment statistics
            
        Returns:
            str: Base64 encoded image
        """
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract data
        status_dist = stats["status_distribution"]
        labels = list(status_dist.keys())
        sizes = list(status_dist.values())
        
        # Generate colors
        colors = ['#4CAF50', '#F44336', '#2196F3', '#FFC107', '#9C27B0']
        
        # Create pie chart - filter out any zero or negative values
        positive_sizes = []
        positive_labels = []
        positive_colors = []
        for i, size in enumerate(sizes):
            if size > 0:
                positive_sizes.append(size)
                positive_labels.append(labels[i])
                positive_colors.append(colors[i])
        
        wedges, texts, autotexts = ax.pie(
            positive_sizes, 
            labels=None, 
            autopct='%1.1f%%',
            startangle=90,
            colors=positive_colors
        )
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Add title
        ax.set_title('出願審査結果の分布', fontsize=14)
        
        # Add legend - only use labels from positive values
        ax.legend(
            wedges, 
            [f"{label} ({size}件)" for label, size in zip(positive_labels, positive_sizes)],
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        
        # Save to an in-memory bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Encode the image to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64

    def _create_application_trend_chart(self, history):
        """
        Create an application trend chart as base64 encoded image
        
        Args:
            history (dict): Application history
            
        Returns:
            str: Base64 encoded image
        """
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Extract yearly data
        years = [data["year"] for data in history["yearly_data"]]
        counts = [data["count"] for data in history["yearly_data"]]
        
        # Create bar chart
        ax.bar(years, counts, color='#2196F3')
        
        # Add labels and title
        ax.set_xlabel('年', fontsize=12)
        ax.set_ylabel('出願数', fontsize=12)
        ax.set_title('年別出願数推移', fontsize=14)
        
        # Add grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Save to an in-memory bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Encode the image to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64

    def _create_tech_distribution_chart(self, tech_dist):
        """
        Create a technical distribution chart as base64 encoded image
        
        Args:
            tech_dist (list): Technical field distribution
            
        Returns:
            str: Base64 encoded image
        """
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract data
        codes = [f"{item['ipc_code']}" for item in tech_dist]
        counts = [item["count"] for item in tech_dist]
        
        # Sort by count
        sorted_indices = np.argsort(counts)
        codes = [codes[i] for i in sorted_indices]
        counts = [counts[i] for i in sorted_indices]
        
        # Create horizontal bar chart
        y_pos = np.arange(len(codes))
        ax.barh(y_pos, counts, color='#4CAF50')
        
        # Add labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(codes)
        ax.set_xlabel('特許数', fontsize=12)
        ax.set_title('技術分野別出願分布', fontsize=14)
        
        # Add count values at the end of each bar
        for i, count in enumerate(counts):
            ax.text(count + 0.5, i, str(count), va='center')
        
        # Save to an in-memory bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Encode the image to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64

    def _create_industry_comparison_chart(self, comparison):
        """
        Create an industry comparison chart as base64 encoded image
        
        Args:
            comparison (dict): Industry comparison data
            
        Returns:
            str: Base64 encoded image
        """
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract data
        metrics = ['特許査定率', '平均オフィスアクション数', '平均処理時間 (月)']
        
        industry_values = [
            comparison["industry_averages"]["grant_rate"] * 100,
            comparison["industry_averages"]["avg_office_actions"],
            comparison["industry_averages"]["avg_processing_time_days"] / 30  # Convert days to months
        ]
        
        applicant_values = [
            comparison["applicant_values"]["grant_rate"] * 100,
            comparison["applicant_values"]["avg_office_actions"],
            comparison["applicant_values"]["avg_processing_time_days"] / 30  # Convert days to months
        ]
        
        # Set up bar chart
        x = np.arange(len(metrics))
        width = 0.35
        
        # Create bars
        ax.bar(x - width/2, industry_values, width, label='業界平均', color='#2196F3')
        ax.bar(x + width/2, applicant_values, width, label='対象出願人', color='#FF9800')
        
        # Add labels and title
        ax.set_ylabel('値', fontsize=12)
        ax.set_title('業界平均との比較', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        
        # Add value labels on top of bars
        def add_labels(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(
                    f'{height:.1f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom'
                )
        
        add_labels(ax.patches[:len(metrics)])
        add_labels(ax.patches[len(metrics):])
        
        # Save to an in-memory bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Encode the image to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64

    def _create_comparative_assessment_chart(self, applicant, competitors):
        """
        Create a comparative assessment chart as base64 encoded image
        
        Args:
            applicant (dict): Applicant data
            competitors (list): Competitor data
            
        Returns:
            str: Base64 encoded image
        """
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Extract data
        names = [applicant["name"]] + [comp["name"] for comp in competitors]
        grant_rates = [self._generate_assessment_statistics(applicant)["grant_rate"] * 100]
        
        for comp in competitors:
            grant_rates.append(comp["assessment_stats"]["grant_rate"] * 100)
        
        # Create bar chart
        colors = ['#4CAF50'] + ['#2196F3'] * len(competitors)
        x = np.arange(len(names))
        ax.bar(x, grant_rates, color=colors)
        
        # Add labels and title
        ax.set_xlabel('出願人', fontsize=12)
        ax.set_ylabel('特許査定率 (%)', fontsize=12)
        ax.set_title('査定率の比較', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        
        # Add value labels on top of bars
        for i, v in enumerate(grant_rates):
            ax.text(i, v + 1, f'{v:.1f}%', ha='center')
        
        # Add grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save to an in-memory bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Encode the image to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
        
    def _create_comparative_field_chart(self, applicant, competitors):
        """
        Create a comparative field distribution chart as base64 encoded image
        
        Args:
            applicant (dict): Applicant data
            competitors (list): Competitor data
            
        Returns:
            str: Base64 encoded image
        """
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Generate technical distribution for the applicant
        applicant_tech = self._generate_technical_distribution(applicant)
        
        # Get top 5 tech fields from applicant
        top_fields = [item["ipc_code"] for item in applicant_tech[:5]]
        
        # Extract data for chart
        field_labels = top_fields
        company_names = [applicant["name"]] + [comp["name"] for comp in competitors]
        
        # Create data structure for grouped bar chart
        data = {}
        for field in field_labels:
            data[field] = []
            
            # Add applicant data
            found = False
            for item in applicant_tech:
                if item["ipc_code"] == field:
                    data[field].append(item["percentage"])
                    found = True
                    break
            if not found:
                data[field].append(0)
            
            # Add competitors data
            for comp in competitors:
                found = False
                for item in comp["tech_distribution"]:
                    if item["ipc_code"] == field:
                        data[field].append(item["percentage"])
                        found = True
                        break
                if not found:
                    data[field].append(0)
        
        # Set up grouped bar chart
        x = np.arange(len(company_names))
        width = 0.15
        num_fields = len(field_labels)
        offsets = np.linspace(-(width * (num_fields-1))/2, (width * (num_fields-1))/2, num_fields)
        
        # Create bars for each field
        for i, field in enumerate(field_labels):
            ax.bar(x + offsets[i], data[field], width, label=field)
        
        # Add labels and title
        ax.set_xlabel('企業', fontsize=12)
        ax.set_ylabel('技術分野の割合 (%)', fontsize=12)
        ax.set_title('主要技術分野の企業間比較', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(company_names, rotation=45, ha='right')
        ax.legend(title="技術分野 (IPC)")
        
        # Add grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save to an in-memory bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Encode the image to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
        
    def _format_markdown_report(self, summary, visualizations):
        """
        Format summary data and visualizations into a markdown report
        
        Args:
            summary (dict): Summary data
            visualizations (dict): Visualization images as base64 strings
            
        Returns:
            str: Markdown report
        """
        applicant = summary["applicant"]
        stats = summary["assessment_statistics"]
        tech_dist = summary["technical_distribution"]
        insights = summary["examiner_insights"]
        app_history = summary["application_history"]
        
        # Create markdown report
        markdown = f"""
# 出願人分析レポート: {applicant["name"]}

## 要約
- **総特許出願数**: {applicant["total_patents"]}件
- **特許査定率**: {stats["grant_rate"]:.1%}
- **平均処理時間**: {stats["average_processing_time_days"] / 30:.1f}ヶ月
- **平均オフィスアクション**: {stats["average_office_actions"]:.1f}回

## 審査結果の分布

![審査結果の分布](data:image/png;base64,{visualizations["assessment_chart"]})

## 出願トレンド分析

過去10年間の出願数推移:

![出願数推移](data:image/png;base64,{visualizations["application_trend"]})

## 技術分野別分布

主要技術分野の分布:

![技術分野別分布](data:image/png;base64,{visualizations["tech_distribution"]})

### 主要技術分野
"""

        for i, item in enumerate(tech_dist[:5]):
            markdown += f"{i+1}. **{item['ipc_code']}**: {item['description']} - {item['count']}件 ({item['percentage']:.1f}%)\n"
        
        markdown += f"""
## 業界平均との比較

![業界平均との比較](data:image/png;base64,{visualizations["industry_comparison"]})

## 審査官向け洞察

"""
        for insight in insights:
            markdown += f"### {insight['type'].replace('_', ' ').title()}\n"
            markdown += f"**レベル**: {insight['level']}\n\n"
            markdown += f"{insight['description']}\n\n"
            markdown += f"**推奨**: {insight['recommendation']}\n\n"
        
        markdown += f"""
## 分析レポート生成日
{datetime.now().strftime('%Y年%m月%d日')}
"""
        
        return markdown
