# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a containerized document processing system using IBM Docling for multi-format document conversion. The project uses Podman with podman-compose for orchestration and provides Japanese language support through Tesseract OCR.

## Core Architecture

**Container Structure:**
- Base image: `python:3.11-slim`
- Main service: `docling-processor`
- Processing script: `process_documents.py` (copied to `/app/` in container)
- Persistent command: `tail -f /dev/null` (keeps container running)

**Volume Mount Strategy:**
```
./data/input  -> /shared/input   (input documents)
./data/output -> /shared/output  (processed results)
./data/config -> /shared/config  (configuration files)
./data/cache  -> /shared/cache   (Docling cache)
```

**Key Configuration:**
- User mapping: `0:0` (root) to handle volume permissions
- SELinux labels: `:Z` flag on all volume mounts for proper access
- Port exposure: `8000:8000` for optional FastAPI server mode

## Essential Commands

**Container Management:**
```bash
# Build container image
podman-compose build

# Start container (background)
podman-compose up -d

# Stop container
podman-compose down

# Check container status
podman-compose ps
```

**Using Management Script:**
```bash
# Make executable (if needed)
chmod +x scripts.sh

# Process single document (outputs to Markdown by default)
./scripts.sh process filename.pdf

# Check container and directory status
./scripts.sh status

# Access container shell
./scripts.sh shell

# View container logs
./scripts.sh logs
```

**Direct Container Commands:**
```bash
# Process with specific output format
podman exec docling-processor python process_documents.py /shared/input/document.pdf json

# Process entire directory
podman exec docling-processor python process_documents.py /shared/input/

# Process with RapidOCR engine
podman exec docling-processor docling --ocr-engine rapidocr --to md /shared/input/document.pdf --output /shared/output/document.md

# Access container interactively
podman exec -it docling-processor bash
```

## Document Processing Capabilities

**Supported Input Formats:** PDF, DOCX, PPTX, HTML, TXT, MD, JSON, XML
**Output Formats:** Markdown (default), JSON, Text

**Processing Script Logic:**
- Relative paths are automatically prefixed with `/shared/input/`
- Output files are created in `/shared/output/` with appropriate extensions
- Supports both single file and directory batch processing
- Japanese text processing via Tesseract OCR (tesseract-ocr-jpn package)

## Critical Configuration Details

**Volume Permission Requirements:**
- The container runs as root (`user: "0:0"`) due to Podman user namespace mapping
- Volume mounts use `:Z` SELinux label for proper access
- Host directories in `./data/` must be accessible by the container user

**Container Lifecycle:**
- Container uses `tail -f /dev/null` to stay running indefinitely
- Health check verifies Docling import capability
- Graceful shutdown may require SIGKILL after SIGTERM timeout

## System Dependencies

**Installed in Container:**
- LibreOffice (document conversion)
- Tesseract OCR with Japanese language pack
- Pandoc (markup conversion)
- Poppler utilities (PDF processing)
- Build tools and development libraries

**Python Dependencies:**
- docling, docling-core, docling-ibm-models
- fastapi, uvicorn (for optional API mode)
- python-multipart
- onnxruntime (required for RapidOCR engine)

## Troubleshooting Common Issues

**Volume Mount Problems:**
- Ensure directories exist: `mkdir -p data/{input,output,config,cache}`
- Check permissions: `chmod -R 755 data/`
- Verify SELinux labels are applied correctly

**Container Won't Start/Process Files:**
- Rebuild after Dockerfile changes: `podman-compose build`
- Check volume mounts with: `podman exec docling-processor df -h`
- Verify file accessibility: `podman exec docling-processor ls -la /shared/input/`

**RapidOCR Engine Issues:**
- If encountering "ImportError: onnxruntime is not installed", rebuild container with no-cache: `podman-compose build --no-cache`
- RapidOCR requires onnxruntime package for optimal performance
- Verify RapidOCR availability: `podman exec docling-processor docling --ocr-engine rapidocr --help`
- Test RapidOCR functionality: `podman exec docling-processor docling --ocr-engine rapidocr --to md input.pdf --output output.md`

## Optional Features

**FastAPI Server Mode:**
```bash
# Start API server inside container
podman exec -d docling-processor uvicorn api_server:app --host 0.0.0.0 --port 8000
```
Access at `http://localhost:8000` when running.

**Custom Configuration:**
Edit `data/config/docling_config.py` to customize:
- OCR language settings and DPI
- Output format preferences
- Supported file type filtering