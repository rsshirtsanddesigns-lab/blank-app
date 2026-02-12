import base64
from pathlib import Path

import cv2
import numpy as np
import streamlit as st


st.set_page_config(layout="wide", page_title="Pro Histogram Equalizer Studio")
st.title("🧪 Pro Histogram Equalizer Studio")
st.caption(
    "Interactive forensic canvas with live histogram equalization, microscope lens, zoom, resize, and drag controls."
)

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"])
use_demo = st.toggle("Use built-in demo image", value=uploaded is None)


def demo_image_bytes() -> bytes:
    canvas = np.zeros((720, 1080, 3), dtype=np.uint8)
    for y in range(canvas.shape[0]):
        canvas[y, :, 0] = np.clip(40 + y // 4, 0, 255)
        canvas[y, :, 1] = np.clip(30 + y // 5, 0, 255)
        canvas[y, :, 2] = np.clip(90 + y // 3, 0, 255)

    for x in range(0, canvas.shape[1], 40):
        color = (x % 255, 160, 220)
        cv2.line(canvas, (x, 0), (x, canvas.shape[0]), color, 1)
    for y in range(0, canvas.shape[0], 40):
        color = (220, y % 255, 120)
        cv2.line(canvas, (0, y), (canvas.shape[1], y), color, 1)

    cv2.circle(canvas, (540, 360), 200, (255, 255, 255), 6)
    cv2.putText(canvas, "Forensic Demo Subject", (290, 660), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

    ok, encoded = cv2.imencode(".png", canvas)
    return encoded.tobytes() if ok else b""


def image_to_data_url(raw_bytes: bytes, suffix: str) -> str:
    encoded = base64.b64encode(raw_bytes).decode("utf-8")
    ext = suffix.lstrip(".").lower()
    mime = "image/png"
    if ext in {"jpg", "jpeg"}:
        mime = "image/jpeg"
    elif ext == "bmp":
        mime = "image/bmp"
    elif ext in {"tif", "tiff"}:
        mime = "image/tiff"
    return f"data:{mime};base64,{encoded}"


if uploaded:
    image_data_url = image_to_data_url(uploaded.getvalue(), Path(uploaded.name).suffix)
elif use_demo:
    image_data_url = image_to_data_url(demo_image_bytes(), ".png")
else:
    st.info("Upload an image (or enable demo image) to start.")
    st.stop()

ui = f"""
<div style="font-family: Inter, system-ui, sans-serif; color: #f5f7fb;">
  <style>
    .control-panel {{
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(4, minmax(180px, 1fr));
      margin-bottom: 12px;
    }}
    .card {{
      background: #0f1523;
      border: 1px solid #2b3750;
      border-radius: 10px;
      padding: 10px;
    }}
    .title {{
      font-size: 12px;
      color: #9eb2d8;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .value {{
      font-size: 20px;
      font-weight: 700;
      margin: 0 8px;
      min-width: 64px;
      text-align: center;
      display: inline-block;
    }}
    .btn {{
      border: 1px solid #4d628b;
      background: #17243b;
      color: #e8eefc;
      border-radius: 8px;
      padding: 5px 10px;
      cursor: pointer;
      font-weight: 700;
    }}
    .btn:hover {{ background: #1e3152; }}
    .switch {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: #d5e0f8;
      font-size: 14px;
      margin-top: 8px;
    }}
    .stage {{
      border: 1px solid #2b3750;
      border-radius: 12px;
      background: #060b15;
      position: relative;
      overflow: hidden;
      user-select: none;
      touch-action: none;
    }}
    #mainCanvas {{
      display: block;
      width: 100%;
      height: min(72vh, 820px);
      cursor: grab;
      background: #050912;
    }}
    .hint {{
      margin-top: 8px;
      font-size: 13px;
      color: #aac0ec;
      opacity: 0.9;
    }}
  </style>

  <div class="control-panel">
    <div class="card">
      <div class="title">Microscope Size</div>
      <button class="btn" id="lensSizeMinus">-</button>
      <span class="value" id="lensSizeValue">220</span>
      <button class="btn" id="lensSizePlus">+</button>
    </div>
    <div class="card">
      <div class="title">Microscope Zoom</div>
      <button class="btn" id="lensZoomMinus">-</button>
      <span class="value" id="lensZoomValue">3.0x</span>
      <button class="btn" id="lensZoomPlus">+</button>
    </div>
    <div class="card">
      <div class="title">Histogram Equalizer</div>
      <button class="btn" id="eqMinus">-</button>
      <span class="value" id="eqValue">0.45</span>
      <button class="btn" id="eqPlus">+</button>
    </div>
    <div class="card">
      <div class="title">Picture Size</div>
      <button class="btn" id="imgScaleMinus">-</button>
      <span class="value" id="imgScaleValue">1.00x</span>
      <button class="btn" id="imgScalePlus">+</button>
      <label class="switch"><input type="checkbox" id="lockLens"/> Lock microscope (drag photo)</label>
    </div>
  </div>

  <div class="stage">
    <canvas id="mainCanvas"></canvas>
  </div>
  <div class="hint">Move cursor to inspect. Drag to move image. Mouse wheel = scene zoom. Lock microscope to pin lens while panning image.</div>
</div>

<script>
(() => {{
  const img = new Image();
  img.src = "{image_data_url}";

  const canvas = document.getElementById("mainCanvas");
  const ctx = canvas.getContext("2d", {{ willReadFrequently: true }});

  const state = {{
    lensSize: 220,
    lensZoom: 3,
    eqStrength: 0.45,
    imgScale: 1,
    sceneZoom: 1,
    offsetX: 0,
    offsetY: 0,
    lensX: 240,
    lensY: 200,
    dragging: false,
    lastX: 0,
    lastY: 0,
    lockLens: false,
    pointerInside: false,
  }};

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  function fitCanvas() {{
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.floor(rect.width * dpr);
    canvas.height = Math.floor(rect.height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  }}

  function drawBackground() {{
    const w = canvas.clientWidth, h = canvas.clientHeight;
    ctx.fillStyle = "#060b15";
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = "rgba(106, 131, 178, 0.22)";
    for (let x = 0; x < w; x += 40) {{
      ctx.beginPath();
      ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }}
    for (let y = 0; y < h; y += 40) {{
      ctx.beginPath();
      ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }}
  }}

  function draw() {{
    if (!img.complete) return;
    const w = canvas.clientWidth, h = canvas.clientHeight;
    drawBackground();

    const scaledW = img.width * state.imgScale * state.sceneZoom;
    const scaledH = img.height * state.imgScale * state.sceneZoom;
    const drawX = (w - scaledW) / 2 + state.offsetX;
    const drawY = (h - scaledH) / 2 + state.offsetY;

    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(img, drawX, drawY, scaledW, scaledH);

    if (!state.pointerInside) return;

    const radius = state.lensSize / 2;
    const lensX = clamp(state.lensX, radius, w - radius);
    const lensY = clamp(state.lensY, radius, h - radius);

    ctx.save();
    ctx.beginPath();
    ctx.arc(lensX, lensY, radius, 0, Math.PI * 2);
    ctx.clip();

    const srcW = state.lensSize / state.lensZoom;
    const srcH = state.lensSize / state.lensZoom;
    const srcX = ((lensX - drawX) / scaledW) * img.width - srcW / 2;
    const srcY = ((lensY - drawY) / scaledH) * img.height - srcH / 2;

    const safeSrcX = clamp(srcX, 0, Math.max(0, img.width - srcW));
    const safeSrcY = clamp(srcY, 0, Math.max(0, img.height - srcH));

    const temp = document.createElement("canvas");
    temp.width = Math.max(2, Math.floor(state.lensSize));
    temp.height = Math.max(2, Math.floor(state.lensSize));
    const tctx = temp.getContext("2d", {{ willReadFrequently: true }});
    tctx.drawImage(
      img,
      safeSrcX,
      safeSrcY,
      srcW,
      srcH,
      0,
      0,
      temp.width,
      temp.height,
    );

    if (state.eqStrength > 0.001) applyHistogramEqualization(tctx, temp.width, temp.height, state.eqStrength);

    ctx.drawImage(temp, lensX - radius, lensY - radius, state.lensSize, state.lensSize);
    ctx.restore();

    ctx.beginPath();
    ctx.arc(lensX, lensY, radius, 0, Math.PI * 2);
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#f1f6ff";
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(lensX, lensY, radius + 5, 0, Math.PI * 2);
    ctx.lineWidth = 1;
    ctx.strokeStyle = "rgba(78, 152, 255, 0.85)";
    ctx.stroke();
  }}

  function applyHistogramEqualization(context, width, height, strength) {{
    const frame = context.getImageData(0, 0, width, height);
    const data = frame.data;
    const hist = new Uint32Array(256);
    const lum = new Uint8Array(width * height);

    for (let i = 0, p = 0; i < data.length; i += 4, p++) {{
      const y = Math.round(0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2]);
      lum[p] = y;
      hist[y]++;
    }}

    let cdf = 0;
    const total = width * height;
    const cdfMap = new Uint8Array(256);
    let firstNonZero = -1;
    for (let i = 0; i < 256; i++) {{
      if (hist[i] > 0 && firstNonZero === -1) firstNonZero = i;
      cdf += hist[i];
      cdfMap[i] = Math.round((cdf / total) * 255);
    }}

    const cdfMin = firstNonZero >= 0 ? cdfMap[firstNonZero] : 0;

    for (let i = 0, p = 0; i < data.length; i += 4, p++) {{
      const oldY = lum[p];
      const mapped = clamp(Math.round(((cdfMap[oldY] - cdfMin) / (255 - cdfMin || 1)) * 255), 0, 255);
      const targetY = oldY + (mapped - oldY) * strength;
      const factor = targetY / (oldY || 1);

      data[i] = clamp(Math.round(data[i] * factor), 0, 255);
      data[i + 1] = clamp(Math.round(data[i + 1] * factor), 0, 255);
      data[i + 2] = clamp(Math.round(data[i + 2] * factor), 0, 255);
    }}

    context.putImageData(frame, 0, 0);
  }}

  function bindAdjusters() {{
    const adjust = (idMinus, idPlus, key, step, minV, maxV, fmt) => {{
      const minus = document.getElementById(idMinus);
      const plus = document.getElementById(idPlus);
      const val = document.getElementById(key + "Value");

      function refresh() {{
        val.textContent = fmt(state[key]);
        draw();
      }}

      minus.onclick = () => {{ state[key] = clamp(state[key] - step, minV, maxV); refresh(); }};
      plus.onclick = () => {{ state[key] = clamp(state[key] + step, minV, maxV); refresh(); }};
      refresh();
    }};

    adjust("lensSizeMinus", "lensSizePlus", "lensSize", 10, 80, 500, (v) => String(Math.round(v)));
    adjust("lensZoomMinus", "lensZoomPlus", "lensZoom", 0.2, 1.2, 12, (v) => v.toFixed(1) + "x");
    adjust("eqMinus", "eqPlus", "eqStrength", 0.05, 0, 1, (v) => v.toFixed(2));
    adjust("imgScaleMinus", "imgScalePlus", "imgScale", 0.05, 0.2, 5, (v) => v.toFixed(2) + "x");

    const lock = document.getElementById("lockLens");
    lock.onchange = () => {{ state.lockLens = lock.checked; }};
  }}

  canvas.addEventListener("mousemove", (e) => {{
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (state.dragging) {{
      state.offsetX += x - state.lastX;
      state.offsetY += y - state.lastY;
      state.lastX = x;
      state.lastY = y;
      draw();
      return;
    }}

    if (!state.lockLens) {{
      state.lensX = x;
      state.lensY = y;
    }}
    draw();
  }});

  canvas.addEventListener("mousedown", (e) => {{
    const rect = canvas.getBoundingClientRect();
    state.dragging = true;
    state.lastX = e.clientX - rect.left;
    state.lastY = e.clientY - rect.top;
    canvas.style.cursor = "grabbing";
  }});

  window.addEventListener("mouseup", () => {{
    state.dragging = false;
    canvas.style.cursor = "grab";
  }});

  canvas.addEventListener("mouseenter", () => {{ state.pointerInside = true; draw(); }});
  canvas.addEventListener("mouseleave", () => {{ state.pointerInside = false; draw(); }});

  canvas.addEventListener("wheel", (e) => {{
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.05 : 0.05;
    state.sceneZoom = clamp(state.sceneZoom + delta, 0.2, 8);
    draw();
  }}, {{ passive: false }});

  window.addEventListener("resize", fitCanvas);

  bindAdjusters();
  img.onload = () => {{
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    state.offsetX = 0;
    state.offsetY = 0;
    state.lensX = w * 0.5;
    state.lensY = h * 0.5;
    fitCanvas();
  }};
}})();
</script>
"""

st.components.v1.html(ui, height=980, scrolling=False)
