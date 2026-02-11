import cv2
import numpy as np
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(layout="wide", page_title="Microscope Histogram Equalizer")
st.title("🔬 Microscope Histogram Equalizer")
st.caption("Upload an image, click anywhere on the canvas, and inspect a magnified view with optional histogram equalization.")

# ---- Sidebar controls ----
st.sidebar.header("Controls")
uploaded_file = st.sidebar.file_uploader(
    "Upload image",
    type=["jpg", "jpeg", "png", "tif", "tiff", "bmp", "webp"],
)

lens_size = st.sidebar.slider("Lens size (px)", min_value=64, max_value=600, value=220, step=4)
zoom_level = st.sidebar.slider("Zoom", min_value=1.0, max_value=12.0, value=4.0, step=0.1)

hist_eq_enabled = st.sidebar.toggle("Histogram equalization", value=True)
clip_limit = st.sidebar.slider(
    "Histogram intensity (CLAHE clip limit)",
    min_value=1.0,
    max_value=12.0,
    value=4.0,
    step=0.1,
    disabled=not hist_eq_enabled,
)
tile_size = st.sidebar.slider(
    "Histogram tile size",
    min_value=4,
    max_value=32,
    value=8,
    step=2,
    disabled=not hist_eq_enabled,
)

snapshot_format = st.sidebar.selectbox("Snapshot format", ["PNG (lossless)", "TIFF (lossless)"])

st.sidebar.markdown("---")
st.sidebar.write("Magnifier is always active once you click the image canvas.")


def decode_uploaded_image(file_obj) -> np.ndarray:
    file_bytes = np.frombuffer(file_obj.read(), dtype=np.uint8)
    image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError("Could not decode uploaded image.")
    return image_bgr


def build_snapshot_bytes(image_bgr: np.ndarray, selected_format: str) -> tuple[bytes, str, str]:
    if selected_format.startswith("PNG"):
        ok, encoded = cv2.imencode(".png", image_bgr, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        if not ok:
            raise ValueError("Failed to encode PNG snapshot.")
        return encoded.tobytes(), "lens_snapshot.png", "image/png"

    ok, encoded = cv2.imencode(".tiff", image_bgr)
    if not ok:
        raise ValueError("Failed to encode TIFF snapshot.")
    return encoded.tobytes(), "lens_snapshot.tiff", "image/tiff"


if uploaded_file is None:
    st.info("Upload an image to begin.")
else:
    try:
        source_bgr = decode_uploaded_image(uploaded_file)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    source_rgb = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2RGB)

    st.subheader("Canvas")
    st.write("Click any point on the image to move the microscope lens.")
    coords = streamlit_image_coordinates(source_rgb, key="microscope_canvas")

    if not coords:
        st.warning("No lens target selected yet. Click on the image canvas.")
        st.stop()

    center_x, center_y = int(coords["x"]), int(coords["y"])

    radius = lens_size // 2
    y1 = max(0, center_y - radius)
    y2 = min(source_bgr.shape[0], center_y + radius)
    x1 = max(0, center_x - radius)
    x2 = min(source_bgr.shape[1], center_x + radius)

    lens_crop = source_bgr[y1:y2, x1:x2].copy()

    if lens_crop.size == 0:
        st.error("Selected region is outside the valid image area.")
        st.stop()

    if hist_eq_enabled:
        lab = cv2.cvtColor(lens_crop, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
        l_channel = clahe.apply(l_channel)
        lens_crop = cv2.cvtColor(cv2.merge((l_channel, a_channel, b_channel)), cv2.COLOR_LAB2BGR)

    lens_zoom = cv2.resize(
        lens_crop,
        dsize=None,
        fx=zoom_level,
        fy=zoom_level,
        interpolation=cv2.INTER_LANCZOS4,
    )

    lens_zoom_rgb = cv2.cvtColor(lens_zoom, cv2.COLOR_BGR2RGB)

    st.subheader("Microscope View")
    st.image(
        lens_zoom_rgb,
        caption=f"Lens @ ({center_x}, {center_y}) • {zoom_level:.1f}x • {lens_size}px",
        use_container_width=True,
    )

    st.write("Snapshot captures exactly what you see in the microscope view at full-resolution output.")
    snapshot_bytes, snapshot_name, snapshot_mime = build_snapshot_bytes(lens_zoom, snapshot_format)
    st.download_button(
        label="📸 Snapshot magnifier view",
        data=snapshot_bytes,
        file_name=snapshot_name,
        mime=snapshot_mime,
        use_container_width=False,
    )
