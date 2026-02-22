import streamlit as st
import streamlit.components.v1 as components
import pathlib

st.set_page_config(layout="wide", page_title="Photo Clarity Viewer")

# Serve the self-contained HTML photo viewer.
# For the best experience open photo_viewer.html directly in a browser.
_html = pathlib.Path(__file__).parent / "photo_viewer.html"
if _html.exists():
    components.html(_html.read_text(encoding="utf-8"), height=820, scrolling=False)
else:
    st.error(
        "photo_viewer.html not found. "
        "Please ensure it is in the same directory as streamlit_app.py."
    )
    st.info(
        "Alternatively, open **photo_viewer.html** directly in your browser "
        "for the full-screen experience."
    )

