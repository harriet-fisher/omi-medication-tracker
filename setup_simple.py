#!/usr/bin/env python3
"""
Simple Setup Script for Medication Tracker
This script helps you get the medication tracker running quickly!
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 Simple Medication Tracker Setup")
    print("=" * 50)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected!")
        print("   It's recommended to activate your virtual environment first.")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled. Please activate your virtual environment and try again.")
            return
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command("pip install -r simple_requirements.txt", "Installing Python packages"):
        print("❌ Failed to install dependencies. Please check your internet connection and try again.")
        return
    
    # Test the simple tracker
    print("\n🧪 Testing the medication tracker...")
    try:
        from simple_medication_tracker import SimpleMedicationTracker
        tracker = SimpleMedicationTracker()
        print("✅ Simple medication tracker imported successfully!")
    except Exception as e:
        print(f"❌ Error testing tracker: {e}")
        return
    
    # Create a simple test
    print("\n🧪 Running a quick test...")
    test_result = tracker.process_transcript("I'm taking medication")
    if test_result.get("status") == "triggered":
        print("✅ Test passed! The tracker is working correctly.")
    else:
        print("⚠️  Test had unexpected result, but tracker is installed.")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. To test the tracker: python simple_medication_tracker.py")
    print("2. To run the server: python simple_server.py")
    print("3. For Omi integration, set the webhook URL to: http://your-ip:8000/medication-tracker")
    print("\n📁 Your medication data will be stored in: medications.csv")
    print("\n💡 Tips:")
    print("- The server runs on port 8000 by default")
    print("- Make sure your Omi device can reach your computer's IP address")
    print("- You can view your medication history by opening medications.csv in Excel or similar")

if __name__ == "__main__":
    main()
