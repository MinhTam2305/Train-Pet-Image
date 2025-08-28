This repository contains a Flask app to find similar images.

Lightweight deployment (no TensorFlow)

Quick start (local):

1. Create a venv and install deps
   python -m venv .venv; .\.venv\Scripts\Activate; pip install -r requirements.txt
2. Build lightweight features from images
   python build_features_light.py
3. Run app
   set PORT=5000; gunicorn app:app -b 0.0.0.0:5000

Deploy to a free host

- Heroku: push the repo, set config var LIGHT_MODE=1, and ensure `Procfile` is present.
- Render/Other: Use Dockerfile or native Python build. Build features with `python build_features_light.py` before starting if not built at image time.

Notes

- Original TensorFlow-based mode remains available when LIGHT_MODE=0 and TensorFlow is installed.
- `firebase_download.py` is executed by `/train` route; ensure credentials exist if you use that endpoint.
