# Available InsightFace Model Packs and Recommendations

## Current Model: buffalo_l
- Recognition: ArcFace R50 (w600k_r50.onnx)
- Good for: General face recognition
- Weakness: Struggles with quality disparity (CNIC vs Selfie)

## Better Options for CNIC vs Selfie

### Option 1: antelopev2 (RECOMMENDED - Best Accuracy)
```python
self.app = FaceAnalysis(name='antelopev2', providers=['CPUExecutionProvider'])
```
- **Recognition Model**: ArcFace R100 (more powerful than R50)
- **Accuracy**: ~5-10% better than buffalo_l
- **Speed**: ~2x slower (but still acceptable on CPU)
- **Best for**: High-accuracy applications, handles quality differences better

### Option 2: buffalo_sc (Faster, Less Accurate)
```python
self.app = FaceAnalysis(name='buffalo_sc', providers=['CPUExecutionProvider'])
```
- **Recognition Model**: ArcFace MobileFaceNet
- **Accuracy**: ~5% worse than buffalo_l
- **Speed**: ~3x faster
- **Best for**: Speed-critical applications

### Option 3: Custom Model Loading (Advanced)
Load a custom ONNX model (like AdaFace) manually.

## AdaFace Integration (Manual)

AdaFace is not in InsightFace's model zoo, but you can integrate it manually:

### Step 1: Download AdaFace Model
- GitHub: https://github.com/mk-minchul/AdaFace
- Model: adaface_ir50_ms1mv2.onnx or adaface_ir101_webface12m.onnx

### Step 2: Load with ONNX Runtime
```python
import onnxruntime as ort
import numpy as np

class AdaFaceRecognizer:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
    
    def get_embedding(self, aligned_face):
        # aligned_face should be 112x112 BGR image
        # Normalize to [-1, 1]
        img = aligned_face.astype(np.float32)
        img = (img - 127.5) / 128.0
        img = np.transpose(img, (2, 0, 1))  # HWC to CHW
        img = np.expand_dims(img, axis=0)   # Add batch dimension
        
        # Run inference
        embedding = self.session.run([self.output_name], {self.input_name: img})[0]
        return embedding[0]  # Return 512-d embedding
```

### Step 3: Integrate into Service
Replace the InsightFace recognition model with AdaFace while keeping RetinaFace for detection.

## Practical Recommendation

**For your use case (CNIC vs Selfie), I recommend:**

1. **First try**: Switch to `antelopev2` (easy, 5-10% improvement)
2. **If still not enough**: Implement multi-model ensemble (use both buffalo_l and antelopev2, take max score)
3. **Advanced**: Manually integrate AdaFace (requires downloading external model)

## Quick Test: Switch to antelopev2

Change one line in `service.py`:
```python
# OLD
self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])

# NEW
self.app = FaceAnalysis(name='antelopev2', providers=['CPUExecutionProvider'])
```

Expected improvement: +5-10% similarity score
