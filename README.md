# Microscope Histogram Equalizer (Pure HTML Canvas)

This project now includes a **plain HTML** microscope viewer with:
- image upload,
- click-to-position microscope lens,
- zoom control,
- lens size control,
- histogram equalization **ON/OFF toggle**,
- intensity control,
- high-quality snapshot export of the magnifier view.

## File
- `microscope.html`

## Step-by-step instructions

1. Open a terminal in this folder.
2. Start a simple local server:

   ```bash
   python -m http.server 8000
   ```

3. Open your browser to:

   ```
   http://127.0.0.1:8000/microscope.html
   ```

4. Click **Upload image** and select a photo.
5. Click anywhere on the left canvas to place the microscope target.
6. Adjust:
   - **Lens size** (how much area is sampled),
   - **Zoom** (magnification),
   - **Histogram equalization** ON/OFF,
   - **Intensity blend** (how strong equalization is).
7. Pick a **Snapshot size** and click **📸 Snapshot magnifier**.

The snapshot is saved as **PNG (lossless)** for high quality.

## Notes
- No UI framework used (just HTML/CSS/JavaScript).
- Histogram equalization only affects the magnifier content when the toggle is ON.
- Magnifier itself is always active after selecting a point.
