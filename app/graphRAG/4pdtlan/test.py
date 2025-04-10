import boto3
import json

# --- Bedrock クライアントのセットアップ ---
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

# --- 推論プロファイル ARN ---
inference_profile_arn = "arn:aws:bedrock:us-east-1:711387140677:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0"

# --- 修正されたペイロード ---
payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 256,
    "messages": [
        {"role": "user", "content": "こんにちは、モデルに質問します。"}
    ]
}

# --- モデルの呼び出し ---
try:
    print("モデルを呼び出しています...")
    response = bedrock_runtime.invoke_model(
        modelId=inference_profile_arn,
        body=json.dumps(payload),
        contentType="application/json"
    )
    
    # StreamingBodyを文字列に変換
    response_body = response["body"].read().decode("utf-8")
    
    # JSONとして解析
    result = json.loads(response_body)
    print("モデルの応答:", result)

except Exception as e:
    print("エラーが発生しました:", e)

