# SQLクエリHTTPリクエスト例

以下は`AI_integrated_search_mcp`の`/execute/{db_name}`エンドポイントを使用して、提示されたSQLクエリを実行するHTTPリクエストの例です。

## cURLを使用する場合

```bash
curl -X POST http://localhost:5003/execute/inpit \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT 技術分野1 AS セクション, COUNT(*) AS 出願数 FROM inpit_data WHERE 出願人 LIKE '\''%トヨタ%'\'' GROUP BY 技術分野1 ORDER BY 出願数 DESC;"
  }'
```

## JavaScriptのfetchを使用する場合

```javascript
const query = `SELECT 技術分野1 AS セクション, COUNT(*) AS 出願数
FROM inpit_data
WHERE 出願人 LIKE '%トヨタ%'
GROUP BY 技術分野1
ORDER BY 出願数 DESC;`;

fetch('http://localhost:5003/execute/inpit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ query: query })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## Pythonのrequestsを使用する場合

```python
import requests
import json

query = """
SELECT 技術分野1 AS セクション, COUNT(*) AS 出願数
FROM inpit_data
WHERE 出願人 LIKE '%トヨタ%'
GROUP BY 技術分野1
ORDER BY 出願数 DESC;
"""

url = "http://localhost:5003/execute/inpit"
headers = {"Content-Type": "application/json"}
data = {"query": query}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

## サービス実行の前提条件

リクエストを実行する前に、`AI_integrated_search_mcp`サービスが起動していることを確認してください：

```bash
cd AI_integrated_search_mcp
source ~/.aws/source.aws  # AWS認証情報の読み込み
./scripts/start_services.sh
```

## レスポンス形式

成功すると、以下のようなJSON形式のレスポンスが返されます：

```json
{
  "columns": ["セクション", "出願数"],
  "rows": [
    ["電子通信", 1240],
    ["車両システム", 982],
    ["材料技術", 756],
    ...
  ],
  "execution_time": 0.156
}
```

## 注意事項

- データベースサービスは`http://localhost:5003`で実行されていることを前提としています
- SQLクエリは正しい構文で記述する必要があります
- 認証が必要な場合は、ヘッダーに認証情報を追加してください
