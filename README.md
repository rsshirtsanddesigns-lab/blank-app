# Head Shape Reconstructor (Python + Streamlit)

This project gives you a Python program where you can:
- Upload one or more photos/silhouettes.
- Label each image as **front** or **profile**.
- Extract only the visible head/face **shape outline**.
- Combine multiple images to produce a more stable front-view and profile-view shape.

> Important: this is a **2D shape reconstruction tool** (outline modeling), not a medical-grade 3D craniofacial scanner.

---

## 1) Install

### Step 1.1 — Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 1.2 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## 2) Run the app

### Step 2.1 — Start Streamlit

```bash
streamlit run streamlit_app.py
```

### Step 2.2 — Open the URL shown in your terminal
Usually: `http://localhost:8501`

---

## 3) Use it (one element at a time)

### Step 3.1 — Prepare your photos
Use images where:
- Head is fully visible.
- Background is plain (high contrast works best).
- Lighting is clear.
- Image is not heavily blurred.

### Step 3.2 — Upload images
Use **Upload face/silhouette photos** and add one or many files.

### Step 3.3 — Label each image
For each uploaded image:
- Choose `front` if it is a face-forward view.
- Choose `profile` if it is side-view.

### Step 3.4 — Check detected outline
Each image shows **Detected outline** on a normalized canvas.
If the shape is wrong, adjust:
- **Threshold mode** (`auto` vs `adaptive`)
- **Invert black/white** (toggle on/off)

### Step 3.5 — Review combined models
The app builds:
- **Front-view shape model** from all front-labeled images.
- **Profile-view shape model** from all profile-labeled images.

---

## 4) How combination improves accuracy

When multiple photos are added:
1. Each photo is segmented into a binary silhouette mask.
2. The largest contour (head/face shape) is isolated.
3. Masks are normalized to the same canvas size and centered.
4. All masks of the same label (front/profile) are averaged.
5. A consensus contour is extracted from the average.

This reduces random noise from any single image and gives a more stable outline.

---

## 5) Files

- `streamlit_app.py` — UI and workflow.
- `head_shape_modeler.py` — segmentation, normalization, contour extraction, and combination logic.
- `requirements.txt` — dependencies.

---

## 6) Troubleshooting

- **No visible contour found**
  - Use a tighter crop around the head.
  - Try `Invert black/white`.
  - Try `adaptive` threshold mode.

- **Contour looks jagged or too small**
  - Use higher-resolution images.
  - Ensure silhouette occupies enough of the frame.

- **Front/profile model looks inconsistent**
  - Remove bad-angle photos.
  - Keep camera distance similar across photos.
