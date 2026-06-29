import streamlit as st
from PIL import Image
import io
import math

# ── Raise Pillow's pixel limit so large upscales don't crash ──────────────────
# Default limit is ~178M pixels. We raise it to 1 billion (safe for local use).
Image.MAX_IMAGE_PIXELS = 1_000_000_000

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Image Upscaler & Resizer",
    page_icon="🔍",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main { background: #0f0f13; }

.stApp {
    background: linear-gradient(135deg, #0f0f13 0%, #1a1a2e 100%);
    color: #e2e8f0;
}

h1 { 
    color: #a78bfa !important; 
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}
h2, h3 { color: #c4b5fd !important; font-weight: 600 !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #1e1e2e;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #94a3b8;
    border-radius: 8px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #7c3aed !important;
    color: white !important;
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #6d28d9);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.2s;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed);
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(124,58,237,0.4);
}

.stSelectbox label, .stSlider label, .stNumberInput label, .stRadio label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

div[data-testid="stInfo"] {
    background: #1e1e2e;
    border-left: 3px solid #7c3aed;
    border-radius: 8px;
    color: #c4b5fd;
}

div[data-testid="stSuccess"] {
    background: #052e16;
    border-left: 3px solid #22c55e;
    border-radius: 8px;
}

.stat-card {
    background: #1e1e2e;
    border: 1px solid #2d2d3d;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.stat-label { color: #64748b; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; }
.stat-value { color: #a78bfa; font-size: 1.3rem; font-weight: 700; margin-top: 4px; }

.preset-info {
    background: #1e1e2e;
    border: 1px solid #2d2d3d;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-top: 0.5rem;
    font-size: 0.85rem;
    color: #94a3b8;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

PRESETS = {
    "Instagram Post (1:1)"         : (1080, 1080),
    "Instagram Portrait (4:5)"     : (1080, 1350),
    "Instagram Story / Reel (9:16)": (1080, 1920),
    "Twitter / X Post"             : (1200, 675),
    "Facebook Post"                : (1200, 630),
    "LinkedIn Post"                : (1200, 627),
    "YouTube Thumbnail (16:9)"     : (1280, 720),
    "WhatsApp Status (9:16)"       : (1080, 1920),
    "Wallpaper HD (16:9)"          : (1920, 1080),
    "Wallpaper 4K (16:9)"          : (3840, 2160),
    "A4 Print (300 dpi)"           : (2480, 3508),
    "Custom size"                  : None,
}

UPSCALE_METHODS = {
    "Lanczos (Sharpest — recommended)": Image.LANCZOS,
    "Bicubic (Smooth)"               : Image.BICUBIC,
    "Bilinear (Fastest)"             : Image.BILINEAR,
    "Nearest (Pixel-art)"            : Image.NEAREST,
}

def file_size_str(data: bytes) -> str:
    kb = len(data) / 1024
    return f"{kb/1024:.2f} MB" if kb > 1024 else f"{kb:.0f} KB"

def upscale_image(img: Image.Image, scale: float, method) -> Image.Image:
    new_w = int(img.width  * scale)
    new_h = int(img.height * scale)
    return img.resize((new_w, new_h), method)

def fit_to_canvas(img: Image.Image, target_w: int, target_h: int,
                  method, mode: str) -> Image.Image:
    """
    mode = 'fit'  → letterbox (add background bars, keep all pixels)
    mode = 'fill' → crop-to-fill (cover entire canvas, may crop edges)
    mode = 'stretch' → ignore aspect ratio, stretch to exact size
    """
    if mode == "stretch":
        return img.resize((target_w, target_h), method)

    src_ratio = img.width / img.height
    dst_ratio = target_w / target_h

    if mode == "fill":
        # Scale so the smaller dimension fills the canvas, then center-crop
        if src_ratio > dst_ratio:
            new_h = target_h
            new_w = int(new_h * src_ratio)
        else:
            new_w = target_w
            new_h = int(new_w / src_ratio)
        resized = img.resize((new_w, new_h), method)
        left = (new_w - target_w) // 2
        top  = (new_h - target_h) // 2
        return resized.crop((left, top, left + target_w, top + target_h))

    # mode == "fit"  — letterbox
    if src_ratio > dst_ratio:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    else:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    resized = img.resize((new_w, new_h), method)

    canvas = Image.new("RGBA" if img.mode == "RGBA" else "RGB",
                       (target_w, target_h), (0, 0, 0))
    x = (target_w  - new_w) // 2
    y = (target_h - new_h) // 2
    canvas.paste(resized, (x, y))
    return canvas

def preview_thumb(img: Image.Image, max_px: int = 1200) -> Image.Image:
    """Return a downscaled copy safe for st.image preview (never upscales)."""
    if img.width <= max_px and img.height <= max_px:
        return img
    ratio = min(max_px / img.width, max_px / img.height)
    return img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)

def to_bytes(img: Image.Image, fmt: str, quality: int) -> bytes:
    buf = io.BytesIO()
    save_img = img
    if fmt == "JPEG" and save_img.mode in ("RGBA", "P"):
        save_img = save_img.convert("RGB")
    kwargs = {"format": fmt}
    if fmt == "JPEG":
        kwargs["quality"] = quality
        kwargs["optimize"] = True
    elif fmt == "PNG":
        kwargs["optimize"] = True
    save_img.save(buf, **kwargs)
    return buf.getvalue()


# ── UI ─────────────────────────────────────────────────────────────────────────

st.title("🔍 Image Upscaler & Resizer")
st.caption("Upscale blurry images · Fix aspect ratios · Export any size — all local, no API")

uploaded = st.file_uploader(
    "Drop your image here",
    type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
    label_visibility="collapsed",
)

if not uploaded:
    st.info("👆 Upload an image to get started — JPG, PNG, WebP, BMP, TIFF supported")
    st.stop()

# Load image
raw_bytes = uploaded.read()
img = Image.open(io.BytesIO(raw_bytes))
orig_w, orig_h = img.size
orig_mode = img.mode

# ── Info bar ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, label, val in [
    (c1, "Width",  f"{orig_w} px"),
    (c2, "Height", f"{orig_h} px"),
    (c3, "Mode",   orig_mode),
    (c4, "Size",   file_size_str(raw_bytes)),
]:
    col.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{val}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔭 Upscale", "📐 Resize to Preset", "✏️ Custom Size"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — UPSCALE
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Upscale Image")
    st.caption("Enlarges the image while keeping it as sharp as possible")

    col_a, col_b = st.columns(2)
    with col_a:
        scale = st.select_slider(
            "Scale factor",
            options=[1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 8.0],
            value=2.0,
            format_func=lambda x: f"{x}×",
        )
    with col_b:
        method_name = st.selectbox("Upscale method", list(UPSCALE_METHODS.keys()))

    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    st.markdown(f"""
    <div class="preset-info">
    Output will be <strong style="color:#a78bfa">{new_w} × {new_h} px</strong>
    &nbsp;(was {orig_w} × {orig_h} px)
    </div>""", unsafe_allow_html=True)

    out_fmt_1 = st.radio("Save as", ["JPEG", "PNG", "WebP"], horizontal=True, key="fmt1")
    quality_1 = 92
    if out_fmt_1 in ("JPEG", "WebP"):
        quality_1 = st.slider("Quality", 60, 100, 92, key="q1")

    if st.button("🚀 Upscale Now", key="btn_upscale"):
        with st.spinner("Upscaling…"):
            result = upscale_image(img, scale, UPSCALE_METHODS[method_name])
            data = to_bytes(result, out_fmt_1, quality_1)

        st.success(f"✅ Done! Output: {result.width} × {result.height} px · {file_size_str(data)}")
        col_orig, col_out = st.columns(2)
        col_orig.image(preview_thumb(img), caption="Original", use_container_width=True)
        col_out.image(preview_thumb(result), caption=f"Upscaled {scale}× (preview — download for full res)", use_container_width=True)

        ext = out_fmt_1.lower().replace("jpeg", "jpg")
        st.download_button(
            f"⬇️ Download {out_fmt_1}",
            data=data,
            file_name=f"upscaled_{scale}x_{uploaded.name.rsplit('.',1)[0]}.{ext}",
            mime=f"image/{ext}",
        )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRESET RESIZE
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Resize to Platform Preset")
    st.caption("Auto-corrects aspect ratio for social media, print, and wallpapers")

    preset_name = st.selectbox("Choose preset", list(PRESETS.keys()), key="preset")
    target = PRESETS[preset_name]

    if target:
        tw, th = target
        st.markdown(f"""
        <div class="preset-info">
        Target: <strong style="color:#a78bfa">{tw} × {th} px</strong>
        &nbsp;|&nbsp; Aspect ratio: <strong style="color:#a78bfa">{tw/math.gcd(tw,th)}:{th/math.gcd(tw,th)}</strong>
        </div>""", unsafe_allow_html=True)

        fit_mode = st.radio(
            "Fit mode",
            ["fit", "fill", "stretch"],
            horizontal=True,
            format_func=lambda x: {
                "fit":     "🔲 Fit (letterbox — no crop)",
                "fill":    "🖼️ Fill (crop to cover)",
                "stretch": "↔️ Stretch (ignore ratio)",
            }[x],
            key="fitmode",
        )

        method_name2 = st.selectbox("Resize method", list(UPSCALE_METHODS.keys()), key="m2")
        out_fmt_2    = st.radio("Save as", ["JPEG", "PNG", "WebP"], horizontal=True, key="fmt2")
        quality_2    = 92
        if out_fmt_2 in ("JPEG", "WebP"):
            quality_2 = st.slider("Quality", 60, 100, 92, key="q2")

        if st.button("🚀 Resize Now", key="btn_preset"):
            with st.spinner("Resizing…"):
                result2 = fit_to_canvas(img, tw, th, UPSCALE_METHODS[method_name2], fit_mode)
                data2   = to_bytes(result2, out_fmt_2, quality_2)

            st.success(f"✅ Done! Output: {result2.width} × {result2.height} px · {file_size_str(data2)}")
            col_o2, col_r2 = st.columns(2)
            col_o2.image(preview_thumb(img),     caption="Original",       use_container_width=True)
            col_r2.image(preview_thumb(result2), caption=preset_name + " (preview)",      use_container_width=True)

            ext2 = out_fmt_2.lower().replace("jpeg", "jpg")
            safe_name = preset_name.replace(" ", "_").replace("/", "-").replace("(", "").replace(")", "")
            st.download_button(
                f"⬇️ Download {out_fmt_2}",
                data=data2,
                file_name=f"{safe_name}_{uploaded.name.rsplit('.',1)[0]}.{ext2}",
                mime=f"image/{ext2}",
            )
    else:
        st.info("Select a preset above (Custom size is in the next tab)")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — CUSTOM SIZE
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Custom Size")
    st.caption("Enter any width × height you need")

    lock_ratio = st.checkbox("🔒 Lock aspect ratio", value=True)
    col_w, col_h = st.columns(2)

    with col_w:
        custom_w = st.number_input("Width (px)", min_value=1, max_value=20000,
                                   value=orig_w, step=1, key="cw")
    with col_h:
        if lock_ratio:
            locked_h = int(custom_w * orig_h / orig_w)
            st.number_input("Height (px) — locked", value=locked_h,
                            disabled=True, key="ch_locked")
            custom_h = locked_h
        else:
            custom_h = st.number_input("Height (px)", min_value=1, max_value=20000,
                                       value=orig_h, step=1, key="ch")

    fit_mode3    = st.radio(
        "Fit mode",
        ["fit", "fill", "stretch"],
        horizontal=True,
        format_func=lambda x: {
            "fit":     "🔲 Fit (letterbox)",
            "fill":    "🖼️ Fill (crop to cover)",
            "stretch": "↔️ Stretch",
        }[x],
        key="fitmode3",
        disabled=lock_ratio,
    )
    if lock_ratio:
        fit_mode3 = "fit"

    method_name3 = st.selectbox("Resize method", list(UPSCALE_METHODS.keys()), key="m3")
    out_fmt_3    = st.radio("Save as", ["JPEG", "PNG", "WebP"], horizontal=True, key="fmt3")
    quality_3    = 92
    if out_fmt_3 in ("JPEG", "WebP"):
        quality_3 = st.slider("Quality", 60, 100, 92, key="q3")

    if st.button("🚀 Apply Custom Size", key="btn_custom"):
        with st.spinner("Resizing…"):
            result3 = fit_to_canvas(img, custom_w, custom_h,
                                    UPSCALE_METHODS[method_name3], fit_mode3)
            data3   = to_bytes(result3, out_fmt_3, quality_3)

        st.success(f"✅ Done! Output: {result3.width} × {result3.height} px · {file_size_str(data3)}")
        col_o3, col_r3 = st.columns(2)
        col_o3.image(preview_thumb(img),     caption="Original",    use_container_width=True)
        col_r3.image(preview_thumb(result3), caption="Custom size (preview)", use_container_width=True)

        ext3 = out_fmt_3.lower().replace("jpeg", "jpg")
        st.download_button(
            f"⬇️ Download {out_fmt_3}",
            data=data3,
            file_name=f"custom_{custom_w}x{custom_h}_{uploaded.name.rsplit('.',1)[0]}.{ext3}",
            mime=f"image/{ext3}",
        )
