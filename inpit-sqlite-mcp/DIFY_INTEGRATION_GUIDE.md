# Dify 統合ガイド：Inpit SQLite MCP サーバー

このガイドでは、Difyでinpit-sqlite MCPサーバーを使用して、Claudeに特許データベースへのアクセス機能を提供する方法を説明します。

## 前提条件

- Difyをインストール済み（セルフホストまたはクラウドアカウント）
- Claude APIキー（Anthropicのアカウントが必要）
- inpit-sqlite MCPサーバーのセットアップ完了

## セットアップ手順

### 1. MCPサーバーのセットアップ

1. このリポジトリのセットアップ手順に従って、inpit-sqlite MCPサーバーを設定および起動します:

```bash
# Inpit SQLiteサービスが実行されていることを確認
cd inpit-sqlite-mcp
./start_server.sh
```

または、Docker Composeを使用する場合:

```bash
cd inpit-sqlite-mcp
export AWS_ACCESS_KEY_ID=あなたのアクセスキー
export AWS_SECRET_ACCESS_KEY=あなたのシークレットキー
docker-compose up -d
```

2. MCPサーバーが http://localhost:8000 で実行されていることを確認します:

```bash
curl http://localhost:8000
```

レスポンス例:
```json
{
  "status": "ok", 
  "message": "Inpit SQLite MCP Server is running",
  "service": "Inpit SQLite Database API"
}
```

### 2. Difyの設定

#### 2.1 新しいアプリケーションの作成

1. Difyダッシュボードにログインします
2. 「新規アプリケーション作成」ボタンをクリックします
3. アプリ名（例：「特許検索アシスタント」）と説明を入力します
4. アプリタイプとして「チャット」を選択します
5. 「作成」をクリックします

#### 2.2 モデル設定

1. 新しく作成したアプリケーションの設定ページに移動します
2. 「モデル」タブをクリックします
3. モデルプロバイダーとして「Claude (Anthropic)」を選択します
4. API設定で、AnthropicのAPIキーを入力します
5. モデルとして「Claude 3 Opus」または「Claude 3 Sonnet」を選択します（ほとんどの場合、Sonnetで十分です）
6. 必要に応じてコンテキスト長やその他のパラメータを調整します

#### 2.3 MCP設定

1. 「MCP統合」セクションに移動します
2. 「MCPサーバーを追加」ボタンをクリックします
3. 以下の情報を入力します:
   - サーバー名: `inpit-sqlite`
   - サーバーURL: `http://localhost:8000`（または実際のMCPサーバーのURL）
   - 有効化: チェックを入れる
4. 「保存」をクリックして設定を適用します

#### 2.4 プロンプト設定

Difyの「プロンプト」セクションで、以下のようなシステムプロンプトを設定します:

```
あなたは特許情報アシスタントです。inpit-sqlite MCPサーバーを使用して特許データベースにアクセスし、
ユーザーからの質問に答えます。

あなたの主な機能は:
1. 出願番号による特許検索
2. 出願人名による特許検索 
3. SQLクエリによる高度な分析

ユーザーからの質問に応じて、適切なMCPツールを使用してデータを取得し、
わかりやすく整理された形で情報を提示してください。

専門的な用語が使われていても、一般の人にもわかりやすい言葉で説明するよう努めてください。
SQLクエリを実行する場合は、常にクエリの内容と目的を説明してから結果を表示してください。
```

#### 2.5 アプリの公開

設定が完了したら、「公開」ボタンをクリックしてアプリケーションを公開します。

### 3. テストと利用

#### 3.1 Webインターフェースでのテスト

1. 公開されたアプリケーションのWebインターフェースにアクセスします
2. 以下のような質問でテストします:
   - 「テック株式会社の特許情報を教えてください」
   - 「出願番号2022-123456の詳細を表示して」
   - 「出願人別の特許出願数上位10社を教えてください」

#### 3.2 API経由での利用

Difyの「API」セクションからAPIキーを取得し、以下のようなリクエストでテストできます:

```bash
curl -X POST https://your-dify-instance/api/chat-messages \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -d '{
        "query": "テック株式会社の特許情報を教えてください",
        "conversation_id": "default-conversation",
        "user": "user-001",
        "inputs": {}
     }'
```

## トラブルシューティング

### MCPサーバー接続エラー

Claude/Difyからのレスポンスに「MCPサーバーに接続できません」というエラーが表示される場合:

1. MCPサーバーが実行されていることを確認します:
   ```bash
   curl http://localhost:8000
   ```

2. Difyサーバーからこのエラーが発生している場合、MCPサーバーのURLがDifyサーバーからアクセス可能であることを確認します。
   - Docker環境で実行している場合、適切なネットワーク設定が必要かもしれません
   - クラウド環境の場合、ファイアウォール設定を確認してください

### データベースアクセスエラー

「データベースに接続できません」というエラーが表示される場合:

1. Inpit SQLiteサービスが実行されていることを確認します:
   ```bash
   curl http://localhost:5001/api/status
   ```

2. MCPサーバーが正しいURLでInpit SQLiteサービスにアクセスしていることを確認します:
   ```bash
   INPIT_API_URL=http://localhost:5001  # 必要に応じて変更
   ```

### その他の問題

その他の問題については、ログファイルを確認してください:

- MCPサーバーのログ: `/tmp/inpit-sqlite-mcp.log`
- Dockerログ（Docker使用時）: `docker-compose logs`

## 高度な設定

### カスタムプロンプトの例

特許分析に特化したプロンプト例:

```
あなたは特許情報アナリストです。特許データベースにアクセスして、技術トレンド分析や
出願人の戦略分析などの高度な分析を提供します。

以下の分析を行うことができます:
1. 出願人のポートフォリオ分析
2. 技術分野別の出願傾向
3. 時系列での出願活動分析
4. 競合他社との比較分析

分析結果は、できるだけ以下のような構造で提示してください:
- 要約: 主な発見・傾向の簡潔なまとめ
- データ分析: SQLクエリの結果と統計的解釈
- 洞察: データから読み取れるビジネス/技術的示唆
- 提案: 追加の分析方向や調査すべきポイント

質問の趣旨が不明確な場合は、分析の目的や具体的に知りたい情報について確認してください。
```

### Dify APIをプログラムから利用する例

Node.js での利用例:

```javascript
const axios = require('axios');

async function queryPatentAssistant(question) {
  try {
    const response = await axios.post('https://your-dify-instance/api/chat-messages', {
      query: question,
      conversation_id: "patent-analysis-session",
      user: "analyst-001",
      inputs: {}
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error querying patent assistant:', error);
    return null;
  }
}

// 使用例
async function main() {
  const result = await queryPatentAssistant("AI関連特許の出願数上位10社を分析してください");
  console.log(result.answer);
}

main();
```

Python での利用例:

```python
import requests

def query_patent_assistant(question):
    url = "https://your-dify-instance/api/chat-messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"
    }
    data = {
        "query": question,
        "conversation_id": "patent-analysis-session",
        "user": "analyst-001",
        "inputs": {}
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying patent assistant: {e}")
        return None

# 使用例
if __name__ == "__main__":
    result = query_patent_assistant("AI関連特許の出願数上位10社を分析してください")
    if result and "answer" in result:
        print(result["answer"])
