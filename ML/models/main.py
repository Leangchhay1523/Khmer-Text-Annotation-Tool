"""
ML OCR Server - Khmer Text Recognition

FastAPI service for Khmer text extraction from images using multiple OCR engines.
Supports DocTR/YOLO for detection and Tesseract/KiriOCR/Gemini for recognition.
"""

# ============================================================================
# Imports
# ============================================================================

import io
import os
import re
import sys
import time
import tempfile
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from dotenv import load_dotenv
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image as PILImage
import pytesseract
from pydantic import BaseModel
from tqdm import tqdm

# Add parent directory to Python path for utils imports
# This is needed because utils/ is a sibling directory to models/
_UTILS_PATH = Path(__file__).resolve().parent.parent
if str(_UTILS_PATH) not in sys.path:
    sys.path.insert(0, str(_UTILS_PATH))

# Import from utils package
from utils.YoloKh.YoloModel import YOLODetector  # type: ignore
from utils.GeminiOCR import GeminiOCR, extract_text_gemini  # type: ignore

# KiriOCR for Khmer text recognition (optional)
try:
    from kiri_ocr import OCR as KiriOCR
    KIRI_OCR_AVAILABLE = True
except ImportError:
    KIRI_OCR_AVAILABLE = False
    print("WARNING: kiri_ocr not installed. Install with: pip install kiri-ocr")


# ============================================================================
# Pydantic Models
# ============================================================================

class ImageRequest(BaseModel):
    """Request model for image path-based detection."""
    path: str
    mode: str = "word"  # "word" or "line"


class BoundingBox(BaseModel):
    """Bounding box model for detection results."""
    x: int
    y: int
    width: int
    height: int
    text: str
    confidence: float


class AutoDetectResponse(BaseModel):
    """Response model for auto-detect endpoint."""
    success: bool
    image_width: int = 0
    image_height: int = 0
    boxes: List[Dict[str, Any]] = []
    error: str = ""


class EvaluateRequest(BaseModel):
    """Request model for model evaluation."""
    extracted_text: str
    ground_truth: str
    model_name: str = "Tesseract"


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="ML OCR Server - Khmer Text Recognition",
    description="OCR service for Khmer text extraction using DocTR, YOLO, Tesseract, KiriOCR, and Gemini Vision",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Configuration & Model Loading
# ============================================================================

def load_environment():
    """Load environment variables from .env file."""
    script_dir = Path(__file__).resolve().parent
    dotenv_path = script_dir / ".env"
    
    if not dotenv_path.exists():
        dotenv_path = script_dir.parent.parent / ".env"
    
    print(f"[CONFIG] Looking for .env at: {dotenv_path}")
    print(f"[CONFIG] .env exists: {dotenv_path.exists()}")
    
    load_dotenv(dotenv_path=dotenv_path)


def configure_tesseract():
    """Configure Tesseract OCR path and verify Khmer language support."""
    tesseract_cmd = os.getenv("TESSERACT_CMD")
    tessdata_prefix = os.getenv("TESSERACT_TESSDATA_PREFIX")
    
    if not (tesseract_cmd and tessdata_prefix):
        print("[WARN] Tesseract environment variables not found. Please set TESSERACT_CMD and TESSERACT_TESSDATA_PREFIX in .env file.")
        return False
    
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    os.environ["TESSDATA_PREFIX"] = tessdata_prefix
    print("[CONFIG] Tesseract configured successfully.")
    
    # Check available languages
    try:
        langs = pytesseract.get_languages(config='')
        print(f"[CONFIG] Tesseract available languages: {langs}")
        
        if 'khm' not in langs:
            print("[WARN] Khmer language (khm) not found in Tesseract!")
            print("[WARN] Please install Khmer language data:")
            print("[WARN] 1. Re-run Tesseract installer")
            print("[WARN] 2. Select 'Additional Language Data'")
            print("[WARN] 3. Check 'Khmer' language pack")
            return False
        else:
            print("[CONFIG] ✓ Khmer language is available in Tesseract")
            return True
            
    except Exception as e:
        print(f"[WARN] Could not check Tesseract languages: {e}")
        return False


def load_doctr_model() -> ocr_predictor:
    """Load DocTR OCR predictor model."""
    print("[MODEL] Loading DocTR OCR model...")
    model = ocr_predictor(pretrained=True)
    print("[MODEL] DocTR model loaded successfully.")
    return model


