#!/usr/bin/env python3
"""
Simple Medication Tracker for Omi Devices
A lightweight medication tracking app that stores data locally in CSV format.
No server required - just run this script directly!
"""

import csv
import os
from datetime import datetime
import re
from typing import Dict, Optional, List
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMedicationTracker:
    def __init__(self, csv_file: str = None):
        """Initialize the medication tracker with a CSV file
        If not provided, uses MEDS_CSV_PATH env var or defaults to medications.csv
        """
        configured_path = csv_file or os.getenv("MEDS_CSV_PATH", "medications.csv")
        self.csv_file = configured_path
        self.setup_csv_file()
    
    def setup_csv_file(self):
        """Create CSV file with headers if it doesn't exist"""
        # Ensure directory exists if a directory is provided
        directory = os.path.dirname(os.path.abspath(self.csv_file))
        try:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
        except PermissionError:
            # Fallback to a writable project-local directory
            fallback_dir = os.path.join(os.getcwd(), 'data')
            os.makedirs(fallback_dir, exist_ok=True)
            logger.warning(f"⚠️  No permission to create '{directory}'. Falling back to '{fallback_dir}'.")
            self.csv_file = os.path.join(fallback_dir, 'medications.csv')
            directory = fallback_dir
        
        if not os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Date', 'Time', 'Medication', 'Dosage', 'Notes'])
                logger.info(f"✅ Created new medication log: {self.csv_file}")
            except (PermissionError, FileNotFoundError):
                # Final fallback to project-local data path
                fallback_dir = os.path.join(os.getcwd(), 'data')
                os.makedirs(fallback_dir, exist_ok=True)
                self.csv_file = os.path.join(fallback_dir, 'medications.csv')
                with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Date', 'Time', 'Medication', 'Dosage', 'Notes'])
                logger.info(f"✅ Created new medication log (fallback): {self.csv_file}")

    def _med_matches(self, recorded: str, queried: str) -> bool:
        """Return True if medication names look like a match (case-insensitive, substring)."""
        r = (recorded or "").strip().lower()
        q = (queried or "").strip().lower()
        if not r or not q:
            return False
        return q in r or r in q

    def find_last_entry_for_medication(self, medication_query: str) -> Optional[Dict[str, str]]:
        """Find the most recent CSV row for the given medication name."""
        try:
            if not os.path.exists(self.csv_file):
                return None
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = list(csv.DictReader(file))
                for row in reversed(reader):
                    if self._med_matches(row.get('Medication', ''), medication_query):
                        return row
        except Exception as e:
            logger.error(f"❌ Error searching last entry: {e}")
        return None

    def answer_question(self, text: str) -> Optional[Dict]:
        """Answer simple questions like 'when was the last time I took X' or 'how much X did I take last'."""
        if not text:
            return None
        q = text.lower().strip()

        # Patterns to extract medication for time query
        time_patterns = [
            r"when (?:did i|was the last time i) (?:take|took)\s+(.+)",
            r"when .* last .* (?:take|took)\s+(.+)",
            r"what time .* last .* (?:take|took)\s+(.+)"
        ]

        # Patterns to extract medication for dosage query
        dosage_patterns = [
            r"how much\s+(.+?)\s+did i take last",
            r"what (?:was|is) my last dose of\s+(.+)",
            r"what (?:was|is) the last dosage of\s+(.+)"
        ]

        import re as _re

        # Time query
        for p in time_patterns:
            m = _re.search(p, q)
            if m:
                med = m.group(1).strip().rstrip('?!.')
                row = self.find_last_entry_for_medication(med)
                if row:
                    date = row.get('Date', '')
                    time_str = row.get('Time', '')
                    med_name = row.get('Medication', '')
                    return {
                        "status": "answer",
                        "message": f"Your last {med_name} was on {date} at {time_str}.",
                        "data": {"medication": med_name, "date": date, "time": time_str}
                    }
                return {"status": "answer", "message": f"I couldn't find any {med} in your log."}

        # Dosage query
        for p in dosage_patterns:
            m = _re.search(p, q)
            if m:
                med = m.group(1).strip().rstrip('?!.')
                row = self.find_last_entry_for_medication(med)
                if row:
                    dosage = row.get('Dosage', '')
                    med_name = row.get('Medication', '')
                    date = row.get('Date', '')
                    time_str = row.get('Time', '')
                    return {
                        "status": "answer",
                        "message": f"Your last dose of {med_name} was {dosage} on {date} at {time_str}.",
                        "data": {"medication": med_name, "dosage": dosage, "date": date, "time": time_str}
                    }
                return {"status": "answer", "message": f"I couldn't find any {med} in your log."}

        return None
    
    def extract_medication_info(self, text: str) -> Optional[Dict[str, str]]:
        """Extract medication name and dosage from text"""
        text = text.lower().strip()
        
        # Enhanced patterns for medication descriptions
        patterns = [
            # "I'm taking 10mg of aspirin"
            r"(?:taking|took|take)\s+(\d+(?:\.\d+)?)\s*(mg|ml|pills?|tablets?|units?|capsules?)\s+(?:of\s+)?(.+)",
            # "I'm taking aspirin 10mg"
            r"(?:taking|took|take)\s+(.+?)\s+(\d+(?:\.\d+)?)\s*(mg|ml|pills?|tablets?|units?|capsules?)",
            # "10mg aspirin"
            r"(\d+(?:\.\d+)?)\s*(mg|ml|pills?|tablets?|units?|capsules?)\s+(?:of\s+)?(.+)",
            # "aspirin 10mg"
            r"(.+?)\s+(\d+(?:\.\d+)?)\s*(mg|ml|pills?|tablets?|units?|capsules?)",
            # "one pill of aspirin" or "two tablets of tylenol"
            r"(?:taking|took|take)\s+(one|two|three|four|five|six|seven|eight|nine|ten|a|an)\s+(pill|tablet|capsule)\s+(?:of\s+)?(.+)",
            # "aspirin one pill"
            r"(?:taking|took|take)\s+(.+?)\s+(one|two|three|four|five|six|seven|eight|nine|ten|a|an)\s+(pill|tablet|capsule)",
        ]
        
        # Number word to digit mapping
        number_words = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'a': '1', 'an': '1'
        }
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                
                if len(groups) == 3:
                    # Handle number words (e.g., "one pill")
                    if groups[0] in number_words:
                        dosage = f"{number_words[groups[0]]} {groups[1]}"
                        medication = groups[2].strip()
                    elif groups[1] in number_words:
                        medication = groups[0].strip()
                        dosage = f"{number_words[groups[1]]} {groups[2]}"
                    # Handle regular numbers
                    elif groups[0].replace('.', '').isdigit():
                        dosage = f"{groups[0]} {groups[1]}"
                        medication = groups[2].strip()
                    else:
                        medication = groups[0].strip()
                        dosage = f"{groups[1]} {groups[2]}"
                    
                    return {
                        "medication": medication.title(),
                        "dosage": dosage,
                        "timestamp": datetime.now().strftime("%I:%M %p"),
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
        
        # Fallback: try to extract any medication mention
        cleaned_text = re.sub(r'\b(i am|taking|took|take|some|medication|medicine|pill|tablet|capsule|mg|ml)\b', '', text)
        cleaned_text = cleaned_text.strip()
        
        if cleaned_text and len(cleaned_text) > 2:
            return {
                "medication": cleaned_text.title(),
                "dosage": "Not specified",
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        
        return None
    
    def add_medication(self, medication_data: Dict[str, str]) -> bool:
        """Add medication data to CSV file"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    medication_data["date"],
                    medication_data["timestamp"],
                    medication_data["medication"],
                    medication_data["dosage"],
                    ""  # Notes column (empty for now)
                ])
            
            logger.info(f"✅ Added medication: {medication_data['medication']} - {medication_data['dosage']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding medication: {e}")
            return False
    
    def get_recent_medications(self, days: int = 7) -> List[Dict]:
        """Get recent medications from CSV"""
        try:
            medications = []
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        med_date = datetime.strptime(row['Date'], '%Y-%m-%d')
                        if (cutoff_date - med_date).days <= days:
                            medications.append(row)
                    except ValueError:
                        continue
            
            return medications
            
        except Exception as e:
            logger.error(f"❌ Error reading medications: {e}")
            return []
    
    def process_transcript(self, text: str, session_id: str = None) -> Dict:
        """Process transcript text and return response"""
        text = text.lower().strip()
        
        # Trigger phrases
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
        
        # Check for trigger phrase
        if any(phrase in text for phrase in trigger_phrases):
            return {
                "status": "triggered",
                "message": "Okay, what medication are you taking?",
                "response": "I'm listening for your medication details. Please tell me what medication and dosage you're taking."
            }
        
        # Try to extract medication info
        medication_info = self.extract_medication_info(text)
        
        if medication_info:
            # Add to CSV
            success = self.add_medication(medication_info)
            
            if success:
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
        
        return {"status": "listening"}

# Global tracker instance
tracker = SimpleMedicationTracker()

def main():
    """Simple command-line interface for testing"""
    print("🧪 Simple Medication Tracker - Test Mode")
    print("Type 'quit' to exit")
    print("Try saying: 'I'm taking medication'")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if user_input:
                result = tracker.process_transcript(user_input)
                print(f"App: {result.get('message', result.get('response', 'Listening...'))}")
                
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
