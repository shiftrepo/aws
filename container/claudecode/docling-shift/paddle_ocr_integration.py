#!/usr/bin/env python3
"""
PaddleOCR Integration with Docling
Docling用PaddleOCR統合スクリプト

このスクリプトは、PaddleOCRをDoclingと統合して、
より高精度なOCR処理を提供します。
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from PIL import Image
import logging

try:
    from paddleocr import PaddleOCR
except ImportError:
    print("Error: PaddleOCR is not installed. Please install it using: pip install paddleocr")
    sys.exit(1)

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import ConversionResult
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
except ImportError:
    print("Error: Docling is not installed. Please install docling and related packages.")
    sys.exit(1)

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaddleOCRDoclingIntegration:
    """PaddleOCRとDoclingの統合クラス"""

    def __init__(self,
                 use_angle_cls=True,
                 lang='en',
                 use_gpu=False,
                 show_log=False):
        """
        初期化

        Args:
            use_angle_cls: 角度分類を使用するか
            lang: OCR言語 ('en', 'ch', 'japan', etc.)
            use_gpu: GPU使用フラグ
            show_log: ログ表示フラグ
        """
        self.ocr = PaddleOCR(
            use_angle_cls=use_angle_cls,
            lang=lang,
            use_gpu=use_gpu,
            show_log=show_log
        )
        self.converter = DocumentConverter()
        logger.info(f"PaddleOCR initialized with language: {lang}, GPU: {use_gpu}")

    def extract_text_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        画像からテキストを抽出

        Args:
            image_path: 画像ファイルのパス

        Returns:
            OCR結果のリスト
        """
        try:
            result = self.ocr.ocr(image_path, cls=True)
            ocr_results = []

            if result and result[0]:
                for line in result[0]:
                    if line:
                        bbox = line[0]  # バウンディングボックス
                        text_info = line[1]  # テキスト情報
                        text = text_info[0]  # テキスト内容
                        confidence = text_info[1]  # 信頼度

                        ocr_results.append({
                            'text': text,
                            'confidence': confidence,
                            'bbox': bbox,
                            'coordinates': {
                                'x1': bbox[0][0], 'y1': bbox[0][1],
                                'x2': bbox[2][0], 'y2': bbox[2][1]
                            }
                        })

            logger.info(f"Extracted {len(ocr_results)} text blocks from {image_path}")
            return ocr_results

        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {str(e)}")
            return []

    def process_pdf_with_paddle_ocr(self, pdf_path: str, output_format: str = 'markdown') -> Dict[str, Any]:
        """
        PDFをPaddleOCRとDoclingで処理

        Args:
            pdf_path: PDFファイルのパス
            output_format: 出力形式 ('markdown', 'json', 'text')

        Returns:
            処理結果
        """
        try:
            # まずDoclingで基本的な変換を実行
            logger.info(f"Processing PDF with Docling: {pdf_path}")
            docling_result = self.converter.convert_single(pdf_path)

            # PDFを画像に変換してPaddleOCRで処理
            logger.info("Converting PDF pages to images for PaddleOCR processing")
            pdf_images = self._pdf_to_images(pdf_path)

            paddle_ocr_results = []
            for i, image in enumerate(pdf_images):
                logger.info(f"Processing page {i+1} with PaddleOCR")
                page_result = self.extract_text_from_image(image)
                paddle_ocr_results.append({
                    'page': i + 1,
                    'ocr_results': page_result
                })

            # 結果を統合
            integrated_result = {
                'docling_result': {
                    'markdown': docling_result.render_as_markdown() if output_format == 'markdown' else None,
                    'json': docling_result.render_as_json() if output_format == 'json' else None,
                    'text': docling_result.render_as_text() if output_format == 'text' else None,
                },
                'paddle_ocr_results': paddle_ocr_results,
                'metadata': {
                    'source_file': pdf_path,
                    'total_pages': len(paddle_ocr_results),
                    'processing_method': 'Docling + PaddleOCR'
                }
            }

            return integrated_result

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return {'error': str(e)}

    def _pdf_to_images(self, pdf_path: str) -> List[str]:
        """PDFを画像に変換 (簡易実装)"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            images = []

            temp_dir = Path("/tmp/paddle_ocr_images")
            temp_dir.mkdir(exist_ok=True)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                mat = fitz.Matrix(2, 2)  # 2倍のズーム
                pix = page.get_pixmap(matrix=mat)
                img_path = temp_dir / f"page_{page_num + 1}.png"
                pix.save(str(img_path))
                images.append(str(img_path))

            doc.close()
            return images

        except ImportError:
            logger.warning("PyMuPDF not available, trying alternative method")
            return self._pdf_to_images_alternative(pdf_path)
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            return []

    def _pdf_to_images_alternative(self, pdf_path: str) -> List[str]:
        """代替のPDF→画像変換方法"""
        try:
            import pdf2image
            from pdf2image import convert_from_path

            temp_dir = Path("/tmp/paddle_ocr_images")
            temp_dir.mkdir(exist_ok=True)

            images = convert_from_path(pdf_path, dpi=200)
            image_paths = []

            for i, image in enumerate(images):
                img_path = temp_dir / f"page_{i + 1}.png"
                image.save(str(img_path), 'PNG')
                image_paths.append(str(img_path))

            return image_paths

        except ImportError:
            logger.error("pdf2image not available. Please install: pip install pdf2image")
            return []
        except Exception as e:
            logger.error(f"Error in alternative PDF conversion: {str(e)}")
            return []

    def process_image_file(self, image_path: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        画像ファイルを処理

        Args:
            image_path: 画像ファイルのパス
            output_file: 出力ファイルのパス (オプション)

        Returns:
            処理結果
        """
        ocr_results = self.extract_text_from_image(image_path)

        result = {
            'source_file': image_path,
            'ocr_results': ocr_results,
            'total_text_blocks': len(ocr_results),
            'extracted_text': '\n'.join([item['text'] for item in ocr_results])
        }

        if output_file:
            self._save_result(result, output_file)

        return result

    def _save_result(self, result: Dict[str, Any], output_file: str):
        """結果をファイルに保存"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_file.endswith('.json'):
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            elif output_file.endswith('.txt'):
                with open(output_file, 'w', encoding='utf-8') as f:
                    if 'extracted_text' in result:
                        f.write(result['extracted_text'])
                    else:
                        f.write(json.dumps(result, ensure_ascii=False, indent=2))
            else:  # markdown format
                with open(output_file, 'w', encoding='utf-8') as f:
                    if 'docling_result' in result and result['docling_result']['markdown']:
                        f.write(result['docling_result']['markdown'])
                        f.write('\n\n## PaddleOCR Additional Results\n\n')

                    if 'paddle_ocr_results' in result:
                        for page_result in result['paddle_ocr_results']:
                            f.write(f"### Page {page_result['page']}\n\n")
                            for ocr_item in page_result['ocr_results']:
                                f.write(f"- {ocr_item['text']} (confidence: {ocr_item['confidence']:.3f})\n")
                            f.write('\n')

            logger.info(f"Results saved to {output_file}")

        except Exception as e:
            logger.error(f"Error saving results to {output_file}: {str(e)}")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='PaddleOCR + Docling Integration')
    parser.add_argument('input_file', help='Input file path (PDF or image)')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-f', '--format', choices=['markdown', 'json', 'text'],
                       default='markdown', help='Output format')
    parser.add_argument('-l', '--lang', default='en',
                       help='OCR language (en, ch, japan, etc.)')
    parser.add_argument('--gpu', action='store_true', help='Use GPU for OCR')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # 入力ファイルのパス処理 (相対パスの場合は/shared/input/を前置)
    input_path = args.input_file
    if not os.path.isabs(input_path):
        input_path = f"/shared/input/{input_path}"

    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # 出力ファイルのパス処理
    output_path = args.output
    if output_path and not os.path.isabs(output_path):
        output_path = f"/shared/output/{output_path}"

    # PaddleOCR統合インスタンスを作成
    integration = PaddleOCRDoclingIntegration(
        lang=args.lang,
        use_gpu=args.gpu,
        show_log=args.verbose
    )

    try:
        # ファイル形式に応じて処理
        if input_path.lower().endswith('.pdf'):
            logger.info(f"Processing PDF file: {input_path}")
            result = integration.process_pdf_with_paddle_ocr(input_path, args.format)
        else:
            logger.info(f"Processing image file: {input_path}")
            result = integration.process_image_file(input_path, output_path)

        # 結果を出力
        if output_path:
            integration._save_result(result, output_path)
        else:
            # 標準出力に結果を表示
            if args.format == 'json':
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                if 'extracted_text' in result:
                    print(result['extracted_text'])
                elif 'docling_result' in result:
                    docling_output = result['docling_result'].get(args.format)
                    if docling_output:
                        print(docling_output)
                    else:
                        print(json.dumps(result, ensure_ascii=False, indent=2))

        logger.info("Processing completed successfully")

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()