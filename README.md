# Simple Medication Tracker for Omi Devices

A lightweight medication tracker designed for OMI wearable devices. Stores entries locally in `medications.csv`. No Airtable or external services required.

## 🚀 Quick Start

1. Activate your virtual environment
```bash
source venv/bin/activate
```
2. Install minimal deps
```bash
pip install -r simple_requirements.txt
```
3. Run the simple server (for OMI webhook)
```bash
python simple_server.py
```
4. Set OMI webhook URL to your machine IP:
```
http://YOUR_IP:8000/medication-tracker
```

## 🗣️ Use with OMI
- Logging:
  - Say: "I'm taking medication"
  - Then: e.g. "I'm taking 10mg of aspirin" or "one pill of tylenol"
  - The app extracts medication + dosage and appends to `medications.csv`

- Q&A (natural language):
  - "When was the last time I took aspirin?"
  - "How much gabapentin did I take last?"
  - "What was my last dose of melatonin?"
  - The server answers from the most recent matching CSV entry.

## 🔎 View History
- Open `medications.csv` in a spreadsheet
- Or GET `http://YOUR_IP:8000/medications`

## ⚙️ Configuration
- `MEDS_CSV_PATH` (optional): path to the CSV file. Defaults to `medications.csv`.
  - Example (Render default via render.yaml): `/var/data/medications/medications.csv`
  - The app will auto-create directories and the CSV header if missing.

## 🧩 Files
- `simple_medication_tracker.py` (core CSV logger)
- `simple_server.py` (FastAPI webhook for OMI)
- `simple_requirements.txt` (minimal deps)
- `setup_simple.py` (one-step setup)

## ☁️ Cloud Deployment (Render)

1. Push this repo to GitHub
2. In Render, create a new Web Service from your repo
3. Render will read `render.yaml` and create a service with a persistent disk
4. Environment variable `MEDS_CSV_PATH` is set to `/var/data/medications/medications.csv`
5. Start command uses `uvicorn simple_server:app --host 0.0.0.0 --port $PORT`

Notes:
- The CSV is written to the attached disk so it survives restarts
- You can download the CSV via the `/medications` endpoint output

## 📚 Relevant OMI Docs
- Introduction: https://docs.omi.me/doc/get_started/introduction
- App Intro: https://docs.omi.me/doc/developer/apps/Introduction
- Integrations: https://docs.omi.me/doc/developer/apps/Integrations
- Imports (optional advanced): https://docs.omi.me/doc/developer/apps/Import
- OAuth (optional advanced): https://docs.omi.me/doc/developer/apps/Oauth
- App Setup: https://docs.omi.me/doc/developer/AppSetup
- Submitting Apps: https://docs.omi.me/doc/developer/apps/Submitting

These docs explain creating an app, enabling External Integration, and pointing your device to the webhook.

## ✅ Notes
- Data is local to this machine in `medications.csv`
- No cloud keys needed
- Keep your laptop and OMI device on the same network for webhooks
