#!/usr/bin/env python3
"""Localhost-only editor backend for the FoodStock scene editor."""
import hashlib
import json
import os
import subprocess
import tempfile
from functools import wraps
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
PHOTO_DIR = DATA_DIR / "photos"
OVERLAY_DIR = DATA_DIR / "overlays"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}

app = Flask(__name__, static_folder=None)


def check_auth():
    username = os.environ.get("FOODSTOCK_EDITOR_USER")
    password = os.environ.get("FOODSTOCK_EDITOR_PASSWORD")
    if not username and not password:
        return True
    auth = request.authorization
    return bool(auth and auth.username == username and auth.password == password)


def require_auth(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if check_auth():
            return fn(*args, **kwargs)
        return Response(
            "Authentication required\n",
            401,
            {"WWW-Authenticate": 'Basic realm="FoodStock Editor"'},
        )

    return wrapped


def atomic_write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


@app.get("/")
@require_auth
def editor():
    return send_from_directory(ROOT, "editor-pro.html")


@app.get("/data/<path:filename>")
@require_auth
def data_file(filename):
    return send_from_directory(DATA_DIR, filename)


@app.get("/fonts/<path:filename>")
@require_auth
def font_file(filename):
    return send_from_directory(ROOT / "fonts", filename)


@app.post("/save")
@require_auth
def save():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Expected JSON object"), 400
    restaurants = payload.get("restaurants")
    brand = payload.get("brand")
    if not isinstance(restaurants, list) or not isinstance(brand, dict):
        return jsonify(error="Expected { restaurants: [...], brand: {...} }"), 400

    atomic_write_json(DATA_DIR / "restaurants.json", restaurants)
    atomic_write_json(DATA_DIR / "brand-config.json", brand)
    return jsonify(ok=True)


@app.post("/upload")
@require_auth
def upload():
    upload_type = request.form.get("type")
    file = request.files.get("file")
    if upload_type not in {"photo", "overlay"}:
        return jsonify(error='type must be "photo" or "overlay"'), 400
    if file is None or not file.filename:
        return jsonify(error="Missing upload file"), 400

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify(error=f"Unsupported extension: {ext or '(none)'}"), 400

    blob = file.read()
    digest = hashlib.sha256(blob).hexdigest()[:16]
    safe_name = f"{upload_type}-{digest}{ext}"
    target_dir = PHOTO_DIR if upload_type == "photo" else OVERLAY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / safe_name
    target.write_bytes(blob)

    rel_dir = "photos" if upload_type == "photo" else "overlays"
    return jsonify(ok=True, path=f"{rel_dir}/{safe_name}")


@app.post("/regenerate")
@require_auth
def regenerate():
    result = subprocess.run(
        ["python3", "generate.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode != 0:
        return jsonify(ok=False, stdout=result.stdout, error=result.stderr), 500
    return jsonify(ok=True, stdout=result.stdout)


if __name__ == "__main__":
    host = os.environ.get("FOODSTOCK_EDITOR_HOST", "127.0.0.1")
    port = int(os.environ.get("FOODSTOCK_EDITOR_PORT", "8090"))
    app.run(host=host, port=port)
