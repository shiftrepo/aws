# Classification Analysis API Documentation

## Overview

The Classification Analysis API is designed to provide detailed patent classification trend analysis based on data from the patent database. The `/analyze_classification` endpoint allows users to retrieve top applicants and trend analysis for a specific IPC classification code over a specified period.

## API Endpoints

### POST /analyze_classification

Analyze patent trends by applicant and year for a given classification code.

**Request Format:**
```json
{
  "classification_code": "G",
  "start_year": 2010,
  "end_year": 2023
}
```

**Parameters:**
- `classification_code`: IPC classification code (e.g., 'G' for Physics)
- `start_year`: Optional starting year for analysis
- `end_year`: Optional ending year for analysis

**Response Format:**
```json
{
  "classification_code": "G",
  "yearly_applicant_counts": {
    "2018": {
      "ジーイー－ヒタチ・ニュークリア・エナジー・アメリカズ・エルエルシー": 1,
      "クアルコム，インコーポレイテッド": 1
    },
    "2019": {
      "株式会社堀場エステック": 1,
      "株式会社オトングラス": 1,
      "小林製薬株式会社": 1,
      "レッコ インベスト アーベー": 1,
      "メモリアル スローン ケタリング キャンサー センター; エウレカ セラピューティクス，インコーポレイテッド": 1
    },
    "2020": {
      "キヤノン株式会社": 8,
      "株式会社リコー": 6,
      "マイクロソフト テクノロジー ライセンシング，エルエルシー": 3,
      "ブラザー工業株式会社": 3,
      "株式会社半導体エネルギー研究所": 2
    },
    "2021": {
      "キヤノン株式会社": 15,
      "インターナショナル・ビジネス・マシーンズ・コーポレーション": 15,
      "トヨタ自動車株式会社": 14,
      "日本電気株式会社": 12,
      "セイコーエプソン株式会社": 7
    },
    "2022": {
      "トヨタ自動車株式会社": 6,
      "株式会社日立ハイテク": 3,
      "株式会社デンソー": 3,
      "本田技研工業株式会社": 3,
      "テンセント・アメリカ・エルエルシー": 3
    },
    "2023": {
      "キヤノン株式会社": 10,
      "トヨタ自動車株式会社": 8,
      "京セラドキュメントソリューションズ株式会社": 7,
      "日本電気株式会社": 5,
      "三菱電機株式会社": 5
    }
  },
  "assessment": "Assessment for IPC Class G (Physics):\n\n1. Overall Trend: Patent applications in Class G are increasing from 2018 (2 applications) to 2023 (35 applications), which represents a 1650.0% increase.\n\n2. Top Applicants in this Classification:\n   - キヤノン株式会社: 33 applications (23.4%)\n   - トヨタ自動車株式会社: 28 applications (19.9%)\n   - インターナショナル・ビジネス・マシーンズ・コーポレーション: 15 applications (10.6%)\n   - 日本電気株式会社: 17 applications (12.1%)\n   - セイコーエプソン株式会社: 7 applications (5.0%)\n\n3. Peak Activity: The highest number of patent applications (63) was in 2021.\n\n4. Market Dynamics: The G classification field is led by one major applicant with significant competition.\n\n5. Recent Activity: Patent applications in the most recent years show a fluctuating trend."
}
```

## Implementation Details

The API is implemented using FastAPI and connects to the patent database via the database API (http://localhost:5003). The workflow is as follows:

1. Receive the classification analysis request with classification code and year range
2. Query the database for patent applications matching the criteria
3. Process the results to calculate yearly totals and identify top applicants
4. Generate a comprehensive assessment of the classification field
5. Return the structured response with yearly data and assessment

## Database Query

The core of the implementation involves querying the database for patent applications:

```sql
SELECT 
    substr(filing_date, 1, 4) as year,
    assignee_original as applicant_name,
    COUNT(*) as application_count
FROM 
    publications
WHERE 
    substr(ipc_code, 1, 1) = 'G'
    AND substr(filing_date, 1, 4) >= '2010'
    AND substr(filing_date, 1, 4) <= '2023'
GROUP BY 
    substr(filing_date, 1, 4), 
    assignee_original
ORDER BY 
    substr(filing_date, 1, 4), 
    COUNT(*) DESC
```

## Assessment Generation

The assessment includes:
1. Overall trend analysis (increasing/decreasing)
2. Top applicants with percentage of market share
3. Year with peak activity
4. Market dynamics evaluation (competition level)
5. Recent activity trend

## Usage Example

Using curl to make an API request:

```bash
curl -X POST http://localhost:5006/analyze_classification \
  -H "Content-Type: application/json" \
  -d '{
    "classification_code": "G",
    "start_year": 2010,
    "end_year": 2023
  }'
```

## Integration Notes

To integrate this API with other systems:
1. Ensure the database service is running (http://localhost:5003)
2. Send HTTP POST requests to the /analyze_classification endpoint
3. Process the returned JSON data with yearly counts and assessment
