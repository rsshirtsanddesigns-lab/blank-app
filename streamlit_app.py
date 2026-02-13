import cv2
import numpy as np
import streamlit as st

from head_shape_modeler import combine_shapes, contour_to_overlay, extract_head_shape

st.set_page_config(page_title="Head Shape Reconstructor", layout="wide")
st.title("🧠 Head Shape Reconstructor (Front + Profile)")
st.caption(
    "Upload one or more photos/silhouettes, label each as front or profile, then build combined shape models."
)

with st.expander("Read this first (accuracy + limits)", expanded=True):
    st.write(
        "This tool estimates **2D head/face outlines** from image silhouettes. It can combine multiple photos "
        "for a more stable shape, but it does **not** generate medically accurate 3D reconstructions. "
        "For best results: plain background, high contrast, full head visible, and consistent camera distance."
    )

uploaded_files = st.file_uploader(
    "Upload face/silhouette photos",
    type=["jpg", "jpeg", "png", "webp", "tif", "tiff"],
    accept_multiple_files=True,
)

col_a, col_b, col_c = st.columns(3)
with col_a:
    threshold_mode = st.selectbox("Threshold mode", options=["auto", "adaptive"], index=0)
with col_b:
    invert_mask = st.checkbox("Invert black/white", value=False)
with col_c:
    canvas_size = st.slider("Normalized canvas size", 256, 1024, 512, step=64)

if uploaded_files:
    front_masks = []
    profile_masks = []

    st.subheader("1) Label each image")
    labels = {}

    for i, file in enumerate(uploaded_files):
        cols = st.columns([2, 1])
        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
        img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img_bgr is None:
            st.warning(f"Could not decode image: {file.name}")
            continue

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        cols[0].image(img_rgb, caption=file.name, use_container_width=True)
        labels[i] = cols[1].selectbox(
            f"View for {file.name}",
            options=["front", "profile"],
            key=f"view_{i}",
        )

        try:
            result = extract_head_shape(
                image_bgr=img_bgr,
                canvas_size=canvas_size,
                threshold_mode=threshold_mode,
                invert=invert_mask,
            )
            overlay = contour_to_overlay(result.normalized_mask, result.normalized_contour, (255, 80, 80))
            cols[1].image(overlay, caption="Detected outline", use_container_width=True)

            if labels[i] == "front":
                front_masks.append(result.normalized_mask)
            else:
                profile_masks.append(result.normalized_mask)

        except ValueError as error:
            cols[1].error(f"{file.name}: {error}")

    st.subheader("2) Build combined models")
    result_cols = st.columns(2)

    with result_cols[0]:
        st.markdown("### Front-view shape model")
        if front_masks:
            front_consensus, front_contour = combine_shapes(front_masks)
            front_overlay = contour_to_overlay(front_consensus, front_contour, (0, 180, 255))
            st.image(front_overlay, caption=f"Combined from {len(front_masks)} front image(s)", use_container_width=True)
        else:
            st.info("No front-view images were labeled.")

    with result_cols[1]:
        st.markdown("### Profile-view shape model")
        if profile_masks:
            profile_consensus, profile_contour = combine_shapes(profile_masks)
            profile_overlay = contour_to_overlay(profile_consensus, profile_contour, (0, 255, 150))
            st.image(
                profile_overlay,
                caption=f"Combined from {len(profile_masks)} profile image(s)",
                use_container_width=True,
            )
        else:
            st.info("No profile-view images were labeled.")

    st.success("Done. Adjust threshold/invert settings if contour quality is poor.")
else:
    st.info("Upload one or more images to begin.")
