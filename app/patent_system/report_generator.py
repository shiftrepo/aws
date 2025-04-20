#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
特許分析レポート生成モジュール

このモジュールは、特許データの分析結果をPDFレポートとして生成する機能を提供します。
主な機能：
1. 特許分類別の出願数を表した年別の棒グラフ生成
2. 特許査定、拒絶査定、その他査定の比率を表した円グラフ生成
3. 分析結果をPDFレポートとして出力
"""

import os
import io
import base64
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle

from .mock_analyzer import MockPatentAnalyzer

class PatentReportGenerator:
    """特許分析レポート生成クラス"""
    
    def __init__(self, analyzer=None):
        """
        初期化
        
        Args:
            analyzer: 特許分析器（指定がなければMockPatentAnalyzerを使用）
        """
        self.analyzer = analyzer if analyzer else MockPatentAnalyzer()
    
    def __enter__(self):
        """コンテキストマネージャのエントリー"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャの終了"""
        pass
    
    def generate_classification_trend_chart(self, years=10, top_n=5):
        """
        特許分類別の年次出願数トレンドグラフを生成
        
        Args:
            years (int): 分析する年数
            top_n (int): 表示する上位分類数
        
        Returns:
            str: Base64でエンコードされたグラフ画像
        """
        # 技術トレンドデータを取得
        trend_data = self.analyzer.analyze_technology_trends(years=years, top_n=top_n)
        
        # データフレーム作成のための辞書
        data_dict = {'年': [item['year'] for item in trend_data['yearly_trends']]}
        
        # 各技術分野のデータを追加
        for tech in trend_data['top_technologies'][:top_n]:
            data_dict[tech] = [item.get(tech, 0) for item in trend_data['yearly_trends']]
        
        # データフレーム作成
        df = pd.DataFrame(data_dict)
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 棒グラフの幅を計算
        width = 0.8 / top_n
        
        # 各分類ごとに棒グラフを描画
        for i, tech in enumerate(trend_data['top_technologies'][:top_n]):
            x = np.arange(len(df))
            offset = (i - top_n/2 + 0.5) * width
            ax.bar(x + offset, df[tech], width, label=f"{tech}: {trend_data['technology_descriptions'].get(tech, '')}")
        
        # グラフの装飾設定
        ax.set_xlabel('年', fontsize=12)
        ax.set_ylabel('出願数', fontsize=12)
        ax.set_title('特許分類別の年次出願数推移', fontsize=14)
        ax.set_xticks(np.arange(len(df)))
        ax.set_xticklabels(df['年'])
        ax.legend(loc='upper left', bbox_to_anchor=(0, -0.15), ncol=2)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # グラフを画像としてメモリに保存
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Base64エンコード
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    
    def generate_assessment_ratio_chart(self, applicant_name=None):
        """
        特許査定、拒絶査定、その他査定の比率を表した円グラフを生成
        
        Args:
            applicant_name (str, optional): 出願人名（指定がない場合は全体の比率を計算）
        
        Returns:
            str: Base64でエンコードされたグラフ画像
        """
        # 審査結果データを取得
        if applicant_name:
            from .applicant_analyzer import ApplicantAnalyzer
            app_analyzer = ApplicantAnalyzer()
            applicant = app_analyzer._get_or_create_applicant(applicant_name)
            stats = app_analyzer._generate_assessment_statistics(applicant)
        else:
            # 全体の統計を生成（ここではモック）
            stats = {
                "total_patents": 12345,
                "status_distribution": {
                    "granted": 6543,
                    "rejected": 2109,
                    "pending": 2876,
                    "withdrawn": 687,
                    "appealed": 130
                },
                "grant_rate": 0.53,
                "rejection_rate": 0.17,
                "average_processing_time_days": 730,
                "average_office_actions": 2.3
            }
        
        # 円グラフの作成
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # データ抽出
        status_dist = stats["status_distribution"]
        labels = ["特許査定", "拒絶査定", "審査中", "取下げ", "審判請求中"]
        sizes = [
            status_dist["granted"],
            status_dist["rejected"],
            status_dist["pending"],
            status_dist["withdrawn"],
            status_dist["appealed"]
        ]
        colors = ['#4CAF50', '#F44336', '#2196F3', '#FFC107', '#9C27B0']
        explode = (0.05, 0.05, 0, 0, 0)  # 特許査定と拒絶査定を少し強調
        
        # 0のエントリーを除外
        non_zero_sizes = []
        non_zero_labels = []
        non_zero_colors = []
        non_zero_explode = []
        
        for i, size in enumerate(sizes):
            if size > 0:
                non_zero_sizes.append(size)
                non_zero_labels.append(labels[i])
                non_zero_colors.append(colors[i])
                non_zero_explode.append(explode[i])
        
        # 円グラフ作成
        wedges, texts, autotexts = ax.pie(
            non_zero_sizes,
            explode=non_zero_explode,
            labels=None,
            autopct='%1.1f%%',
            startangle=90,
            colors=non_zero_colors,
            shadow=True
        )
        
        # 凡例の追加
        ax.legend(
            wedges,
            [f"{label} ({size}件)" for label, size in zip(non_zero_labels, non_zero_sizes)],
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        
        # タイトル設定
        title = f"{applicant_name} - " if applicant_name else ""
        ax.set_title(f'{title}特許査定状況の分布', fontsize=14)
        
        # アスペクト比を等しく設定
        ax.axis('equal')
        
        plt.tight_layout()
        
        # グラフを画像としてメモリに保存
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Base64エンコード
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    
    def generate_pdf_report(self, output_path, applicant_name=None, years=10, top_n=5):
        """
        特許分析レポートをPDFとして出力
        
        Args:
            output_path (str): 出力先PDFファイルのパス
            applicant_name (str, optional): 出願人名（指定がない場合は全体の分析を行う）
            years (int): 分析する年数
            top_n (int): 表示する上位分類数
            
        Returns:
            bool: 生成に成功したかどうか
        """
        try:
            # グラフ生成
            trend_chart = self.generate_classification_trend_chart(years, top_n)
            assessment_chart = self.generate_assessment_ratio_chart(applicant_name)
            
            # レポート作成
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # スタイル設定
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            heading1_style = styles['Heading1']
            heading2_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # 日本語対応のスタイルを追加
            jp_normal_style = ParagraphStyle(
                'jp_normal',
                parent=normal_style,
                fontName='HeiseiMin-W3',
                fontSize=10,
                leading=14
            )
            
            jp_heading1_style = ParagraphStyle(
                'jp_heading1',
                parent=heading1_style,
                fontName='HeiseiMin-W3',
                fontSize=16,
                leading=20
            )
            
            jp_heading2_style = ParagraphStyle(
                'jp_heading2',
                parent=heading2_style,
                fontName='HeiseiMin-W3',
                fontSize=14,
                leading=18
            )
            
            # コンテンツ作成
            content = []
            
            # タイトル
            title_text = "特許分析レポート"
            if applicant_name:
                title_text += f" - {applicant_name}"
            content.append(Paragraph(title_text, title_style))
            content.append(Spacer(1, 20))
            
            # 生成日
            content.append(Paragraph(f"生成日: {datetime.now().strftime('%Y年%m月%d日')}", jp_normal_style))
            content.append(Spacer(1, 20))
            
            # セクション1: 特許分類別の出願数推移
            content.append(Paragraph("1. 特許分類別の出願数推移", jp_heading1_style))
            content.append(Spacer(1, 10))
            content.append(Paragraph(f"過去{years}年間における上位{top_n}の特許分類別出願数の推移を示しています。", jp_normal_style))
            content.append(Spacer(1, 10))
            
            # トレンドグラフの埋め込み
            trend_img_data = base64.b64decode(trend_chart)
            trend_img = Image(io.BytesIO(trend_img_data))
            trend_img.drawHeight = 300
            trend_img.drawWidth = 450
            content.append(trend_img)
            content.append(Spacer(1, 20))
            
            # セクション2: 特許査定状況の分布
            content.append(Paragraph("2. 特許査定状況の分布", jp_heading1_style))
            content.append(Spacer(1, 10))
            content.append(Paragraph("特許査定、拒絶査定、その他の状況の分布を示しています。", jp_normal_style))
            content.append(Spacer(1, 10))
            
            # 査定比率グラフの埋め込み
            assessment_img_data = base64.b64decode(assessment_chart)
            assessment_img = Image(io.BytesIO(assessment_img_data))
            assessment_img.drawHeight = 300
            assessment_img.drawWidth = 450
            content.append(assessment_img)
            
            # PDFに書き込み
            doc.build(content)
            
            return True
        
        except Exception as e:
            print(f"PDFレポート生成エラー: {str(e)}")
            return False
    
    def generate_applicant_comparison_report(self, applicants, output_path):
        """
        複数の出願人の比較レポートを生成
        
        Args:
            applicants (list): 出願人名のリスト
            output_path (str): 出力先PDFファイルのパス
            
        Returns:
            bool: 生成に成功したかどうか
        """
        try:
            # PDFドキュメント作成
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # レポートに含めるコンテンツ
            content = []
            
            # スタイル設定
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            heading1_style = styles['Heading1']
            heading2_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # 日本語対応のスタイルを追加
            jp_normal_style = ParagraphStyle(
                'jp_normal',
                parent=normal_style,
                fontName='HeiseiMin-W3',
                fontSize=10,
                leading=14
            )
            
            jp_heading1_style = ParagraphStyle(
                'jp_heading1',
                parent=heading1_style,
                fontName='HeiseiMin-W3',
                fontSize=16,
                leading=20
            )
            
            jp_heading2_style = ParagraphStyle(
                'jp_heading2',
                parent=heading2_style,
                fontName='HeiseiMin-W3',
                fontSize=14,
                leading=18
            )
            
            # タイトル
            content.append(Paragraph("出願人比較レポート", title_style))
            content.append(Spacer(1, 20))
            
            # 生成日
            content.append(Paragraph(f"生成日: {datetime.now().strftime('%Y年%m月%d日')}", jp_normal_style))
            content.append(Spacer(1, 20))
            
            # 各出願人の査定状況グラフを生成
            for applicant in applicants:
                content.append(Paragraph(f"{applicant}の特許査定状況", jp_heading2_style))
                content.append(Spacer(1, 10))
                
                assessment_chart = self.generate_assessment_ratio_chart(applicant)
                
                assessment_img_data = base64.b64decode(assessment_chart)
                assessment_img = Image(io.BytesIO(assessment_img_data))
                assessment_img.drawHeight = 250
                assessment_img.drawWidth = 400
                content.append(assessment_img)
                content.append(Spacer(1, 20))
            
            # 出願人比較セクション
            from .applicant_analyzer import ApplicantAnalyzer
            app_analyzer = ApplicantAnalyzer()
            
            if len(applicants) > 1:
                content.append(Paragraph("出願人間の比較", jp_heading1_style))
                content.append(Spacer(1, 10))
                
                # 比較データ取得
                comparison_data = app_analyzer.compare_with_competitors(applicants[0], len(applicants) - 1)
                
                if "assessment_comparison" in comparison_data:
                    # 査定比較グラフ
                    assessment_comp_data = base64.b64decode(comparison_data["assessment_comparison"])
                    assessment_comp_img = Image(io.BytesIO(assessment_comp_data))
                    assessment_comp_img.drawHeight = 300
                    assessment_comp_img.drawWidth = 450
                    content.append(assessment_comp_img)
                    content.append(Spacer(1, 20))
                
                if "field_comparison" in comparison_data:
                    # 技術分野比較グラフ
                    field_comp_data = base64.b64decode(comparison_data["field_comparison"])
                    field_comp_img = Image(io.BytesIO(field_comp_data))
                    field_comp_img.drawHeight = 300
                    field_comp_img.drawWidth = 450
                    content.append(field_comp_img)
            
            # PDFに書き込み
            doc.build(content)
            
            return True
        
        except Exception as e:
            print(f"出願人比較レポート生成エラー: {str(e)}")
            return False
