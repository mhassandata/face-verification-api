# Production Deployment Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

**Development:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Access the API

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📦 Production Deployment

### Option 1: Docker (Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Create necessary directories
RUN mkdir -p cropped manual_review

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  face-verify-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./cropped:/app/cropped
      - ./manual_review:/app/manual_review
    environment:
      - WORKERS=4
    restart: unless-stopped
```

**Deploy:**
```bash
docker-compose up -d
```

### Option 2: Systemd Service (Linux)

Create `/etc/systemd/system/face-verify.service`:

```ini
[Unit]
Description=Face Verification API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/face_verify_app
Environment="PATH=/opt/face_verify_app/venv/bin"
ExecStart=/opt/face_verify_app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable face-verify
sudo systemctl start face-verify
sudo systemctl status face-verify
```

### Option 3: Windows Service

Use `nssm` (Non-Sucking Service Manager):

```bash
# Download nssm from https://nssm.cc/download

# Install service
nssm install FaceVerifyAPI "D:\face_verify_app\venv\Scripts\uvicorn.exe" "app.main:app --host 0.0.0.0 --port 8000 --workers 4"
nssm set FaceVerifyAPI AppDirectory "D:\face_verify_app"

# Start service
nssm start FaceVerifyAPI
```

---

## ⚙️ Production Configuration

### Environment Variables

Create `.env` file:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=info

# Application Settings
SIMILARITY_THRESHOLD=0.30
SIMILARITY_THRESHOLD_HIGH=0.40
QUALITY_COMPENSATION_ENABLED=true
MANUAL_REVIEW_ENABLED=true

# Paths
CROPPED_FOLDER=./cropped
REVIEW_FOLDER=./manual_review

# Security (add in production)
API_KEY=your-secret-api-key-here
ALLOWED_ORIGINS=https://yourdomain.com
```

### Load Environment Variables

Update `app/main.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

# Use environment variables
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.30'))
```

---

## 🔒 Security Checklist

### Essential Security Measures

- [ ] **HTTPS**: Use reverse proxy (Nginx/Caddy) with SSL certificate
- [ ] **API Authentication**: Implement API key or JWT authentication
- [ ] **Rate Limiting**: Limit requests per IP (e.g., 100/hour)
- [ ] **File Size Limits**: Max 10MB per image
- [ ] **CORS**: Configure allowed origins
- [ ] **Input Validation**: Already implemented
- [ ] **Logging**: Enable access logs
- [ ] **Monitoring**: Set up health checks
- [ ] **Firewall**: Restrict access to necessary ports
- [ ] **Data Privacy**: Comply with GDPR/privacy laws

### Nginx Reverse Proxy Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # File upload size limit
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 Monitoring & Logging

### Health Monitoring

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","model":"insightface-buffalo_l"}
```

### Application Logs

**Enable logging in `app/main.py`:**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('face_verify.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring Tools

- **Prometheus + Grafana**: Metrics and dashboards
- **Sentry**: Error tracking
- **New Relic / DataDog**: APM monitoring
- **ELK Stack**: Log aggregation

---

## 🔧 Performance Optimization

### 1. Use GPU (if available)

Update `app/service.py`:

```python
self.app = FaceAnalysis(
    name='buffalo_l',
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)
```

**Expected speedup**: 5-10x faster

### 2. Increase Workers

```bash
uvicorn app.main:app --workers 8  # Adjust based on CPU cores
```

**Rule of thumb**: (2 × CPU cores) + 1

### 3. Enable Caching

For repeated comparisons, implement Redis caching:

```python
import hashlib
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_result(img1_hash, img2_hash):
    key = f"{img1_hash}:{img2_hash}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None
```

### 4. Async Processing

For batch operations, use background tasks:

```python
from fastapi import BackgroundTasks

@app.post("/verify-batch")
async def verify_batch(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_batch)
    return {"status": "processing"}
```

---

## 📈 Scaling

### Horizontal Scaling

**Load Balancer (Nginx):**

```nginx
upstream face_verify_backend {
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://face_verify_backend;
    }
}
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: face-verify-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: face-verify
  template:
    metadata:
      labels:
        app: face-verify
    spec:
      containers:
      - name: api
        image: face-verify:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

---

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### API Test

```bash
curl -X POST "http://localhost:8000/verify" \
  -F "source_image=@test_cnic.jpg" \
  -F "target_image=@test_selfie.jpg"
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 -p test_data.txt -T multipart/form-data http://localhost:8000/verify
```

---

## 📁 Production File Structure

```
face_verify_app/
├── app/
│   ├── __init__.py
│   ├── main.py              # API endpoints
│   ├── service.py           # Face verification logic
│   └── schemas.py           # Response models
├── cropped/                 # Aligned face images (auto-created)
├── manual_review/           # Flagged cases (auto-created)
├── docs/                    # Documentation
│   ├── ENHANCED_SYSTEM_GUIDE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── ...
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore rules
├── CHANGELOG.md            # Version history
├── DEPLOYMENT.md           # This file
├── README.md               # Main documentation
└── requirements.txt        # Python dependencies
```

---

## 🔄 Backup & Recovery

### Backup Strategy

**What to backup:**
1. Application code (Git repository)
2. `cropped/` folder (audit trail)
3. `manual_review/` folder (review cases)
4. Configuration files (`.env`)
5. Logs

**Backup script:**

```bash
#!/bin/bash
BACKUP_DIR="/backups/face_verify_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup data
cp -r /opt/face_verify_app/cropped $BACKUP_DIR/
cp -r /opt/face_verify_app/manual_review $BACKUP_DIR/
cp /opt/face_verify_app/.env $BACKUP_DIR/

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Keep only last 30 days
find /backups -name "face_verify_*.tar.gz" -mtime +30 -delete
```

---

## 📞 Support

For production issues:
1. Check logs: `tail -f face_verify.log`
2. Check health: `curl http://localhost:8000/health`
3. Review manual_review folder for flagged cases
4. Check system resources: `htop` or Task Manager

---

**Last Updated**: February 2, 2026  
**Version**: 2.1.0  
**Status**: Production Ready ✅
