#!/usr/bin/env python3
"""
Document processing script using Docling
Usage: python process_documents.py [input_file] [output_format]
"""

import os
import sys
import json
from pathlib import Path
from docling.document_converter import DocumentConverter

def process_document(input_path, output_format="markdown"):
    """
    ドキュメントを処理してMarkdownまたは他の形式に変換

    Args:
        input_path (str): 入力ファイルのパス
        output_format (str): 出力形式 (markdown, json, text)
    """

    # 入力ファイルの確認
    if not os.path.exists(input_path):
        print(f"エラー: 入力ファイルが見つかりません: {input_path}")
        return False

    # Doclingコンバーターの初期化
    converter = DocumentConverter()

    try:
        # ドキュメントの変換
        print(f"処理中: {input_path}")
        result = converter.convert(input_path)

        # 出力ファイルパスの生成
        input_file = Path(input_path)
        output_dir = Path("/shared/output")
        output_dir.mkdir(exist_ok=True)

        if output_format.lower() == "markdown":
            output_file = output_dir / f"{input_file.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.document.export_to_markdown())

        elif output_format.lower() == "json":
            output_file = output_dir / f"{input_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result.document.export_to_dict(), f,
                         ensure_ascii=False, indent=2)

        elif output_format.lower() == "text":
            output_file = output_dir / f"{input_file.stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.document.export_to_text())

        else:
            print(f"サポートされていない出力形式: {output_format}")
            return False

        print(f"変換完了: {output_file}")
        return True

    except Exception as e:
        print(f"変換エラー: {str(e)}")
        return False

def process_directory(input_dir, output_format="markdown"):
    """
    ディレクトリ内のすべてのファイルを処理
    """
    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"エラー: ディレクトリが見つかりません: {input_dir}")
        return

    supported_extensions = {'.pdf', '.docx', '.pptx', '.html', '.txt', '.md'}

    for file_path in input_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            process_document(str(file_path), output_format)

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python process_documents.py <input_file_or_dir> [output_format]")
        print("  output_format: markdown (デフォルト), json, text")
        print("")
        print("例:")
        print("  python process_documents.py /shared/input/document.pdf")
        print("  python process_documents.py /shared/input/ json")
        return

    input_path = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "markdown"

    # 入力パスが相対パスの場合、/shared/input/を基準にする
    if not os.path.isabs(input_path):
        input_path = os.path.join("/shared/input", input_path)

    if os.path.isdir(input_path):
        process_directory(input_path, output_format)
    else:
        process_document(input_path, output_format)

if __name__ == "__main__":
    main()