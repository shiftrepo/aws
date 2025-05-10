# patentDWH AWS Credentials Fix

## 問題の概要 / Problem Summary

patentDWH の自然言語クエリ機能が AWS Bedrock 認証エラーにより動作していませんでした。具体的には、以下のエラーが発生していました。

The Natural Language Query functionality in patentDWH was not working due to AWS Bedrock authentication errors. Specifically, the following error occurred:

```
[2025-05-10 09:38:49] [uvicorn] 2025-05-10 09:38:49,462 - ERROR - Error generating SQL: An error occurred (UnrecognizedClientException) when calling the InvokeModel operation: The security token included in the request is invalid.
```

## 根本原因 / Root Cause

1. AWS Bedrock サービス（Claude 3 Haiku モデルと Titan Embedding モデル）へのアクセスに必要な AWS 認証情報が設定されていませんでした。
2. 環境変数 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` が欠落していました。
3. 認証情報の不足が検出されたとき、明確なエラーメッセージが表示されず、単にリクエストが失敗するだけでした。

1. AWS credentials required for accessing AWS Bedrock services (Claude 3 Haiku model and Titan Embedding model) were not configured.
2. The environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` were missing.
3. When authentication credentials were missing, there was no clear error message, just a failed request.

## 実装された修正 / Implemented Fix

以下のような改善を施しました：

The following improvements were implemented:

### 1. 強化された認証情報チェック / Enhanced Credential Checking

- `nl_query_processor.py` に明示的な AWS 認証情報チェックを追加
- AWS 認証情報の検証ロジックを強化
- 認証情報がない場合の明確なエラーメッセージを追加

- Added explicit AWS credential checking to `nl_query_processor.py`
- Improved validation logic for AWS credentials
- Added clear error messages when credentials are missing

### 2. AWS 認証情報ステータス API / AWS Credentials Status API

- `/api/aws-status` エンドポイントを追加し、AWS 認証情報の状態を確認可能に
- ヘルスチェックエンドポイントに AWS 認証情報の状態を含めるように更新

- Added an `/api/aws-status` endpoint to check the status of AWS credentials
- Updated the health check endpoint to include AWS credential status

### 3. 優雅な障害処理 / Graceful Failure Handling

- AWS 認証情報がない場合でもアプリケーション全体がクラッシュしないように
- 自然言語クエリ以外の機能は引き続き正常に動作
- 詳細なエラーメッセージで問題の診断を簡素化

- Ensured the application doesn't crash when AWS credentials are missing
- Other functionalities continue to work even if natural language queries don't
- Detailed error messages to simplify problem diagnosis

## ファイルの変更 / Modified Files

以下のファイルが変更されました：

The following files were modified:

1. `patentDWH/app/nl_query_processor.py` → `patched_nl_query_processor.py`
2. `patentDWH/app/server.py` → `patched_server.py`

また、実装のためのスクリプトが作成されました：

An implementation script was also created:

- `patentDWH/apply_aws_credentials_fix.sh`

## 使用方法 / Usage

AWS 認証情報を設定するには、以下の手順に従ってください：

To set up AWS credentials, follow these steps:

### 1. AWS 認証情報の設定 / Set AWS Credentials

```bash
# AWS認証情報を環境変数として設定
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

または、AWS 認証情報ファイルを設定します：

Or configure AWS credentials file:

```bash
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
EOF

cat > ~/.aws/config << EOF
[default]
region = us-east-1
output = json
EOF
```

### 2. 修正スクリプトの実行 / Run the Fix Script

```bash
cd patentDWH
./apply_aws_credentials_fix.sh
```

### 3. AWS 認証情報の状態確認 / Check AWS Credentials Status

```bash
curl http://localhost:8080/api/aws-status
```

## トラブルシューティング / Troubleshooting

AWS 認証情報が設定されていない、または無効な場合、自然言語クエリは以下のようなエラーを返します：

If AWS credentials are not set or are invalid, natural language queries will return an error like this:

```json
{
  "success": false,
  "error": "AWS Bedrock設定エラー: AWS認証情報が設定されていないか無効です。AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、AWS_REGIONが適切に設定されていることを確認してください。"
}
```

このエラーが表示される場合は、以下を確認してください：

If you see this error, check the following:

1. 環境変数 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` が設定されているか
2. 認証情報が AWS Bedrock にアクセスする権限を持っているか
3. 指定されたリージョンで AWS Bedrock サービスが利用可能か

1. Whether the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` are set
2. Whether the credentials have permission to access AWS Bedrock
3. Whether AWS Bedrock services are available in the specified region

## AWS Bedrock アクセス権限 / AWS Bedrock Access Permissions

AWS Bedrock サービスにアクセスするには、IAM ユーザーまたはロールに以下の権限が必要です：

To access AWS Bedrock services, your IAM user or role needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:model/anthropic.claude-3-haiku-20240307-v1:0",
        "arn:aws:bedrock:*:*:model/amazon.titan-embed-text-v2:0"
      ]
    }
  ]
}
