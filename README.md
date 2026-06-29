# 🔍 Local Image Upscaler & Resizer
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
A fully local image upscaling and resizing tool — no API, no internet required.

## Features
- **Upscale** blurry/small images (1.5×, 2×, 3×, 4×, up to 8×) using Lanczos/Bicubic
- **Preset resize** for Instagram, Twitter, YouTube, WhatsApp, Wallpaper 4K, Print A4, and more
- **Custom size** with optional aspect ratio lock
- Fit modes: Letterbox (no crop), Fill (crop to cover), Stretch
- Export as JPEG, PNG, or WebP with quality control

## Run locally

```bash
# 1. Install dependencies (only needs to be done once)
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Deploy to Hugging Face Spaces

1. Create a new Space (SDK: Streamlit)
2. Upload `app.py` and `requirements.txt`
3. That's it — no `packages.txt` needed (pure Python, no system packages)

## No API key needed
Everything runs locally using Pillow's built-in resampling algorithms.
For even sharper upscaling, you can later integrate Real-ESRGAN (requires PyTorch).
