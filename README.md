# Crypto AI Prediction Dashboard

This project is a Flask web app that serves an AI crypto prediction dashboard and exposes:

- `GET /` → dashboard UI
- `POST /predict` → prediction JSON response

It requires the model file `crypto_ai_brain.keras` in the app root (same folder as `server.py`).

## Runtime

- Python `3.10` or `3.11` (configured as `3.11.9` in `runtime.txt`)

## Deploy files in this repo

- `requirements.txt` for dependency installation
- `Procfile` with production start command:
  - `web: gunicorn --bind 0.0.0.0:${PORT:-5000} server:app`
- `runtime.txt` for Python version

## Local run

```bash
pip install -r requirements.txt
python server.py
```

The app will start on `0.0.0.0:${PORT:-5000}`.

## Deploy (Render/Railway/Fly.io/VPS)

Use these settings on your host:

- **Build command**: `pip install -r requirements.txt`
- **Start command**: `gunicorn --bind 0.0.0.0:$PORT server:app`

Also ensure:

- Outbound internet access is enabled (for `yfinance` data pulls).
- The `crypto_ai_brain.keras` file is present in the deployed app root.
- Instance memory is sufficient for TensorFlow model loading.

## Post-deploy validation

1. Open `/` and confirm dashboard loads.
2. Send a prediction request:

```bash
curl -X POST "$APP_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"coin":"BTC-USD"}'
```

You should receive JSON containing `current_price`, `predicted_price`, and `trend`.
