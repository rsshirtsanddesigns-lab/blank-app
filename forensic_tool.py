import streamlit as st
import cv2
import numpy as np

# 1. Page Setup
st.set_page_config(layout="wide", page_title="Forensic Explorer")
st.title("🔬 Forensic Microscope: Integrated HG Lens")

# --- Sidebar: Instrument Panel ---
st.sidebar.header("Instrument Panel")
uploaded_file = st.sidebar.file_uploader("Upload Evidence", type=['jpg', 'png', 'tiff'])

# Microscope Controls
lens_size = st.sidebar.slider("Lens Diameter (Pixels)", 50, 400, 200)
mag_power = st.sidebar.slider("Lens Magnification", 1.0, 8.0, 4.0)
hg_intensity = st.sidebar.slider("Lens HG Intensity", 0.0, 10.0, 4.0)

if uploaded_file:
    # Load image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    st.subheader("Original Evidence")
    st.info("Click the image below to center your Enhanced Microscope Lens.")
    
    # 2. TRACK CLICK COORDINATES (Built-in Streamlit)
    # This creates the 'Canvas' you can click on
    from streamlit_image_coordinates import streamlit_image_coordinates
    coords = streamlit_image_coordinates(img_rgb, key="forensic_lens")

    if coords:
        x, y = coords['x'], coords['y']
        
        # 3. THE VIRTUAL LENS MATH (Crop area)
        r = lens_size // 2
        y1, y2 = max(0, y-r), min(img.shape[0], y+r)
        x1, x2 = max(0, x-r), min(img.shape[1], x+r)
        
        # Pull the raw 'Evidence' from under the lens
        lens_crop = img[y1:y2, x1:x2].copy()

        # 4. APPLY HG ONLY INSIDE THE LENS
        if hg_intensity > 0:
            lab = cv2.cvtColor(lens_crop, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=hg_intensity, tileGridSize=(8,8))
            l = clahe.apply(l)
            lens_crop = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

        # 5. ZOOM & DISPLAY
        # Using LANCZOS4 for the professional forensic edge
        lens_zoom = cv2.resize(lens_crop, None, fx=mag_power, fy=mag_power, interpolation=cv2.INTER_LANCZOS4)
        lens_rgb = cv2.cvtColor(lens_zoom, cv2.COLOR_BGR2RGB)

        st.subheader(f"🔬 Microscope View: {mag_power}x Magnification")
        st.image(lens_rgb, caption=f"Coordinate Lock: {x}, {y}", use_container_width=True)

else:
    st.info("Upload an image to start the investigation.")
