---
title: Local Image Upscaler
emoji: 🔍
colorFrom: purple
colorTo: blue
sdk: streamlit
sdk_version: "1.32.0"
app_file: app.py
pinned: false
---

# 🔍 Local Image Upscaler & Resizer

Upscale blurry images · Fix aspect ratios · Export any size — **all local, no API, no internet needed.**

---

## ▶️ Run Locally

**Step 1 — Install dependencies (only do this once)**
```bash
pip install -r requirements.txt
```

**Step 2 — Run the app**
```bash
streamlit run app.py
```

**Step 3 — Open in browser**
```
http://localhost:8501
```

To stop the app, press `Ctrl + C` in the terminal.

---

## 📦 What's Inside

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit app |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

---

## 🛠️ Features

- **Upscale** — Scale images 1.5×, 2×, 3×, 4×, 6×, 8× using Lanczos / Bicubic / Bilinear
- **Preset Resize** — Instagram, Twitter, YouTube, WhatsApp, 4K Wallpaper, A4 Print, and more
- **Custom Size** — Enter any width × height with optional aspect ratio lock
- **Fit Modes** — Letterbox (no crop) · Fill (crop to cover) · Stretch
- **Export** — JPEG, PNG, or WebP with quality control

---

## 💾 Push to GitHub (Backup)

```bash
git init
git add .
git commit -m "Initial commit: local image upscaler"
git remote add origin https://github.com/MaazzAlii/local-image-upscaler.git
git branch -M main
git push -u origin main
```

For future updates:
```bash
git add .
git commit -m "your update message"
git push origin main
```

---

## 🚀 Deploy to Hugging Face Spaces (do this later after watching a tutorial)

```bash
# Add Hugging Face as a remote
git remote add huggingface https://huggingface.co/spaces/MaazzAlii/local-image-upscaler

# Push to Hugging Face
git push huggingface main
```

It will ask for your HF username + Access Token (create one at huggingface.co → Settings → Access Tokens).

For future updates to HF:
```bash
git push huggingface main
```

---

## ✅ Requirements

- Python 3.8+
- Pillow
- Streamlit

No GPU needed. No API key needed. Runs fully offline.
