import re

class JapaneseToEnglish:
    @staticmethod
    def convert(text):
        """Convert Japanese text to English using romaji and common translations"""
        # Common Japanese terms with English translations
        mapping = {
            '株式会社': 'Corporation',
            'テクノロジー': 'Technology',
            'サイエンス': 'Science',
            'エレクトロニクス': 'Electronics',
            'システム': 'Systems',
            'デバイス': 'Devices',
            '研究所': 'Laboratory',
            'グループ': 'Group',
            '製作所': 'Works',
            '電機': 'Electric',
            '電子': 'Electronics',
            '開発': 'Development',
            '特許': 'Patent',
            '出願': 'Application',
            '分析': 'Analysis',
            '技術': 'Technical',
            '年': 'Year',
            '件数': 'Count',
            '合計': 'Total',
            'テック': 'Tech',
            '情報': 'Information',
            '通信': 'Communications',
            '半導体': 'Semiconductor',
            'ソフトウェア': 'Software',
            'ハードウェア': 'Hardware',
            '機械': 'Machine',
            '自動車': 'Automobile',
            '化学': 'Chemical',
            '製薬': 'Pharmaceutical',
            '医療': 'Medical',
            '建設': 'Construction',
            '金属': 'Metal',
            '材料': 'Materials',
            'エネルギー': 'Energy',
            'バイオ': 'Bio',
            '環境': 'Environment',
        }
        
        result = text
        for ja, en in mapping.items():
            result = result.replace(ja, en)
        
        # Convert any remaining Japanese characters to romaji-like placeholder
        # In a production system you'd use a proper Japanese romanization library
        result = re.sub(r'[^\x00-\x7F]+', lambda m: 'X'*len(m.group()), result)
        
        return result

# Create an instance for easy import
japanese_to_english = JapaneseToEnglish()

if __name__ == "__main__":
    # Test the conversion
    test_text = "テック株式会社の特許出願分析"
    converted = japanese_to_english.convert(test_text)
    print(f"Original: {test_text}")
    print(f"Converted: {converted}")
