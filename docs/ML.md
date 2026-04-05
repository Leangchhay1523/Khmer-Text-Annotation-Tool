# ML Server - Khmer Data Annotation Tool

Machine Learning service for Khmer text extraction from images using multiple OCR engines.

## Quick Start

### 1. Install Dependencies

```bash
cd ml
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
```

Edit `.env` with your Tesseract path and API keys.

### 3. Run Server

```bash
cd models
python main.py
```

Server starts at `http://localhost:8000`

API docs: http://localhost:8000/docs

---

## Overview

The ML (Machine Learning) server is a Python-based FastAPI service that provides OCR (Optical Character Recognition) capabilities for Khmer text extraction from images. It supports multiple OCR engines and object detection models to accurately identify and extract text regions.

## Features

- 🔍 **Text Detection**: Automatic text region detection using DocTR or YOLO
- 📝 **Text Recognition**: OCR extraction using Tesseract, KiriOCR, or Gemini Vision
- 🎯 **Bounding Box Support**: Process user-defined or auto-detected text regions
- 📊 **Evaluation Metrics**: Compute CER (Character Error Rate) and WER (Word Error Rate)
- 🤖 **Multiple OCR Engines**: 
  - **Tesseract OCR** - Primary engine with Khmer language support
  - **KiriOCR** - Khmer-specific OCR engine (optional)
  - **Gemini Vision** - Cloud-based AI OCR via Google Gemini API
- 🔄 **Auto-Detection Pipeline**: Complete detection + extraction workflow
- 📈 **Model Evaluation**: Compare OCR performance against ground truth

## Architecture

```
Frontend → ML Server (FastAPI)
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
 DocTR/YOLO        Tesseract/KiriOCR/Gemini
 (Detection)       (Recognition)
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| ASGI Server | Uvicorn |
| OCR Detection | DocTR, YOLO (Ultralytics) |
| Text Recognition | Tesseract, KiriOCR, Gemini Vision |
| Image Processing | OpenCV, Pillow |
| Deep Learning | PyTorch, Torchvision |

## Prerequisites

Before running this project, ensure you have the following installed:

- **Python** (version 3.10 or higher)
- **Tesseract OCR** (version 5+ with Khmer language data)
- **Git** (for cloning the repository)

### Tesseract OCR Installation

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR\`
3. **IMPORTANT**: Select Khmer (khm) and English (eng) language data during installation
4. Add to system PATH: `C:\Program Files\Tesseract-OCR\`
5. Verify installation:
   ```bash
   tesseract --version
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-khm  # Khmer language data
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # Additional language data
```

## Installation

### 1. Navigate to ML Directory

```bash
cd ML
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

All dependencies are now in a single `requirements.txt` file at the root level.

### 4. Set Up Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Configure the following variables:

```env
# Server Configuration
HOST=127.0.0.1
PORT=8000

# Tesseract Configuration
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe  # Windows
# TESSERACT_PATH=/usr/bin/tesseract  # Linux/macOS
TESSERACT_LANG=khm+eng

# Backend API (for callbacks)
BACKEND_URL=http://localhost:3000

# Model Settings
YOLO_MODEL_PATH=utils/YoloKh/best.pt
CONFIDENCE_THRESHOLD=0.5

# Gemini API (optional)
GEMINI_API_KEY=your_api_key_here
```

### 5. Verify YOLO Model Weights

Ensure YOLO model weights exist in:
```
utils/YoloKh/best.pt
utils/YoloKh/best_V1.pt
```

## Running the ML Server

### From Root ML Directory

```bash
cd ML/models
python main.py
```

### Using Uvicorn Directly

```bash
cd ML/models
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

You should see:
```
Uvicorn running on http://127.0.0.1:8000
✅ Tesseract initialized
✅ YOLO model loaded
```

### Interactive API Documentation

FastAPI provides interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check - returns `{"message": "Server is running"}` |

### Text Detection & Extraction

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/detect` | Legacy detection endpoint; accepts `Image` model with `path` and `mode` (word/line); runs DocTR detection + Tesseract OCR |
| POST | `/detect-only` | DocTR detection only (no text extraction); returns bounding boxes with empty text |
| POST | `/detect-and-extract` | DocTR detection + Tesseract text extraction |
| POST | `/extract-text` | Full DocTR detection + Tesseract OCR; returns concatenated full text |

### OCR with Bounding Boxes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ocr` | Accepts uploaded image + user-drawn JSON bounding boxes; extracts text per box using selected OCR engine (Tesseract, KiriOCR, or Gemini) |

### Auto-Detection Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auto-detect` | Complete pipeline: accepts image, runs detection (DocTR or YOLO) + optional text extraction (Tesseract, KiriOCR, or Gemini); returns boxes with text and confidence scores |

### Model Evaluation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/evaluate` | Computes CER (Character Error Rate) and WER (Word Error Rate) between extracted text and ground truth |

## Request/Response Examples

