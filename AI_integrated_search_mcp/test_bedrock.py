#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock client configuration.
"""

import os
import json
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info("Testing AWS Bedrock client configuration")
    
    # Print boto3 version
    logger.info(f"boto3 version: {boto3.__version__}")
    
    # Get AWS region from environment
    region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
    if not region:
        logger.error("AWS region not found in environment variables")
        return False
    
    logger.info(f"Using AWS region: {region}")
    
    # Create Bedrock client
    try:
        bedrock = boto3.client('bedrock-runtime', region_name=region)
        logger.info("Bedrock client initialized successfully")
        
        # For Claude 3.7 Sonnet which may require specific region
        model_id = os.environ.get("BEDROCK_LLM_MODEL", "amazon.titan-text-lite-v1")
        if "claude-3-7" in model_id or "us.anthropic" in model_id:
            claude_region = "us-west-2"  # Claude 3.7 Sonnet is available in this region
            if region != claude_region:
                logger.info(f"Creating cross-region client for Claude 3.7 in {claude_region}")
                cross_region_bedrock = boto3.client('bedrock-runtime', region_name=claude_region)
                # Use the cross-region client for Claude models
                bedrock = cross_region_bedrock
                logger.info("Cross-region Bedrock client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock client: {str(e)}")
        return False
    
    # Get specified model ID from environment or use default
    model_id = os.environ.get("BEDROCK_LLM_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")
    logger.info(f"Using model ID: {model_id}")
    
    # Get list of available models to check access
    try:
        # First try to list models using the bedrock service (not bedrock-runtime)
        bedrock_mgmt = boto3.client('bedrock', region_name=region)
        response = bedrock_mgmt.list_foundation_models()
        model_ids = [model.get("modelId") for model in response.get("modelSummaries", [])]
        logger.info(f"Available models: {model_ids}")
        
        if model_id in model_ids:
            logger.info(f"Model {model_id} is available")
        else:
            logger.warning(f"Model {model_id} was not found in available models")
            
    except Exception as e:
        logger.warning(f"Could not list models: {str(e)}")
    
    # Test a simple completion
    try:
        logger.info("Testing model invocation...")
        
        # Prepare a simple test prompt
        # Format depends on the model
        model_id = os.environ.get("BEDROCK_LLM_MODEL", "amazon.titan-text-express-v1")
        
        if "anthropic" in model_id:
            # Claude format
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": "Say hello and identify yourself in one sentence."
                    }
                ]
            }
        elif "amazon.titan" in model_id:
            # Titan format
            body = {
                "inputText": "Say hello and identify yourself in one sentence.",
                "textGenerationConfig": {
                    "maxTokenCount": 100,
                    "temperature": 0,
                    "topP": 1
                }
            }
        else:
            # Generic fallback
            body = {
                "prompt": "Say hello and identify yourself in one sentence.",
                "max_tokens": 100,
                "temperature": 0
            }
        
        body_json = json.dumps(body)
        
        # Send request to Bedrock
        response = bedrock.invoke_model(
            modelId=model_id,
            body=body_json
        )
        
        # Parse response
        response_body = json.loads(response.get('body').read())
        
        # Extract and print generated text based on model type
        if "anthropic" in model_id:
            if "content" in response_body and len(response_body["content"]) > 0:
                generated_text = response_body["content"][0]["text"]
                logger.info(f"Response from Claude model: {generated_text}")
                logger.info("Model invocation successful!")
                return True
        elif "amazon.titan" in model_id:
            if "results" in response_body and len(response_body["results"]) > 0:
                generated_text = response_body["results"][0]["outputText"]
                logger.info(f"Response from Titan model: {generated_text}")
                logger.info("Model invocation successful!")
                return True
        else:
            # Generic response extraction attempt
            if "completion" in response_body:
                generated_text = response_body["completion"]
                logger.info(f"Response from model: {generated_text}")
                logger.info("Model invocation successful!")
                return True
            elif "generated_text" in response_body:
                generated_text = response_body["generated_text"]
                logger.info(f"Response from model: {generated_text}")
                logger.info("Model invocation successful!")
                return True
                
        # If we got here, we couldn't extract the response
        logger.error(f"Unexpected response format: {response_body}")
        return False
            
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        error_message = e.response.get("Error", {}).get("Message")
        logger.error(f"Error invoking model: {error_code} - {error_message}")
        
        if error_code == "AccessDeniedException":
            logger.error("You don't have access to the specified model. Check your AWS permissions and model subscription.")
            logger.error("Suggested actions:")
            logger.error("1. Verify your AWS credentials have the correct permissions")
            logger.error("2. Verify you have subscribed to the model in AWS Marketplace")
            logger.error("3. Use a different model that's available to you")
            logger.error("4. Update BEDROCK_LLM_MODEL in the .env file to a model you have access to")
        return False
    except Exception as e:
        logger.error(f"Error testing model: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    print("Test " + ("succeeded" if success else "failed"))
    exit(0 if success else 1)
