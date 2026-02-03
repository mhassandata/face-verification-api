# Deployment Checklist

## Pre-Deployment

- [ ] Review and update `README.md` with your contact info and license
- [ ] Update `DEPLOYMENT.md` with your server details
- [ ] Test all API endpoints locally
- [ ] Verify face detection works with sample images
- [ ] Check `requirements.txt` is up to date

## Files to Deploy

### Required Files
```
face_verify_app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── service.py
│   └── schemas.py
├── .gitignore
├── requirements.txt
├── README.md
└── DEPLOYMENT.md
```

### Auto-Created Folders (on first run)
- `cropped/` - Stores aligned face crops
- `manual_review/` - Stores cases needing review
- `~/.insightface/` - Model files (downloaded automatically)

### Do NOT Deploy
- `venv/` - Virtual environment (create fresh on server)
- `.git/` - Git repository (optional)
- `cropped/` - Local test data
- `manual_review/` - Local review data
- `__pycache__/` - Python cache

## Environment Setup on Server

```bash
# 1. Install Python 3.8+
python3 --version

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux
# venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test the server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Production Configuration

### 1. Environment Variables (Optional)
```bash
export WORKERS=4
export PORT=8000
export HOST=0.0.0.0
```

### 2. Run with Gunicorn (Recommended)
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### 3. Or Run with Uvicorn
```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

## Post-Deployment

- [ ] Test `/health` endpoint
- [ ] Test `/verify` with sample CNIC and selfie
- [ ] Monitor logs for errors
- [ ] Check memory usage
- [ ] Verify cropped images are being saved
- [ ] Test with rotated/landscape images
- [ ] Test with poor quality images
- [ ] Set up monitoring (optional)

## Security Checklist

- [ ] Enable HTTPS/SSL (see DEPLOYMENT.md)
- [ ] Configure firewall rules
- [ ] Set up rate limiting (optional)
- [ ] Enable CORS if needed
- [ ] Secure API with authentication (if required)
- [ ] Regular security updates

## Monitoring

### Key Metrics to Monitor
- Response time (should be < 2s for most requests)
- Memory usage (expect ~500MB per worker)
- CPU usage
- Error rate
- Face detection success rate

### Log Files
- Application logs: Check uvicorn/gunicorn output
- Failed detections: Check `cropped/*_NO_FACE_*.jpg`
- Manual review cases: Check `manual_review/` folder

## Troubleshooting

### Common Issues

**Issue**: Model files not downloading
```bash
# Manually download models
python -c "from insightface.app import FaceAnalysis; app = FaceAnalysis(name='buffalo_l'); app.prepare(ctx_id=0)"
```

**Issue**: Out of memory
```bash
# Reduce workers
uvicorn app.main:app --workers 2
```

**Issue**: Slow response times
```bash
# Check if using CPU (expected) or GPU
# For GPU support, install onnxruntime-gpu
pip install onnxruntime-gpu
```

## Backup Strategy

### What to Backup
- Application code (`app/` folder)
- Configuration files (`requirements.txt`, etc.)
- Manual review cases (`manual_review/` folder - optional)

### What NOT to Backup
- Virtual environment (`venv/`)
- Temporary crops (`cropped/`)
- Model files (can be re-downloaded)

## Version Information

- **Current Version**: 3.0.0
- **Python**: 3.8+
- **FastAPI**: Latest
- **InsightFace**: Latest

## Support

For deployment issues, refer to `DEPLOYMENT.md` or contact your system administrator.