### 1. OCR with User-Drawn Boxes

**Endpoint**: `POST /ocr`

**Request**:
- Content-Type: `multipart/form-data`
- Fields:
  - `image` (file): The image file
  - `boxes` (string): JSON array of bounding boxes
  - `recognition_model` (string, optional): `tesseract`, `kiriocr`, or `gemini`

**Boxes Format**:
```json
[
  {
    "x": 100,
    "y": 150,
    "width": 200,
    "height": 50
  }
]
```

**Response**:
```json
{
  "boxes": [
    {
      "x": 100,
      "y": 150,
      "width": 200,
      "height": 50,
      "text": "Extracted Khmer text",
      "confidence": 0.95
    }
  ]
}
```

### 2. Auto-Detect Pipeline

**Endpoint**: `POST /auto-detect`

**Request**:
- Content-Type: `multipart/form-data`
- Fields:
  - `file` (file): The image file
  - `detection_model` (string, optional): `docTR` or `yolo`
  - `recognition_model` (string, optional): `tesseract`, `kiriocr`, or `gemini`

**Response**:
```json
{
  "success": true,
  "image_width": 1920,
  "image_height": 1080,
  "boxes": [
    {
      "x": 100,
      "y": 150,
      "width": 200,
      "height": 50,
      "text": "Extracted text",
      "confidence": 0.92
    }
  ]
}
```

### 3. Model Evaluation

**Endpoint**: `POST /evaluate`

**Request Body**:
```json
{
  "extracted_text": "Text from OCR",
  "ground_truth": "Correct text",
  "model_name": "tesseract"
}
```

**Response**:
```json
{
  "cer": 0.05,
  "wer": 0.10,
  "model_name": "tesseract"
}
```

## Project Structure

```
ml/
├── .env                    # Environment configuration (gitignored)
├── .env.example            # Configuration template
├── .gitignore
├── requirements.txt        # Python dependencies (unified)
├── README.md               # Quick reference guide
├── models/
│   └── main.py             # FastAPI server entry point (1058 lines)
└── utils/
    ├── GeminiOCR.py        # Gemini Vision API wrapper
    └── YoloKh/
        ├── __init__.py     # Package init
        ├── YoloModel.py    # YOLO-based text detector
        ├── best.pt         # YOLO weights (primary)
        └── best_V1.pt      # YOLO weights (version 1)
```

## OCR Engines

### 1. Tesseract OCR (Default)

**Pros**:
- Fast and lightweight
- Good accuracy for printed text
- Supports Khmer language (`khm`)
- Runs locally (no API costs)

**Cons**:
- Lower accuracy on handwritten text
- Requires clean images for best results

**Configuration**:
- Language: `khm+eng` (Khmer + English)
- Path: Set via `TESSERACT_PATH` in `.env`

### 2. KiriOCR (Optional)

**Pros**:
- Specifically designed for Khmer text
- Better accuracy for Khmer script

**Cons**:
- Requires `kiri-ocr` package installation
- May not be actively maintained

**Installation**:
```bash
pip install kiri-ocr
```

### 3. Gemini Vision API (Cloud)

**Pros**:
- High accuracy on diverse text types
- Handles handwritten text well
- Cloud-based (no local compute needed)

**Cons**:
- Requires API key and billing
- Network latency
- Usage limits/costs

**Configuration**:
- Set `GEMINI_API_KEY` in `.env`
- Requires `google-generativeai` package

## Detection Models

### 1. DocTR (Primary)

**Technology**: Deep Learning-based document text detection

**Features**:
- Pre-trained OCR predictor
- Automatic text region detection
- Returns bounding boxes with confidence scores

**Loading**:
```python
from doctr.models import ocr_predictor
model = ocr_predictor(pretrained=True)
```

### 2. YOLO (Alternative)

**Technology**: Ultralytics YOLO for object detection

**Features**:
- Custom-trained for Khmer text detection
- Fast inference time
- Configurable confidence threshold

**Model Weights**:
- `utils/YoloKh/best.pt` - Primary model
- `utils/YoloKh/best_V1.pt` - Version 1

**Configuration**:
- Set via `YOLO_MODEL_PATH` in `.env`
- Adjust `CONFIDENCE_THRESHOLD` (default: 0.5)

## Image Preprocessing

The ML server applies preprocessing to improve OCR accuracy:

- **Grayscale Conversion**: Convert to single channel
- **Denoising**: Remove noise with Gaussian blur
- **Thresholding**: Binarize image for better contrast
- **Resizing**: Scale images to optimal size

## Evaluation Metrics

### Character Error Rate (CER)

Measures the edit distance between extracted and ground truth text at the character level:

```
CER = (Substitutions + Insertions + Deletions) / Total Characters
```

**Lower is better** (0.0 = perfect match)

### Word Error Rate (WER)

Measures the edit distance at the word level:

```
WER = (Substitutions + Insertions + Deletions) / Total Words
```

