#!/usr/bin/env python3
"""
Simple Medication Tracker Server for Omi Devices
A lightweight FastAPI server that stores medication data locally in CSV format.
Much simpler than the original - no Airtable required!
"""

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import logging
from datetime import datetime
import os

# Import our simple tracker
from simple_medication_tracker import SimpleMedicationTracker

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Simple Medication Tracker",
    description="A lightweight medication tracking app for Omi devices - stores data locally in CSV",
    version="2.0.0"
)

# Initialize the tracker
tracker = SimpleMedicationTracker()

# Store session states (in production, use Redis or database)
session_states = {}

class TranscriptData(BaseModel):
    segments: List[Dict]
    session_id: Optional[str] = None

@app.post("/medication-tracker")
async def process_medication_transcript(
    session_id: str = Query(...),
    uid: str = Query(...),
    transcript_data: TranscriptData = None
):
    """Process real-time transcript for medication tracking - OMI Integration Endpoint"""
    
    if not transcript_data or not transcript_data.segments:
        return {"status": "no_data"}
    
    # Get the latest transcript segment
    latest_segment = transcript_data.segments[-1] if transcript_data.segments else {}
    text = latest_segment.get("text", "").lower()
    
    # Initialize session state if needed
    if session_id not in session_states:
        session_states[session_id] = {
            "waiting_for_medication": False,
            "last_processed": "",
            "trigger_time": None
        }
    
    session_state = session_states[session_id]
    
    # Enhanced trigger phrases - more natural for older adults
    trigger_phrases = [
        "i am about to take some medication",
        "i'm about to take some medication", 
        "about to take medication",
        "taking medication now",
        "i am taking medication",
        "i need to take my medication",
        "time to take my medication",
        "remind me to take my medication",
        "i'm taking my medicine",
        "medicine time",
        "pill time",
        "i'm about to take my pills",
        "time for my medication",
        "i'm going to take my medication"
    ]
    
    # First: see if this is a question we can answer from CSV
    qa = tracker.answer_question(text)
    if qa:
        return qa

    # Then: check for trigger phrase
    if any(phrase in text for phrase in trigger_phrases):
        session_state["waiting_for_medication"] = True
        session_state["last_processed"] = text
        session_state["trigger_time"] = datetime.now()
        logger.info(f"🎯 Trigger detected for user {uid}. Waiting for medication details...")
        return {
            "status": "triggered", 
            "message": "Okay, what medication are you taking?",
            "response": "I'm listening for your medication details. Please tell me what medication and dosage you're taking."
        }
    
    # If we're waiting for medication details
    if session_state["waiting_for_medication"]:
        # Avoid processing the same text twice
        if text != session_state["last_processed"]:
            medication_info = tracker.extract_medication_info(text)
            
            if medication_info:
                # Add to CSV
                success = tracker.add_medication(medication_info)
                
                # Reset session state
                session_state["waiting_for_medication"] = False
                session_state["last_processed"] = text
                
                if success:
                    logger.info(f"✅ Medication logged successfully: {medication_info}")
                    return {
                        "status": "logged",
                        "message": f"Perfect! I've logged {medication_info['medication']} - {medication_info['dosage']} at {medication_info['timestamp']}",
                        "data": medication_info,
                        "response": f"Great! I've recorded that you took {medication_info['medication']} {medication_info['dosage']} at {medication_info['timestamp']}. Your medication has been logged."
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Sorry, I couldn't save that to your medication log. Please try again.",
                        "response": "I'm sorry, but I couldn't save your medication information right now. Please try again in a moment."
                    }
            else:
                # If we've been waiting too long, reset the session
                if session_state["trigger_time"] and (datetime.now() - session_state["trigger_time"]).seconds > 30:
                    session_state["waiting_for_medication"] = False
                    session_state["trigger_time"] = None
                    return {
                        "status": "timeout",
                        "message": "Session timed out. Please try again.",
                        "response": "I didn't catch the medication details. Please say 'I'm taking medication' again and then tell me what you're taking."
                    }
    
    return {"status": "listening"}

@app.get("/setup-status")
async def setup_status(uid: str = Query(...)):
    """Check if the app is set up for this user - OMI Integration Endpoint"""
    return {"is_setup_completed": True}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Simple Medication Tracker",
        "version": "2.0.0",
        "storage": "Local CSV",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/medications")
async def get_medications(uid: str = Query(...), days: int = 7):
    """Get medication history from CSV"""
    try:
        medications = tracker.get_recent_medications(days)
        return {"medications": medications}
    except Exception as e:
        logger.error(f"❌ Error in get_medications: {e}")
        return {"error": "Internal server error"}

@app.get("/")
async def root():
    """Root endpoint with app information"""
    return {
        "app": "Simple Medication Tracker",
        "description": "A lightweight medication tracking app for Omi devices - stores data locally in CSV",
        "version": "2.0.0",
        "storage": "Local CSV file (medications.csv)",
        "endpoints": {
            "medication-tracker": "POST - Process medication transcripts",
            "setup-status": "GET - Check app setup status",
            "health": "GET - Health check",
            "medications": "GET - Get medication history"
        },
        "setup_instructions": "No external services required! Just run this server and point your Omi device to it."
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Simple Medication Tracker Server...")
    logger.info("📊 Storage: Local CSV file (medications.csv)")
    logger.info("🌐 Server: http://localhost:8000")
    logger.info("📱 Omi Integration: Set webhook to http://your-ip:8000/medication-tracker")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
