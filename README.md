# Face Verification API

A production-ready face verification API optimized for CNIC (ID card) vs Selfie matching scenarios. Built with InsightFace, FastAPI, and advanced preprocessing techniques.

## Features

### 🎯 Core Capabilities
- **Face Detection & Alignment**: 5-point landmark-based alignment for accurate embeddings
- **Multi-Method Verification**: Cosine similarity, Euclidean distance, and Pearson correlation
- **🆕 Dynamic Similarity Selection**: Automatically selects the highest score among all methods for maximum accuracy
- **Quality Compensation**: Automatic boost for CNIC vs Selfie quality disparities (up to 60% boost)
- **Baseline Enhancement**: 20% baseline boost for all comparisons

### Perception Pipeline in this App:
**Raw Image → Detection Perception → Alignment Perception → Feature Perception → Similarity Perception → Decision**

### 🔧 Advanced Detection
- **🆕 Proactive Landscape Auto-Rotation**: Automatically detects and corrects landscape CNIC orientation BEFORE processing
- **4-Layer Optimized Fallback System**: Handles challenging images with essential detection strategies
  1. Original image processing
  2. Aggressive contrast enhancement
  3. Lower detection threshold (0.15)
  4. **Auto-rotation** (0°, 90°, 180°, 270°) for rotated/landscape images

### 📊 Smart Processing
- **Conservative Preprocessing**: Balanced enhancement without embedding degradation
- **Quality Assessment**: Automatic quality scoring and compensation
- **Manual Review System**: Flags uncertain cases for human review
- **Graceful Error Handling**: Returns 200 OK with helpful messages instead of errors

## New Features (v3.1.0)

### 🎯 Feature 1: Dynamic Similarity Selection

The system now **intelligently selects the best similarity metric** for each verification:

**How it works:**
- Calculates 3 different similarity scores:
  - Cosine similarity (with quality boost)
  - Euclidean distance
  - Pearson correlation
- **Automatically picks the highest score** as the final result
- Shows which method was selected in the response

**Benefits:**
- **Maximizes true positive rate** - catches matches that one method might miss
- **Adapts to different scenarios** - some faces work better with euclidean, others with cosine
- **Transparent selection** - logs show which method was chosen and why

**Example:**
```json
{
  "similarity_score": 0.353,
  "selected_method": "euclidean",
  "cosine_similarity": 0.241,
  "euclidean_similarity": 0.353,
  "pearson_similarity": 0.162,
}
```

**Console Output:**
```
📊 Similarity Scores:
   Cosine:    0.241
   Euclidean: 0.353
   Pearson:   0.162
✓ Selected: EUCLIDEAN (0.353) as final score
```

### 🔄 Feature 2: Proactive Landscape Auto-Rotation

CNIC cards in landscape orientation are now **automatically detected and rotated BEFORE processing**:

**How it works:**
- Detects if image is landscape (width > height)
- Tries all 4 orientations (0°, 90°, 180°, 270°)
- Selects orientation with best face detection
- Rotates image to correct orientation
- Proceeds with normal processing

**Benefits:**
- **Faster processing** - rotation happens upfront, not as last resort
- **Better accuracy** - face is detected in optimal orientation from the start
- **Cleaner crops** - saved images are always upright
- **Higher success rate** - no more failed detections due to wrong orientation

**Example Console Output:**
```
⚠️  cnic is LANDSCAPE (1920x1080)
   Trying to find correct orientation...
   ✓ Found 1 face(s) in 90° clockwise (score: 0.842)
   ✅ Auto-rotated cnic to correct orientation (1080x1920)
✓ Face aligned using landmarks for cnic
```

**Before vs After:**
- **Before**: Landscape CNIC → 6 failed attempts → rotation fallback → success (slow)
- **After**: Landscape CNIC → auto-detect → rotate → immediate success (fast)

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd face_verify_app

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (see DEPLOYMENT.md for full guide)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Usage

### Verify Faces

**Endpoint**: `POST /verify`

**Request**:
```bash
curl -X POST "http://localhost:8000/verify" \
  -F "cnic_image=@cnic.jpg" \
  -F "selfie_image=@selfie.jpg"
```

**Response**:
```json
{
  "similarity_score": 0.72,
  "is_match": true,
  "confidence": "HIGH",
  "needs_manual_review": false,
  "selected_method": "ensemble",
  "cosine_similarity": 0.70,
  "euclidean_similarity": 0.71,
  "pearson_similarity": 0.69,
  "image_quality_1": {
    "quality_score": 0.85,
    "face_size": 246,
    "detection_score": 0.84
  },
  "image_quality_2": {
    "quality_score": 0.65,
    "face_size": 180,
    "detection_score": 0.77
  },
  "faces_found_image_1": 1,
  "faces_found_image_2": 1,
  "execution_time_ms": 1250.5,
  "message": "CNIC and Selfie match verified. High confidence."
}
```

### Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

## Configuration

### Detection Thresholds

Edit `app/service.py`:

```python
self.SIMILARITY_THRESHOLD = 0.30        # Main threshold
self.SIMILARITY_THRESHOLD_HIGH = 0.40   # High confidence
self.SIMILARITY_THRESHOLD_MEDIUM = 0.35 # Review zone
```

### Quality Boost Settings

```python
baseline_boost = 1.20  # 20% baseline boost
additional_boost = 1.0 + (avg_quality * 0.5)  # Up to 25% additional
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

## Image Requirements

### Optimal
- Face clearly visible and well-lit
- Face occupies 20-50% of image
- Resolution: 640×640 or higher
- Upright orientation (auto-corrected if rotated)

### Minimum
- Face occupies at least 5% of image
- Minimum face size: 50×50 pixels
- Any orientation (auto-rotation handles 90°/180°/270°)

## Output Folders

- `cropped/`: Aligned face crops (112×112) for audit
- `manual_review/`: Cases flagged for manual review

## Performance

- **Average response time**: 500-1500ms
- **With fallback detection**: 2-6 seconds
- **Memory usage**: ~500MB per worker
- **Recommended**: 4 workers for production

## Model Information

- **Model**: InsightFace Buffalo_L
- **Detector**: RetinaFace
- **Recognition**: ArcFace R50
- **Embedding size**: 512 dimensions
- **Detection size**: 640×640

## Error Handling

The API returns 200 OK for all cases with appropriate messages:

### No Face Detected
```json
{
  "similarity_score": null,
  "is_match": false,
  "message": "⚠️ No face detected in CNIC image(s). The system tried 7 different detection methods...",
  "faces_found_image_1": 0
}
```

### Processing Error
```json
{
  "similarity_score": null,
  "is_match": false,
  "message": "Error processing images: ...",
  "review_reason": "Image processing error"
}
```

## Deployment

See `DEPLOYMENT.md` for detailed production deployment instructions including:
- Docker deployment
- Nginx configuration
- SSL/TLS setup
- Performance optimization
- Monitoring setup

## Dependencies

- Python 3.8+
- FastAPI
- InsightFace
- OpenCV (cv2)
- NumPy
- Uvicorn

See `requirements.txt` for complete list.

## License

[Your License Here]

## Support

For issues or questions, please contact [Your Contact Info]

---

**Version**: 3.1.0  
**Last Updated**: 2026-02-04

**New in v3.1.0:**
- 🎯 Dynamic Similarity Selection (automatically picks best method)
- 🔄 Proactive Landscape Auto-Rotation (detects and corrects orientation upfront)
