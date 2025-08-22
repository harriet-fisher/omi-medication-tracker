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
- Download CSV: `http://YOUR_IP:8000/download-csv`

## ⚙️ Configuration
- `MEDS_CSV_PATH` (optional): path to the CSV file. Defaults to `medications.csv`.
  - Example (Render default via render.yaml): `/opt/render/project/src/medications.csv`
  - The app will auto-create directories and the CSV header if missing.
  
Optional OMI Imports (Conversations/Memories):
- `OMI_APP_ID`: your OMI app id
- `OMI_API_KEY`: your OMI app API key
- `OMI_IMPORT_TYPE` (optional): `conversation` or `memories` (defaults to `conversation`)
- When set, each successful log also creates an OMI conversation or memory entry with the details. See OMI Imports docs: https://docs.omi.me/doc/developer/apps/Import

## 🧩 Files
- `simple_medication_tracker.py` (core CSV logger)
- `simple_server.py` (FastAPI webhook for OMI)
- `simple_requirements.txt` (minimal deps)
- `setup_simple.py` (one-step setup)

## ☁️ Cloud Deployment (Render)

1. Push this repo to GitHub
2. In Render, create a new Web Service from your repo
3. Render reads `render.yaml` and creates a service
4. `MEDS_CSV_PATH` points to `/opt/render/project/src/medications.csv`
5. Start command uses `uvicorn simple_server:app --host 0.0.0.0 --port $PORT`

Notes:
- Free tier: CSV data is ephemeral (lost on redeploy/restart)
- Download CSV regularly via `/download-csv` endpoint
- For persistent storage, consider upgrading to paid Render plan with disks

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
- Free tier: download CSV regularly as data is ephemeral
