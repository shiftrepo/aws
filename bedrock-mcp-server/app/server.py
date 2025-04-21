import os
import json
import boto3
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Bedrock MCP Server")

# Bedrockクライアントの初期化
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
)

class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9

@app.get("/")
async def root():
    return {"status": "ok", "message": "Bedrock MCP Server is running"}

@app.post("/inference")
async def generate_inference(request: InferenceRequest):
    try:
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-v2')
        
        # リクエストペイロードの構築（モデルによって異なる形式）
        if "claude" in model_id:
            body = json.dumps({
                "prompt": f"\n\nHuman: {request.prompt}\n\nAssistant:",
                "max_tokens_to_sample": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p
            })
        elif "amazon.titan" in model_id:
            body = json.dumps({
                "inputText": request.prompt,
                "textGenerationConfig": {
                    "maxTokenCount": request.max_tokens,
                    "temperature": request.temperature,
                    "topP": request.top_p
                }
            })
        elif "meta.llama" in model_id:
            body = json.dumps({
                "prompt": request.prompt,
                "max_gen_len": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p
            })
        else:
            # その他のモデル用の汎用フォーマット
            body = json.dumps({
                "prompt": request.prompt,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p
            })

        # 推論リクエスト送信
        # 注: パフォーマンス設定が必要な場合は performanceConfigLatency パラメータを使用
        # performanceConfigLatency オプションの例: "low-latency", "balanced", "high"
        if os.environ.get('BEDROCK_PERFORMANCE_CONFIG'):
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body,
                performanceConfigLatency=os.environ.get('BEDROCK_PERFORMANCE_CONFIG')
            )
        else:
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body
            )
        
        # レスポンスの解析（モデルによって異なる）
        response_body = json.loads(response.get('body').read())
        
        if "claude" in model_id:
            generated_text = response_body.get('completion')
        elif "amazon.titan" in model_id:
            generated_text = response_body.get('results', [{}])[0].get('outputText', '')
        elif "meta.llama" in model_id:
            generated_text = response_body.get('generation', '')
        else:
            # その他のモデル用の汎用レスポンス解析
            generated_text = response_body.get('generated_text', 
                            response_body.get('text', 
                            response_body.get('output', '')))
            
        return {
            "generated_text": generated_text,
            "model_id": model_id,
            "performance_config": os.environ.get('BEDROCK_PERFORMANCE_CONFIG', 'default')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating inference: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)