#!/usr/bin/env python3
"""
Move existing reports to organized Google Drive folders
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from reports_organizer import upload_to_folder, get_folder_id

MEMORY_DIR = Path("C:/Users/MuLabs/.openclaw/workspace/memory")
REPORTS_DIR = MEMORY_DIR / "clinical-reports"

def organize_existing_reports():
    """Move all existing reports to organized folders"""
    print("="*70)
    print("ORGANIZING EXISTING REPORTS")
    print("="*70)
    
    moved = []
    
    # Clinical reports
    print("\n[Clinical Reports]")
    for report in REPORTS_DIR.glob("clinical-weekly-*.html"):
        print(f"  Moving {report.name} -> Clinical/Weekly...")
        file_id, link = upload_to_folder(report, 'Clinical', 'Weekly', f"Clinical weekly report")
        if link:
            moved.append(('Clinical/Weekly', report.name, link))
            print(f"    [OK] {link}")
    
    for report in REPORTS_DIR.glob("clinical-evolution-*.xlsx"):
        print(f"  Moving {report.name} -> Clinical/Weekly...")
        file_id, link = upload_to_folder(report, 'Clinical', 'Weekly', f"Clinical evolution report with charts")
        if link:
            moved.append(('Clinical/Weekly', report.name, link))
            print(f"    [OK] {link}")
    
    # System reports (health reports, etc.)
    print("\n[System Reports]")
    for report in MEMORY_DIR.glob("system-health-report-*.md"):
        print(f"  Moving {report.name} -> System/Weekly...")
        file_id, link = upload_to_folder(report, 'System', 'Weekly', f"System health report")
        if link:
            moved.append(('System/Weekly', report.name, link))
            print(f"    [OK] {link}")
    
    # Task/Team reports
    print("\n[Team/Tasks Reports]")
    for report in MEMORY_DIR.glob("team-velocity.json"):
        print(f"  Moving {report.name} -> Tasks/Weekly...")
        file_id, link = upload_to_folder(report, 'Tasks', 'Weekly', f"Team velocity metrics")
        if link:
            moved.append(('Tasks/Weekly', report.name, link))
            print(f"    [OK] {link}")
    
    # Energy heatmap
    for report in MEMORY_DIR.glob("energy-heatmap.json"):
        print(f"  Moving {report.name} -> System/Weekly...")
        file_id, link = upload_to_folder(report, 'System', 'Weekly', f"Energy/focus heatmap analysis")
        if link:
            moved.append(('System/Weekly', report.name, link))
            print(f"    [OK] {link}")
    
    # Patterns
    for report in MEMORY_DIR.glob("patterns.json"):
        print(f"  Moving {report.name} -> System/Weekly...")
        file_id, link = upload_to_folder(report, 'System', 'Weekly', f"Detected patterns analysis")
        if link:
            moved.append(('System/Weekly', report.name, link))
            print(f"    [OK] {link}")
    
    # Waiting on tracker
    for report in MEMORY_DIR.glob("waiting-on.json"):
        print(f"  Moving {report.name} -> Tasks/Weekly...")
        file_id, link = upload_to_folder(report, 'Tasks', 'Weekly', f"Waiting-on tracker")
        if link:
            moved.append(('Tasks/Weekly', report.name, link))
            print(f"    [OK] {link}")
    
    print("\n" + "="*70)
    print(f"ORGANIZATION COMPLETE: {len(moved)} files moved")
    print("="*70)
    
    for folder, name, link in moved:
        print(f"  {folder}: {name}")
    
    return moved

if __name__ == "__main__":
    organize_existing_reports()
