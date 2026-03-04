# 1:1 Image Square Tool (Streamlit)

This app makes uploaded images square (1:1) by padding (no crop) and ensures output is <= 900px.

## Why this version
Some Streamlit Community Cloud deployments currently build with Python 3.13 by default.
This requirements set uses versions that support Python 3.13 (Streamlit + Pillow 11 + NumPy 2.3).

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
