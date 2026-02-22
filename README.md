# 📷 Photo Clarity Viewer

A high-performance **in-browser** photo viewing app for clarity, contrast, and
denoise inspection — not a forensic workflow tool.

## Features

| Feature | Details |
|---|---|
| **Square magnifier lens** | Cursor-follow, adjustable size & zoom |
| **Lock / freeze lens** | Freeze lens at any position; pan the main image independently while locked |
| **Main zoom & fit controls** | Fit-to-view, 1:1, smooth scroll-wheel zoom |
| **CLAHE** | Tile-based histogram equalization with 7 ready-made presets + fine-tune Clip Limit & Tile Grid |
| **Levels** | Black-point, Mid-point (gamma), White-point sweep |
| **Denoise** | Separable Gaussian blur, strength 0–10, tuned for pleasant viewing |
| **PCA Channels** | PC1 / PC2 / PC3 grayscale projections with variance % readout |
| **UI controls** | ▼ / ▲ buttons only — no sliders |
| **Performance** | `requestAnimationFrame` render loop; image processing done off the hot path via dirty-flag caching |

---

## Option A — Open directly in a browser (recommended, zero install)

1. Double-click **`photo_viewer.html`** in Windows Explorer, or drag it onto
   any modern browser (Chrome, Edge, Firefox).
2. Click / drop an image.  That's it.

---

## Option B — Run with Streamlit

### Prerequisites
* Python 3.9 or newer ([python.org](https://www.python.org/downloads/))

### Install dependencies

**cmd.exe (recommended on Windows — avoids PowerShell execution-policy issues)**
```cmd
python -m pip install -r requirements.txt
```

**PowerShell (if you see "running scripts is disabled on this system")**

Choose one of:
```powershell
# Option 1 – run as Administrator once, then run normally afterwards
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Option 2 – bypass for this session only (no admin rights needed)
powershell -ExecutionPolicy Bypass -Command "python -m pip install -r requirements.txt"
```

Or just switch to cmd.exe:
```powershell
cmd /c "python -m pip install -r requirements.txt"
```

### Start the app

```cmd
python -m streamlit run streamlit_app.py
```

Streamlit will open a browser tab automatically.  If it does not, navigate to
`http://localhost:8501`.

> **Tip:** For the best experience (full-screen, no iframe restrictions) use
> **Option A** and open `photo_viewer.html` directly.

---

## Keyboard shortcuts (viewer)

| Key | Action |
|---|---|
| `L` | Lock / unlock magnifier lens |
| `F` | Fit image to window |
| `1` | 1:1 pixel zoom |
| `+` / `-` | Zoom in / out |
| Scroll wheel | Zoom (cursor-centred) |
| Alt + drag | Pan image |
| Right-click + drag | Pan image |
| Drag (lens locked) | Pan image |

