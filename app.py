import io
import zipfile
import numpy as np
import streamlit as st
from PIL import Image, ImageFilter

st.set_page_config(page_title="Image Pixel", layout="wide")
st.title("Image Pixel and Dimension Aligner")

st.caption("Manual upload. Output is always square (1:1) and never larger than 900x900. No upscaling. Contact Pratik Adsare for any doubts")

def corner_color(img: Image.Image, patch: int = 25):
    arr = np.array(img.convert("RGB"))
    h, w, _ = arr.shape
    p = max(1, min(patch, h, w))

    corners = [
        arr[0:p, 0:p],
        arr[0:p, w-p:w],
        arr[h-p:h, 0:p],
        arr[h-p:h, w-p:w],
    ]
    flat = np.concatenate([c.reshape(-1, 3) for c in corners], axis=0)
    avg = np.mean(flat, axis=0)
    return tuple(int(x) for x in avg)

def make_square(img: Image.Image, max_out: int = 900, mode: str = "Auto"):
    img = img.convert("RGBA")
    w, h = img.size
    max_side = max(w, h)
    out_side = min(max_side, max_out)  # never upscale

    if mode == "White":
        bg = Image.new("RGBA", (max_side, max_side), (255, 255, 255, 255))
    elif mode == "Blur":
        base = img.convert("RGB")
        stretched = base.resize((max_side, max_side), Image.Resampling.LANCZOS)
        stretched = stretched.filter(ImageFilter.GaussianBlur(radius=18))
        bg = stretched.convert("RGBA")
    else:
        c = corner_color(img)
        bg = Image.new("RGBA", (max_side, max_side), (*c, 255))

    x = (max_side - w) // 2
    y = (max_side - h) // 2
    bg.paste(img, (x, y), img)

    if max_side != out_side:
        bg = bg.resize((out_side, out_side), Image.Resampling.LANCZOS)

    return bg

with st.sidebar:
    st.header("Settings")
    mode = st.selectbox("Background", ["Auto", "White", "Blur"], index=0)
    max_out = st.number_input("Max size (px)", min_value=200, max_value=900, value=900, step=10)
    jpg_quality = st.slider("JPG quality", 70, 100, 95, 1)

files = st.file_uploader("Upload images", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

if files:
    st.write(f"Files selected: {len(files)}")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            try:
                img = Image.open(f)
                out = make_square(img, int(max_out), mode).convert("RGB")

                out_bytes = io.BytesIO()
                out.save(out_bytes, format="JPEG", quality=int(jpg_quality), optimize=True)

                base_name = f.name.rsplit(".", 1)[0]
                out_name = f"{base_name}_1x1_max{int(max_out)}.jpg"
                zf.writestr(out_name, out_bytes.getvalue())
            except Exception as e:
                zf.writestr(f"{f.name}_ERROR.txt", f"{type(e).__name__}: {e}")

    st.download_button(
        "Download ZIP",
        data=zip_buffer.getvalue(),
        file_name=f"square_images_1x1_max{int(max_out)}.zip",
        mime="application/zip"
    )
else:
    st.info("Upload one or more images to start.")
