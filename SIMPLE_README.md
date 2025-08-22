# Simple Medication Tracker for Omi Devices

A lightweight medication tracking app that stores data locally in CSV format. **No external services required!**

## 🎯 What's Different

- ✅ **No Airtable required** - stores data locally in CSV
- ✅ **No complex setup** - just run the script
- ✅ **No server management** - simple local storage
- ✅ **Easy to use** - perfect for your mom's needs

## 🚀 Quick Start

### 1. Activate Your Virtual Environment
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 2. Run the Setup Script
```bash
python setup_simple.py
```

### 3. Test the Tracker
```bash
python simple_medication_tracker.py
```

### 4. Run the Server (for Omi integration)
```bash
python simple_server.py
```

## 📱 Omi Device Setup

1. Open the Omi mobile app
2. Go to Settings → Developer Mode (enable if needed)
3. Navigate to Developer Settings
4. Set your endpoint URL to: `http://YOUR_IP:8000/medication-tracker`
5. Replace `YOUR_IP` with your computer's IP address

## 🗣️ How to Use

### Trigger Phrases
Say any of these to start logging:
- "I'm taking medication"
- "Time to take my medication"
- "Medicine time"
- "I need to take my medication"

### Medication Examples
Then tell the device what you're taking:
- "I'm taking 10mg of aspirin"
- "One pill of tylenol"
- "Two tablets of ibuprofen"
- "500mg acetaminophen"

## 📊 Viewing Your Data

Your medication data is stored in `medications.csv`. You can:
- Open it in Excel, Google Sheets, or any spreadsheet app
- View it online at: `http://YOUR_IP:8000/medications`
- The file contains: Date, Time, Medication, Dosage, Notes

## 🔧 Troubleshooting

### Server Won't Start
- Make sure your virtual environment is activated
- Check that port 8000 isn't being used by another app
- Try: `python simple_server.py`

### Omi Device Can't Connect
- Make sure your computer and Omi device are on the same WiFi network
- Check your computer's firewall settings
- Verify the IP address is correct

### Medication Not Recognized
- Try different phrasing
- Speak clearly and slowly
- Check the server logs for errors

## 📁 Files Explained

- `simple_medication_tracker.py` - Core medication tracking logic
- `simple_server.py` - FastAPI server for Omi integration
- `simple_requirements.txt` - Minimal dependencies
- `setup_simple.py` - Easy setup script
- `medications.csv` - Your medication data (created automatically)

## 🎉 That's It!

Your mom can now:
1. Say "I'm taking medication" to her Omi device
2. Tell it what medication and dosage
3. Get confirmation that it was logged
4. View her medication history anytime

No complex setup, no external services, just simple local tracking! 🎯
