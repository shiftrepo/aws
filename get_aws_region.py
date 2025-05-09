#!/usr/bin/env python3
import os
import subprocess
import json

# AWS リージョンを環境変数から取得
aws_region = os.environ.get('AWS_DEFAULT_REGION')

if aws_region:
    print(f"AWS Region from environment variable: {aws_region}")
else:
    print("AWS_DEFAULT_REGION environment variable is not set")
    
    # 環境変数が設定されていない場合、AWS設定ファイルから取得を試みる
    aws_config_path = os.path.expanduser('~/.aws/config')
    aws_credentials_path = os.path.expanduser('~/.aws/credentials')
    
    # AWS Config ファイルの確認
    try:
        if os.path.exists(aws_config_path):
            print("\nAWS Config file exists at:", aws_config_path)
            with open(aws_config_path, 'r') as f:
                print("AWS Config file content:")
                print(f.read())
        else:
            print("\nAWS Config file not found at:", aws_config_path)
            
        # AWS CLIのデフォルト設定を確認
        try:
            result = subprocess.run(['aws', 'configure', 'get', 'region'], 
                                   capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                print(f"\nAWS CLI default region: {result.stdout.strip()}")
            else:
                print("\nCould not get AWS CLI default region")
        except FileNotFoundError:
            print("\nAWS CLI not installed or not in PATH")
        except Exception as e:
            print(f"\nError executing AWS CLI: {str(e)}")
            
    except Exception as e:
        print(f"\nError checking AWS configuration: {str(e)}")
