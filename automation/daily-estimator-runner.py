#!/usr/bin/env python3
"""
Daily Activity Estimator Runner
Updates hour estimates every day at 6 AM
"""
import subprocess
import sys
from datetime import datetime

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running activity-based hour estimator...")
    
    # Run the estimator
    result = subprocess.run(
        [sys.executable, 'automation/quick-estimator.py'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("[WARN]", result.stderr)
    
    # Update dashboard
    result2 = subprocess.run(
        [sys.executable, 'automation/mission-control-updater.py', 
         '--changes', 'Daily activity hour estimates updated'],
        capture_output=True,
        text=True
    )
    
    print("[DASHBOARD] Updated with new estimates")
    return 0

if __name__ == "__main__":
    exit(main())