**Lower is better** (0.0 = perfect match)

## Development

### Adding New OCR Engines

1. Create engine wrapper in `utils/`
2. Implement detection and recognition methods
3. Add to `/ocr` and `/auto-detect` endpoints
4. Update API documentation

### Adding New Detection Models

1. Create detection model class in `utils/`
2. Implement `detect()` method returning bounding boxes
3. Integrate into `/auto-detect` pipeline
4. Add configuration options via `.env`

### Testing

```bash
# Test the server
cd models
python main.py

# Test Tesseract
tesseract image.jpg stdout -l khm+eng

# Test YOLO model
python -c "from utils.YoloKh.YoloModel import YOLODetector; print('YOLO loaded')"
```

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Test individual components:

```bash
# Test Tesseract
tesseract image.jpg stdout -l khm+eng

# Test YOLO model
python -c "from utils.YoloKh.YoloModel import YoloModel; print('YOLO loaded')"
```

## Troubleshooting

### Common Issues

#### Tesseract Not Found

**Error**: `TesseractNotFoundError`

**Solution**:
1. Verify Tesseract is installed: `tesseract --version`
2. Check `TESSERACT_PATH` in `.env`
3. Ensure Tesseract is in system PATH
4. On Windows, use full path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

#### Khmer Language Not Available

**Error**: `Error opening data file khm.traineddata`

**Solution**:
1. Reinstall Tesseract and select Khmer language data
2. Download `khm.traineddata` from https://github.com/tesseract-ocr/tessdata_fast
3. Copy to Tesseract's `tessdata` folder
4. Verify with: `tesseract --list-langs`

#### DocTR Import Error

**Error**: `ModuleNotFoundError: No module named 'doctr'`

**Solution**:
```bash
pip install python-doctr[viz,html,contrib]
```

#### YOLO Model Not Loading

**Error**: `FileNotFoundError: best.pt not found`

**Solution**:
1. Check `YOLO_MODEL_PATH` in `.env`
2. Verify file exists at specified path
3. Use relative or absolute path correctly

#### Gemini API Errors

**Error**: `403 Permission denied` or `400 Invalid API key`

**Solution**:
1. Verify `GEMINI_API_KEY` is correct
2. Enable billing on Google Cloud Console
3. Check API quota limits
4. Ensure `google-generativeai` is installed

#### Port Already in Use

**Error**: `[Errno 10048] Address already in use`

**Solution**:
```bash
# Find process
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

#### Memory Errors

**Error**: `Out of memory` or CUDA errors

**Solution**:
1. Reduce image size before processing
2. Use CPU instead of GPU if memory-constrained
3. Close other applications
4. Increase virtual memory (Windows)

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `HOST` | Yes | Server host (default: 127.0.0.1) |
| `PORT` | Yes | Server port (default: 8000) |
| `TESSERACT_PATH` | Yes | Path to Tesseract executable |
| `TESSERACT_LANG` | Yes | Language code (default: khm+eng) |
| `BACKEND_URL` | No | Backend API URL for callbacks |
| `YOLO_MODEL_PATH` | No | Path to YOLO weights file |
| `CONFIDENCE_THRESHOLD` | No | Detection confidence (default: 0.5) |
| `GEMINI_API_KEY` | No | Google Gemini API key |

## Performance Optimization

### Tips for Better OCR Results

1. **Use High-Quality Images**: Higher resolution = better accuracy
2. **Good Lighting**: Avoid shadows and glare
3. **Tight Bounding Boxes**: Draw boxes closely around text
4. **Preprocess Images**: Denoise and enhance contrast
5. **Choose Right Engine**: 
   - Printed text → Tesseract
   - Khmer-specific → KiriOCR
   - Handwritten/mixed → Gemini

### Speed Optimization

- Use YOLO for detection (faster than DocTR)
- Reduce image resolution for preview
- Cache detection results
- Batch process multiple images

## Dependencies

### Core

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **python-multipart** - Form data parsing

### OCR & Detection

- **python-doctr** - Primary OCR engine with detection
- **pytesseract** - Tesseract wrapper
- **ultralytics** - YOLO object detection
- **opencv-python** - Image processing
- **Pillow** - Image manipulation

### Deep Learning

- **torch** - PyTorch
- **torchvision** - Computer vision library

### Utilities

- **numpy** - Numerical computing
- **tqdm** - Progress bars
- **python-dotenv** - Environment variable loading
- **httpx** - Async HTTP client
- **google-generativeai** - Gemini API (optional)

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Endpoint descriptions
- Request/response schemas
- Try-it-out functionality
- Authentication requirements

## Future Enhancements

- [ ] Support for additional languages
- [ ] Improved handwritten text recognition
- [ ] Batch processing endpoint
- [ ] Model fine-tuning capabilities
- [ ] Caching layer for repeated requests
- [ ] WebSocket support for real-time processing
- [ ] Docker containerization
- [ ] GPU acceleration optimizations