def load_kiriocr():
    """Load KiriOCR model if available."""
    if not KIRI_OCR_AVAILABLE:
        print("[MODEL] KiriOCR not available — Tesseract will be used as fallback.")
        return None
    
    try:
        print("[MODEL] Loading KiriOCR model...")
        model = KiriOCR()
        print("[MODEL] KiriOCR model loaded successfully.")
        return model
    except Exception as e:
        print(f"[WARN] Failed to load KiriOCR: {e}")
        return None


def load_yolo_model():
    """Load YOLO detection model if weights exist."""
    try:
        yolo_weights = Path(__file__).resolve().parent.parent / "utils" / "YoloKh" / "best.pt"
        
        if not yolo_weights.exists():
            print(f"[WARN] YOLO weights not found at {yolo_weights}")
            return None
        
        print(f"[MODEL] Loading YOLO model from {yolo_weights}...")
        model = YOLODetector(str(yolo_weights))
        print("[MODEL] YOLO model loaded successfully.")
        return model
        
    except Exception as e:
        print(f"[WARN] Failed to load YOLO model: {e}")
        return None


def load_gemini_model():
    """Initialize Gemini Vision API if configured."""
    try:
        print("[MODEL] Initializing Gemini Vision API...")
        model = GeminiOCR()
        health = model.health_check()
        
        if health.get("status") == "healthy":
            print("[CONFIG] ✓ Gemini Vision API initialized successfully")
            return model
        else:
            print(f"[WARN] Gemini API issue: {health.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"[WARN] Failed to initialize Gemini: {e}")
        return None


# Load environment and initialize models
load_environment()
configure_tesseract()

# Global model instances
doctr_model = load_doctr_model()
kiri_model = load_kiriocr()
yolo_model = load_yolo_model()
gemini_model = load_gemini_model()


# ============================================================================
# Helper Functions - Path Resolution
# ============================================================================

def resolve_image_path(image_path: str) -> str:
    """Resolve image path from frontend URL to local file path."""
    if image_path.startswith("/api/upload/images/"):
        filename = image_path.replace("/api/upload/images/", "")
        frontend_upload_dir = os.path.join(
            os.path.dirname(__file__), "..", "frontend", "upload", "images"
        )
        resolved_path = os.path.join(frontend_upload_dir, filename)
        print(f"[PATH] Resolving: {resolved_path}")
        return resolved_path
    return image_path


# ============================================================================
# Helper Functions - Coordinate Conversion
# ============================================================================

def convert_to_absolute_boxes(
    result,
    image_shapes: list,
    original_width: int,
    original_height: int,
    detection_mode: str = "word"
) -> List[Dict[str, Any]]:
    """Convert DocTR relative coordinates to absolute pixel coordinates.

    Args:
        result: OCR result from DocTR
        image_shapes: List of (height, width) tuples for each page as loaded by DocTR
        original_width: Original image width
        original_height: Original image height
        detection_mode: "word" for word-level boxes, "line" for line-level boxes
    
    Returns:
        List of box dicts with x, y, width, height, text, confidence
    """
    boxes = []

    for page_idx, page in enumerate(result.pages):
        doc_height, doc_width = image_shapes[page_idx]

        for block in page.blocks:
            for line in block.lines:
                if detection_mode == "line":
                    # Merge all words in the line into one box
                    all_word_geometries = [word.geometry for word in line.words]
                    if not all_word_geometries:
                        continue

                    xmin_rel = min(g[0][0] for g in all_word_geometries)
                    ymin_rel = min(g[0][1] for g in all_word_geometries)
                    xmax_rel = max(g[1][0] for g in all_word_geometries)
                    ymax_rel = max(g[1][1] for g in all_word_geometries)

                    avg_confidence = sum(word.confidence for word in line.words) / len(line.words) if line.words else 0.0

                    xmin = int(xmin_rel * original_width)
                    ymin = int(ymin_rel * original_height)
                    xmax = int(xmax_rel * original_width)
                    ymax = int(ymax_rel * original_height)

                    boxes.append({
                        "x": xmin,
                        "y": ymin,
                        "width": xmax - xmin,
                        "height": ymax - ymin,
                        "text": "",
                        "confidence": float(avg_confidence)
                    })
                else:
                    # Word-level detection
                    for word in line.words:
                        geometry = word.geometry
                        (xmin_rel, ymin_rel), (xmax_rel, ymax_rel) = geometry

                        xmin = int(xmin_rel * original_width)
                        ymin = int(ymin_rel * original_height)
                        xmax = int(xmax_rel * original_width)
                        ymax = int(ymax_rel * original_height)

                        boxes.append({
                            "x": xmin,
                            "y": ymin,
                            "width": xmax - xmin,
                            "height": ymax - ymin,
                            "text": "",
                            "confidence": float(word.confidence) if word.confidence else 0.0
                        })

    return boxes


# ============================================================================
# Helper Functions - Box Merging
# ============================================================================

def _merge_boxes_into_lines(
    boxes: List[Dict[str, Any]],
    y_threshold: float = 0.5
) -> List[Dict[str, Any]]:
    """Merge word-level boxes into line-level boxes based on vertical overlap."""
    if not boxes:
        return []

    sorted_boxes = sorted(boxes, key=lambda b: (b["y"], b["x"]))
    lines: List[List[Dict[str, Any]]] = []

    for box in sorted_boxes:
        merged = False
        box_cy = box["y"] + box["height"] / 2
        
        for line in lines:
            rep = line[0]
            rep_cy = rep["y"] + rep["height"] / 2
            overlap_thresh = min(box["height"], rep["height"]) * y_threshold
            
            if abs(box_cy - rep_cy) < overlap_thresh:
                line.append(box)
                merged = True
                break
        
        if not merged:
            lines.append([box])

    merged_boxes = []
    for line in lines:
        x_min = min(b["x"] for b in line)
        y_min = min(b["y"] for b in line)
        x_max = max(b["x"] + b["width"] for b in line)
        y_max = max(b["y"] + b["height"] for b in line)
        avg_conf = sum(b["confidence"] for b in line) / len(line)
        
        merged_boxes.append({
            "x": x_min,
            "y": y_min,
            "width": x_max - x_min,
            "height": y_max - y_min,
            "text": "",
            "confidence": avg_conf,
        })

    return merged_boxes


# ============================================================================
# Helper Functions - Image Preprocessing
# ============================================================================

def preprocess_for_ocr(pil_image) -> PILImage.Image:
    """Preprocess image for OCR - optimized for Khmer script.

    Khmer script has complex stacked characters that need careful preprocessing.

    Args:
        pil_image: PIL Image object

    Returns:
        Preprocessed PIL Image
    """
    # Convert to grayscale
    gray = np.array(pil_image.convert("L"))

    # Apply light denoising - too much will destroy Khmer subscript characters
    denoised = cv2.fastNlMeansDenoising(
        gray, h=5, templateWindowSize=7, searchWindowSize=21
    )

    # Use Otsu's thresholding but with inversion check
    _, thresh = cv2.threshold(
        denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Check if we need to invert (text should be black on white for Tesseract)
    white_pixels = np.sum(thresh == 255)
    total_pixels = thresh.size
    
    if white_pixels / total_pixels < 0.5:
        # More than half is dark - likely inverted, so invert back
        thresh = cv2.bitwise_not(thresh)

    return PILImage.fromarray(thresh)


# ============================================================================
# Helper Functions - OCR Engines
# ============================================================================

def extract_text_with_tesseract(
    pil_image: PILImage.Image,
    box_coords: Tuple[int, int, int, int]
) -> Tuple[str, float]:
    """Extract text from a cropped image region using Tesseract.
    Optimized for Khmer script with multiple PSM modes.

    Args:
        pil_image: PIL Image object (full image)
        box_coords: Tuple of (x1, y1, x2, y2) coordinates

    Returns:
        Tuple of (extracted_text, confidence)
    """
    x1, y1, x2, y2 = box_coords

    # Validate coordinates
    img_width, img_height = pil_image.size
    x1 = max(0, min(x1, img_width))
    y1 = max(0, min(y1, img_height))
    x2 = max(0, min(x2, img_width))
    y2 = max(0, min(y2, img_height))

    if x2 <= x1 or y2 <= y1:
        return "", 0.0

    # Crop the region
    cropped = pil_image.crop((x1, y1, x2, y2))

    # Skip if too small
    if cropped.size[0] < 8 or cropped.size[1] < 8:
        return "", 0.0

    # Preprocess for OCR
    preprocessed = preprocess_for_ocr(cropped)

    # DEBUG: Save cropped and preprocessed images for debugging
    DEBUG_SAVE = os.getenv("DEBUG_SAVE_IMAGES", "False").lower() == "true"
    if DEBUG_SAVE:
        debug_dir = os.getenv("DEBUG_OCR_DIR", "D:/debug_ocr")
        os.makedirs(debug_dir, exist_ok=True)
        debug_idx = int(time.time() * 1000) % 100000
        box_num = int(time.time() * 1000) % 1000
        
        try:
            cropped.save(f"{debug_dir}/cropped_{box_num:03d}_{debug_idx}.png")
            preprocessed.save(f"{debug_dir}/preprocessed_{box_num:03d}_{debug_idx}.png")
            print(f"  [DEBUG] Saved images: cropped_{box_num:03d}_{debug_idx}.png")
        except Exception as e:
            print(f"  [DEBUG] Failed to save debug images: {e}")

    try:
        best_text = ""
        best_confidence = 0.0

        # Try different PSM modes and pick the best result
        psm_modes = [
            ('--psm 7 --oem 3', "Single line"),
            ('--psm 6 --oem 3', "Uniform block"),
            ('--psm 13 --oem 1', "Raw line LSTM"),
        ]

        for config, mode_name in psm_modes:
            try:
                raw_text = pytesseract.image_to_string(
                    preprocessed, lang="khm", config=config
                )
                text = re.sub(r"\s+", " ", raw_text).strip()

                # Skip if result is mostly non-Khmer characters (likely garbage)
                if text:
                    khmer_chars = sum(1 for c in text if '\u1780' <= c <= '\u17FF')
                    total_chars = len(text.replace(' ', ''))

                    # If less than 30% Khmer characters and has random symbols, skip
                    if total_chars > 0 and khmer_chars / total_chars < 0.3:
                        if any(c in text for c in ['=', '/', '-', '_', '|']):
                            continue

                    # Get confidence
                    try:
                        data = pytesseract.image_to_data(
                            preprocessed,
                            lang="khm",
                            config=config,
                            output_type=pytesseract.Output.DICT
                        )
                        confs = [int(c) for c in data['conf'] if int(c) > 0]
                        confidence = sum(confs) / len(confs) / 100.0 if confs else 0.5
                    except:
                        confidence = 0.5

                    # Keep the result with highest confidence
                    if confidence > best_confidence:
                        best_text = text
                        best_confidence = confidence

            except Exception as e:
                continue

        if best_text:
            print(f"  [Tesseract Khmer] Text: '{best_text}' (conf: {best_confidence:.2f})")
            return best_text, best_confidence

        return "", 0.0

    except Exception as e:
        print(f"[ERROR] Tesseract OCR error: {e}")
        return "", 0.0


def extract_text_with_kiriocr(
    pil_image: PILImage.Image,
    box_coords: Tuple[int, int, int, int]
) -> Tuple[str, float]:
    """Extract text from a cropped image region using KiriOCR.

    Args:
        pil_image: PIL Image object (full image)
        box_coords: Tuple of (x1, y1, x2, y2) coordinates

    Returns:
        Tuple of (extracted_text, confidence)
    """
    if kiri_model is None:
        print("  [WARN] KiriOCR not available, falling back to Tesseract")
        return extract_text_with_tesseract(pil_image, box_coords)

    x1, y1, x2, y2 = box_coords

    # Validate coordinates
    img_width, img_height = pil_image.size
    x1 = max(0, min(x1, img_width))
    y1 = max(0, min(y1, img_height))
    x2 = max(0, min(x2, img_width))
    y2 = max(0, min(y2, img_height))

    if x2 <= x1 or y2 <= y1:
        return "", 0.0

    cropped = pil_image.crop((x1, y1, x2, y2))
    if cropped.size[0] < 8 or cropped.size[1] < 8:
        return "", 0.0

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            cropped.save(tmp, format="PNG")
            tmp_path = tmp.name

        try:
            text, results = kiri_model.extract_text(tmp_path)
            text = text.strip() if text else ""

            # Compute average confidence from detailed results
            if results and len(results) > 0:
                confs = [r.confidence for r in results if hasattr(r, "confidence")]
                avg_conf = sum(confs) / len(confs) if confs else 0.5
            else:
                avg_conf = 0.5 if text else 0.0

            if text:
                print(f"  [KiriOCR] Text: '{text}' (conf: {avg_conf:.2f})")
            return text, avg_conf
            
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        print(f"[ERROR] KiriOCR error: {e}")
        return "", 0.0


def extract_text_with_gemini(
    pil_image: PILImage.Image,
    box_coords: Tuple[int, int, int, int]
) -> Tuple[str, float]:
    """Extract text from a cropped image region using Gemini Vision API.

    Args:
        pil_image: PIL Image object (full image)
        box_coords: Tuple of (x1, y1, x2, y2) coordinates

    Returns:
        Tuple of (extracted_text, confidence)
    """
    if gemini_model is None:
        print("  [WARN] Gemini model not initialized, falling back to Tesseract")
        return extract_text_with_tesseract(pil_image, box_coords)

    x1, y1, x2, y2 = box_coords

    # Validate coordinates
    img_width, img_height = pil_image.size
    x1 = max(0, min(x1, img_width))
    y1 = max(0, min(y1, img_height))
    x2 = max(0, min(x2, img_width))
    y2 = max(0, min(y2, img_height))

    if x2 <= x1 or y2 <= y1:
        return "", 0.0

    cropped = pil_image.crop((x1, y1, x2, y2))
    if cropped.size[0] < 8 or cropped.size[1] < 8:
        return "", 0.0

    try:
        text, confidence = gemini_model.extract_text_from_pil_image(cropped)
        text = text.strip() if text else ""
        return text, confidence
        
    except Exception as e:
        print(f"[ERROR] Gemini OCR error: {e}, falling back to Tesseract")
        return extract_text_with_tesseract(pil_image, box_coords)


# ============================================================================
# Helper Functions - Detection Pipelines
# ============================================================================

def run_yolo_detection(
    image_path: str,
    mode: str = "word"
) -> List[Dict[str, Any]]:
    """Run YOLO detection and return boxes in the same format as DocTR.

    Args:
        image_path: Path to the image file
        mode: "word" or "line" - for YOLO, both return raw detections

    Returns:
        List of box dicts with x, y, width, height, text, confidence
    """
    if yolo_model is None:
        print("[WARN] YOLO model not available")
        return []

    results = yolo_model.predict_image(image_path)
    detections = yolo_model.get_detections(results)

    boxes = []
    for det in detections:
        bbox = det["bbox"]
        if isinstance(bbox[0], list):
            x1, y1, x2, y2 = [int(v) for v in bbox[0]]
        else:
            x1, y1, x2, y2 = [int(v) for v in bbox]

        boxes.append({
            "x": x1,
            "y": y1,
            "width": x2 - x1,
            "height": y2 - y1,
            "text": "",
            "confidence": det["confidence"],
        })

    if mode == "line":
        boxes = _merge_boxes_into_lines(boxes)

    return boxes


def run_doctr_detection(
    image_path: str,
    mode: str,
    extract_text: bool = False,
    recognition_model: str = "tesseract"
) -> Dict[str, Any]:
    """Run DocTR detection and optionally extract text with OCR engine.

    Args:
        image_path: Path to the image file
        mode: "word" or "line" detection mode
        extract_text: If True, extract text using selected OCR engine
        recognition_model: OCR engine to use (tesseract, kiriocr, gemini)

    Returns:
        Dictionary with success status, image dimensions, and detected boxes
    """
    resolved_path = resolve_image_path(image_path)

    # Load image using PIL to get original dimensions
    pil_img = PILImage.open(resolved_path)
    original_width, original_height = pil_img.size
    print(f"[IMAGE] Original size: {original_width} x {original_height}")

    # Load image for DocTR
    doc = DocumentFile.from_images(resolved_path)
    image_shapes = [img.shape[:2] for img in doc]
    doc_height, doc_width = image_shapes[0]
    print(f"[IMAGE] DocTR size: {doc_width} x {doc_height}")

    # Simulate progress
    print("[OCR] Running DocTR detection...")
    for _ in tqdm(range(5), desc="Processing", ncols=100):
        time.sleep(0.3)

    # Run OCR
    result = doctr_model(doc)
    print(f"[OCR] Result: {len(result.pages)} pages")

    # Convert to absolute coordinates
    boxes = convert_to_absolute_boxes(
        result, image_shapes, original_width, original_height, mode
    )
    print(f"[OCR] Detected {len(boxes)} boxes (mode: {mode})")

    # Optionally extract text
    if extract_text:
        # Select OCR engine
        use_kiriocr = recognition_model == "kiriocr" and kiri_model is not None
        use_gemini = recognition_model == "gemini" and gemini_model is not None

        if recognition_model == "kiriocr" and kiri_model is None:
            print("[WARN] KiriOCR requested but not available, falling back to Tesseract")
        if recognition_model == "gemini" and gemini_model is None:
            print("[WARN] Gemini requested but not available, falling back to Tesseract")

        engine_name = "Gemini" if use_gemini else "KiriOCR" if use_kiriocr else "Tesseract"
        print(f"[OCR] Extracting text from {len(boxes)} boxes using {engine_name}...")
        
        for idx, box in enumerate(boxes):
            box_coords = (
                box["x"],
                box["y"],
                box["x"] + box["width"],
                box["y"] + box["height"]
            )
            
            if use_gemini:
                extracted, confidence = extract_text_with_gemini(pil_img, box_coords)
            elif use_kiriocr:
                extracted, confidence = extract_text_with_kiriocr(pil_img, box_coords)
            else:
                extracted, confidence = extract_text_with_tesseract(pil_img, box_coords)
            
            box["text"] = extracted
            box["confidence"] = confidence

            if extracted:
                print(f"  Box {idx + 1}: '{extracted}' (conf: {confidence:.2f})")
            else:
                print(f"  Box {idx + 1}: [no text extracted]")
        
        print(f"[OCR] Text extraction completed for all {len(boxes)} boxes")
    else:
        print("[OCR] Skipping text extraction (detection only)")

    return {
        "success": True,
        "image_width": original_width,
        "image_height": original_height,
        "boxes": boxes
    }


# ============================================================================
# Helper Functions - Evaluation
# ============================================================================

def _edit_distance(seq1, seq2) -> int:
    """Compute Levenshtein edit distance between two sequences."""
    m, n = len(seq1), len(seq2)
    dp = list(range(n + 1))
    
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        
        for j in range(1, n + 1):
            temp = dp[j]
            if seq1[i - 1] == seq2[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = temp
    
    return dp[n]


# ============================================================================
# API Endpoints - Health Check
# ============================================================================

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Server is running"}


# ============================================================================
# API Endpoints - Image Path Detection
# ============================================================================

@app.post("/detect")
def detect_text(image: ImageRequest):
    """Detect text regions and extract text using Tesseract.
    
    Accepts an ImageRequest with path and mode, runs DocTR detection + Tesseract OCR.
    """
    try:
        image_path = resolve_image_path(image.path)
        
        pil_img = PILImage.open(image_path)
        original_width, original_height = pil_img.size
        print(f"[IMAGE] Original size: {original_width} x {original_height}")

        doc = DocumentFile.from_images(image_path)
        image_shapes = [img.shape[:2] for img in doc]
        doc_height, doc_width = image_shapes[0]
        print(f"[IMAGE] DocTR size: {doc_width} x {doc_height}")

        print("[OCR] Running DocTR detection...")
        for _ in tqdm(range(5), desc="Processing", ncols=100):
            time.sleep(0.3)

        result = doctr_model(doc)
        print(f"[OCR] Result: {len(result.pages)} pages")

        boxes = convert_to_absolute_boxes(
            result, image_shapes, original_width, original_height, image.mode
        )
        print(f"[OCR] Detected {len(boxes)} boxes (mode: {image.mode})")

        print(f"[OCR] Extracting text from {len(boxes)} boxes...")
        for idx, box in enumerate(boxes):
            box_coords = (
                box["x"],
                box["y"],
                box["x"] + box["width"],
                box["y"] + box["height"]
            )
            extracted_text, confidence = extract_text_with_tesseract(pil_img, box_coords)
            box["text"] = extracted_text
            box["confidence"] = confidence

            if extracted_text:
                print(f"  Box {idx + 1}: '{extracted_text}' (conf: {confidence:.2f})")
            else:
                print(f"  Box {idx + 1}: [no text extracted]")

        print(f"[OCR] Text extraction completed")

        return {
            "success": True,
            "image_width": original_width,
            "image_height": original_height,
            "boxes": boxes
        }
        
    except Exception as e:
        print(f"[ERROR] Error during detection: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "boxes": []
        }


@app.post("/detect-only")
def detect_only(image: ImageRequest):
    """Detect text regions using DocTR only (no text extraction)."""
    try:
        result = run_doctr_detection(image.path, image.mode, extract_text=False)
        return result
    except Exception as e:
        print(f"[ERROR] Error during detection: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "boxes": []
        }


@app.post("/detect-and-extract")
def detect_and_extract(image: ImageRequest):
    """Detect text regions using DocTR and extract text using Tesseract."""
    try:
        result = run_doctr_detection(image.path, image.mode, extract_text=True)
        return result
    except Exception as e:
        print(f"[ERROR] Error during detection: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "boxes": []
        }


# ============================================================================
# API Endpoints - File Upload OCR
# ============================================================================

@app.post("/ocr")
async def ocr_endpoint(
    image: UploadFile = File(...),
    annotations: str = Form("[]"),
    project_id: str = Form(""),
    recognition_model: str = Form("tesseract"),
):
    """Accept an uploaded image + bounding box annotations, extract text from each box.
    
    Args:
        image: Uploaded image file
        annotations: JSON array of [x1, y1, x2, y2] boxes
        project_id: Project identifier (optional)
        recognition_model: OCR engine (tesseract, kiriocr, gemini)
    
    Returns:
        Processing result with extracted text per box
    """
    start_time = time.time()
    
    try:
        import json as _json
        boxes = _json.loads(annotations)
        
        if not boxes or not isinstance(boxes, list):
            return {"success": False, "processing_result": [], "error": "No annotations provided"}

        contents = await image.read()
        pil_img = PILImage.open(io.BytesIO(contents)).convert("RGB")
        original_width, original_height = pil_img.size
        print(f"[OCR] Image: {image.filename}, size: {original_width}x{original_height}, boxes: {len(boxes)}, model: {recognition_model}")

        use_kiriocr = recognition_model == "kiriocr" and kiri_model is not None
        use_gemini = recognition_model == "gemini" and gemini_model is not None

        if recognition_model == "kiriocr" and kiri_model is None:
            print("[WARN] KiriOCR requested but not available, falling back to Tesseract")
        if recognition_model == "gemini" and gemini_model is None:
            print("[WARN] Gemini requested but not available, falling back to Tesseract")

        processing_result = []
        for idx, box in enumerate(boxes):
            if not isinstance(box, list) or len(box) < 4:
                processing_result.append({"extracted_text": "", "confidence": 0.0})
                continue

            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            x1 = max(0, min(x1, original_width))
            y1 = max(0, min(y1, original_height))
            x2 = max(0, min(x2, original_width))
            y2 = max(0, min(y2, original_height))

            if x2 <= x1 or y2 <= y1:
                processing_result.append({"extracted_text": "", "confidence": 0.0})
                continue

            box_coords = (x1, y1, x2, y2)
            
            if use_gemini:
                extracted, confidence = extract_text_with_gemini(pil_img, box_coords)
            elif use_kiriocr:
                extracted, confidence = extract_text_with_kiriocr(pil_img, box_coords)
            else:
                extracted, confidence = extract_text_with_tesseract(pil_img, box_coords)

            processing_result.append({"extracted_text": extracted, "confidence": confidence})
            print(f"  Box {idx+1}: [{x1},{y1},{x2},{y2}] -> '{extracted}' (conf: {confidence:.2f})")

        elapsed = (time.time() - start_time) * 1000
        print(f"[OCR] Done in {elapsed:.0f}ms, processed {len(processing_result)} boxes")

        return {
            "success": True,
            "processing_result": processing_result,
            "inference_speed": round(elapsed, 2),
        }

    except Exception as e:
        print(f"[ERROR] OCR error: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "processing_result": [],
            "error": str(e),
        }


@app.post("/extract-text")
async def extract_text_endpoint(
    image: UploadFile = File(...),
    model_name: str = Form("Tesseract"),
    font: str = Form("Khmer"),
):
    """Accept an uploaded image, run DocTR detection + Tesseract OCR, return full text."""
    start_time = time.time()
    
    try:
        contents = await image.read()
        pil_img = PILImage.open(io.BytesIO(contents)).convert("RGB")
        original_width, original_height = pil_img.size
        print(f"[EXTRACT] Image: {image.filename}, size: {original_width}x{original_height}, model: {model_name}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            doc = DocumentFile.from_images(tmp_path)
            image_shapes = [img.shape[:2] for img in doc]
            result = doctr_model(doc)

            boxes = convert_to_absolute_boxes(
                result, image_shapes, original_width, original_height, "line"
            )
            print(f"[EXTRACT] Detected {len(boxes)} text regions")

            all_texts = []
            for idx, box in enumerate(boxes):
                box_coords = (
                    box["x"],
                    box["y"],
                    box["x"] + box["width"],
                    box["y"] + box["height"]
                )
                extracted, confidence = extract_text_with_tesseract(pil_img, box_coords)
                
                if extracted:
                    all_texts.append(extracted)
                    print(f"  Region {idx+1}: '{extracted}' (conf: {confidence:.2f})")

            full_text = "\n".join(all_texts) if all_texts else ""
            elapsed = (time.time() - start_time) * 1000
            print(f"[EXTRACT] Done in {elapsed:.0f}ms, extracted {len(all_texts)} text lines")

            return {
                "success": True,
                "text": full_text,
                "inference_speed": round(elapsed, 2),
                "regions": len(boxes),
            }
            
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        print(f"[ERROR] Extract error: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "text": "",
            "error": str(e),
            "inference_speed": 0,
        }


@app.post("/auto-detect")
async def auto_detect(
    image: UploadFile = File(...),
    mode: str = Form("word"),
    extract_text: bool = Form(False),
    detection_model: str = Form("doctr"),
    recognition_model: str = Form("tesseract"),
):
    """Accept an uploaded image, run detection and optionally extract text.
    
    Args:
        image: Uploaded image file
        mode: Detection mode (word or line)
        extract_text: Whether to extract text from detected boxes
        detection_model: Detection engine (doctr or yolo)
        recognition_model: Recognition engine (tesseract, kiriocr, gemini)
    
    Returns:
        Bounding boxes with optional extracted text
    """
    try:
        contents = await image.read()
        pil_img = PILImage.open(io.BytesIO(contents)).convert("RGB")
        original_width, original_height = pil_img.size
        print(f"[AUTO] Image: {image.filename}, size: {original_width}x{original_height}, mode: {mode}, extract: {extract_text}")
        print(f"[AUTO] Detection: {detection_model}, Recognition: {recognition_model}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            doc = DocumentFile.from_images(tmp_path)
            image_shapes = [img.shape[:2] for img in doc]

            # Detection phase
            if detection_model == "yolo" and yolo_model is not None:
                print("[AUTO] Running YOLO detection...")
                boxes = run_yolo_detection(tmp_path, mode)
                print(f"[AUTO] YOLO detected {len(boxes)} boxes (mode: {mode})")
            else:
                if detection_model == "yolo" and yolo_model is None:
                    print("[WARN] YOLO requested but not available, falling back to DocTR")
                print("[AUTO] Running DocTR detection...")
                result = doctr_model(doc)
                boxes = convert_to_absolute_boxes(
                    result, image_shapes, original_width, original_height, mode
                )
                print(f"[AUTO] DocTR detected {len(boxes)} boxes (mode: {mode})")

            # Recognition phase
            if extract_text:
                use_kiriocr = recognition_model == "kiriocr" and kiri_model is not None
                use_gemini = recognition_model == "gemini" and gemini_model is not None

                if recognition_model == "kiriocr" and kiri_model is None:
                    print("[WARN] KiriOCR requested but not available, falling back to Tesseract")
                if recognition_model == "gemini" and gemini_model is None:
                    print("[WARN] Gemini requested but not available, falling back to Tesseract")

                engine_name = "Gemini" if use_gemini else "KiriOCR" if use_kiriocr else "Tesseract"
                print(f"[AUTO] Extracting text from {len(boxes)} boxes using {engine_name}...")
                
                for idx, box in enumerate(boxes):
                    box_coords = (
                        box["x"],
                        box["y"],
                        box["x"] + box["width"],
                        box["y"] + box["height"]
                    )
                    
                    if use_gemini:
                        extracted, confidence = extract_text_with_gemini(pil_img, box_coords)
                    elif use_kiriocr:
                        extracted, confidence = extract_text_with_kiriocr(pil_img, box_coords)
                    else:
                        extracted, confidence = extract_text_with_tesseract(pil_img, box_coords)
                    
                    box["text"] = extracted
                    box["confidence"] = confidence

            return {
                "success": True,
                "image_width": original_width,
                "image_height": original_height,
                "boxes": boxes,
            }
            
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        print(f"[ERROR] Auto-detect error: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "image_width": 0,
            "image_height": 0,
            "boxes": [],
            "error": str(e),
        }


# ============================================================================
# API Endpoints - Model Evaluation
# ============================================================================

@app.post("/evaluate")
def evaluate_endpoint(req: EvaluateRequest):
    """Compute CER (Character Error Rate) and WER (Word Error Rate) between extracted text and ground truth."""
    start_time = time.time()
    
    try:
        extracted = req.extracted_text
        ground_truth = req.ground_truth

        # Character Error Rate (CER)
        cer = _edit_distance(list(extracted), list(ground_truth)) / max(len(ground_truth), 1)

        # Word Error Rate (WER)
        ext_words = extracted.split()
        gt_words = ground_truth.split()
        wer = _edit_distance(ext_words, gt_words) / max(len(gt_words), 1)

        elapsed = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "cer": round(min(cer, 1.0), 4),
            "wer": round(min(wer, 1.0), 4),
            "inference_speed": round(elapsed, 2),
        }
        
    except Exception as e:
        print(f"[ERROR] Evaluate error: {e}")
        return {"success": False, "cer": 0, "wer": 0, "inference_speed": 0, "error": str(e)}


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
