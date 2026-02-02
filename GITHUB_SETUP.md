# GitHub Setup Guide - Face Verification API

## 📋 Prerequisites

- [x] Git installed on your system
- [ ] GitHub account created
- [ ] Git configured with your credentials

---

## 🚀 Step-by-Step Guide

### Step 1: Check Git Installation

```bash
git --version
```

If not installed, download from: https://git-scm.com/downloads

### Step 2: Configure Git (First Time Only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Initialize Git Repository

```bash
# Navigate to project directory
cd d:\face_verify_app

# Initialize git repository
git init

# Check status
git status
```

### Step 4: Create .gitignore (Already Done ✅)

The `.gitignore` file is already created and will exclude:
- Virtual environment (`venv/`)
- Python cache (`__pycache__/`)
- Runtime data (`cropped/`, `manual_review/`)
- Environment files (`.env`)

### Step 5: Stage All Files

```bash
# Add all files to staging
git add .

# Check what will be committed
git status
```

### Step 6: Create Initial Commit

```bash
git commit -m "Initial commit: Face Verification API v2.1.0

Features:
- Quality disparity compensation for CNIC vs Selfie
- Multi-method verification (Cosine + Euclidean + Ensemble)
- Automatic manual review system
- 5-level confidence system
- Image quality assessment
- Image preprocessing and alignment
- Production-ready with comprehensive documentation"
```

### Step 7: Create GitHub Repository

**Option A: Via GitHub Website (Recommended)**

1. Go to https://github.com
2. Click the "+" icon (top right) → "New repository"
3. Fill in details:
   - **Repository name**: `face-verification-api`
   - **Description**: `Production-ready face verification API with quality compensation for CNIC vs Selfie matching`
   - **Visibility**: ✅ **Private** (Important!)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click "Create repository"

**Option B: Via GitHub CLI (if installed)**

```bash
gh repo create face-verification-api --private --source=. --remote=origin
```

### Step 8: Link Local Repository to GitHub

After creating the repository on GitHub, you'll see commands like:

```bash
# Add remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/face-verification-api.git

# Verify remote
git remote -v
```

### Step 9: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

### Step 10: Verify Upload

1. Go to https://github.com/YOUR_USERNAME/face-verification-api
2. Verify all files are uploaded
3. Check that it's marked as **Private** 🔒

---

## 🔐 Authentication Options

### Option 1: Personal Access Token (Recommended)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `repo` (full control of private repositories)
4. Copy the token (you won't see it again!)
5. When pushing, use token as password:
   - Username: your GitHub username
   - Password: paste the token

### Option 2: SSH Key (More Secure)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub:
# Settings → SSH and GPG keys → New SSH key
# Paste the public key

# Use SSH remote URL
git remote set-url origin git@github.com:YOUR_USERNAME/face-verification-api.git
```

---

## 📁 What Gets Pushed

### ✅ Included (Will be pushed)

```
✅ app/                    # Application code
✅ docs/                   # Documentation
✅ .gitignore             # Git ignore rules
✅ CHANGELOG.md           # Version history
✅ DEPLOYMENT.md          # Deployment guide
✅ PRODUCTION_CHECKLIST.md
✅ PRODUCTION_READY.md
✅ README.md              # Main documentation
✅ requirements.txt       # Dependencies
✅ start.bat              # Startup scripts
✅ start.sh
```

### ❌ Excluded (Will NOT be pushed)

```
❌ venv/                  # Virtual environment (too large)
❌ __pycache__/           # Python cache
❌ cropped/               # Runtime data (contains user images)
❌ manual_review/         # Review data (sensitive)
❌ .env                   # Environment variables (secrets)
❌ *.log                  # Log files
```

---

## 🔄 Future Updates

### Making Changes and Pushing

```bash
# 1. Make your changes to files

# 2. Check what changed
git status
git diff

# 3. Stage changes
git add .
# Or stage specific files:
git add app/service.py

# 4. Commit changes
git commit -m "Description of changes"

# 5. Push to GitHub
git push
```

### Example Workflow

```bash
# After fixing a bug
git add app/service.py
git commit -m "Fix: Corrected quality compensation calculation"
git push

# After adding a feature
git add app/main.py app/service.py
git commit -m "Feature: Added batch verification endpoint"
git push

# After updating documentation
git add README.md
git commit -m "Docs: Updated API examples"
git push
```

---

## 🌿 Branching Strategy (Optional)

### For Team Development

```bash
# Create development branch
git checkout -b development

# Create feature branch
git checkout -b feature/new-model

# Make changes and commit
git add .
git commit -m "Add new face recognition model"

# Push feature branch
git push -u origin feature/new-model

# Merge to main (via Pull Request on GitHub)
```

---

## 🔒 Security Best Practices

### Never Commit These

- ❌ API keys or secrets
- ❌ Database passwords
- ❌ `.env` files with credentials
- ❌ User images or personal data
- ❌ Large binary files (models are OK if needed)

### Use Environment Variables

Create `.env.example` (safe to commit):

```env
# Example environment variables
SIMILARITY_THRESHOLD=0.30
API_KEY=your-api-key-here
DATABASE_URL=your-database-url
```

Then in `.gitignore` (already added):
```
.env
.env.local
```

---

## 📊 Repository Settings

### Recommended Settings

1. **Settings → General**
   - ✅ Restrict who can push to main branch
   - ✅ Require pull request reviews

2. **Settings → Branches**
   - Add branch protection rule for `main`
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass

3. **Settings → Security**
   - ✅ Enable Dependabot alerts
   - ✅ Enable secret scanning

---

## 🎯 Quick Reference

### Common Commands

```bash
# Check status
git status

# View changes
git diff

# Add all changes
git add .

# Commit changes
git commit -m "Your message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- filename
```

---

## 🚨 Troubleshooting

### Issue: "Permission denied"

**Solution**: Use Personal Access Token or SSH key (see Authentication Options above)

### Issue: "Repository not found"

**Solution**: Check remote URL
```bash
git remote -v
# Update if wrong:
git remote set-url origin https://github.com/YOUR_USERNAME/face-verification-api.git
```

### Issue: "Large files rejected"

**Solution**: Files over 100MB are rejected. Use Git LFS or exclude them.

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.onnx"

# Commit .gitattributes
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

### Issue: "Merge conflicts"

**Solution**: Pull first, resolve conflicts, then push
```bash
git pull
# Resolve conflicts in files
git add .
git commit -m "Resolve merge conflicts"
git push
```

---

## ✅ Verification Checklist

After pushing, verify:

- [ ] Repository is **Private** 🔒
- [ ] All essential files are present
- [ ] No sensitive data committed (API keys, passwords)
- [ ] No large unnecessary files (venv, cache)
- [ ] README.md displays correctly
- [ ] .gitignore is working (check excluded files)

---

## 📞 Need Help?

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com/
- **GitHub Support**: https://support.github.com/

---

## 🎉 You're Done!

Your face verification API is now:
- ✅ Version controlled with Git
- ✅ Backed up on GitHub (private)
- ✅ Ready for team collaboration
- ✅ Protected with .gitignore

**Next Steps:**
1. Share repository with team members (Settings → Collaborators)
2. Set up CI/CD (GitHub Actions)
3. Enable branch protection
4. Start developing!

---

**Created**: February 2, 2026  
**Version**: 1.0  
**Status**: Ready to Push ✅
