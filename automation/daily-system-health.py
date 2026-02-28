#!/usr/bin/env python3
"""
Daily System Health Snapshot
Quick daily health check for all systems
Uploads to System/Daily folder
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from reports_organizer import upload_to_folder

MEMORY_DIR = Path("C:/Users/MuLabs/.openclaw/workspace/memory")
STATUS_DIR = Path("C:/Users/MuLabs/.openclaw/workspace/status")

def load_json_file(filepath, default=None):
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
    except:
        pass
    return default or {}

def check_system_health():
    """Generate daily system health snapshot"""
    print("="*70)
    print("GENERATING DAILY SYSTEM HEALTH SNAPSHOT")
    print("="*70)
    
    today = datetime.now()
    
    print("\n[Checking System Components...]")
    
    # Check various status files
    components = []
    
    # Clockify status
    clockify = load_json_file(STATUS_DIR / "clockify.json", {})
    components.append({
        'name': 'Clockify Time Tracking',
        'status': 'OK' if clockify.get('status') == 'active' else 'WARN',
        'details': f"{clockify.get('total_hours_this_week', 0):.1f}h this week"
    })
    
    # Airtable cache
    airtable = load_json_file(MEMORY_DIR / "airtable-sessions-cache.json", {})
    components.append({
        'name': 'Airtable Connection',
        'status': 'OK' if airtable.get('sessions') else 'WARN',
        'details': f"{len(airtable.get('sessions', []))} sessions cached"
    })
    
    # Calendar data
    calendar = load_json_file(MEMORY_DIR / "calendar-today.json", {})
    components.append({
        'name': 'Calendar Sync',
        'status': 'OK' if calendar.get('events') is not None else 'WARN',
        'details': f"{len(calendar.get('events', []))} events today"
    })
    
    # Reports manifest
    reports = load_json_file(MEMORY_DIR / "clinical-reports" / "reports-manifest.json", {})
    components.append({
        'name': 'Reports System',
        'status': 'OK',
        'details': f"{reports.get('total_reports', 0)} reports generated"
    })
    
    # Cost tracking
    costs = load_json_file(MEMORY_DIR / "cost-tracking.json", {})
    components.append({
        'name': 'Cost Tracking',
        'status': 'OK' if costs else 'WARN',
        'details': f"${costs.get('monthly_spend', 0):.2f} this month"
    })
    
    # Team velocity
    velocity = load_json_file(MEMORY_DIR / "team-velocity.json", {})
    components.append({
        'name': 'Team Velocity',
        'status': 'OK',
        'details': f"Masha: {velocity.get('masha_completion_rate', 0)}%, Rafael: {velocity.get('rafael_completion_rate', 0)}%"
    })
    
    for comp in components:
        print(f"  [{comp['status']}] {comp['name']}: {comp['details']}")
    
    # Count status
    ok_count = sum(1 for c in components if c['status'] == 'OK')
    warn_count = sum(1 for c in components if c['status'] == 'WARN')
    error_count = sum(1 for c in components if c['status'] == 'ERROR')
    
    print(f"\n  Summary: {ok_count} OK, {warn_count} Warning, {error_count} Error")
    
    # Generate HTML snapshot
    print("\n[Generating HTML Snapshot...]")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MuLabs System Health - {today.strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px 20px;
            background: #0f172a;
            color: #e2e8f0;
        }}
        h1 {{ 
            color: #60a5fa; 
            border-bottom: 2px solid #3b82f6; 
            padding-bottom: 10px;
            font-size: 1.8em;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #3b82f6;
        }}
        .status-ok {{ color: #10b981; }}
        .status-warn {{ color: #fbbf24; }}
        .status-error {{ color: #f87171; }}
        .component {{
            background: #1e293b;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 10px 0;
            border: 1px solid #334155;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .component-name {{
            font-weight: 600;
        }}
        .component-details {{
            color: #94a3b8;
            font-size: 0.9em;
        }}
        .summary {{
            background: #1e293b;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #334155;
            text-align: center;
        }}
        .summary-number {{
            font-size: 3em;
            font-weight: bold;
        }}
        .summary-label {{
            color: #94a3b8;
        }}
        .footer {{
            text-align: center;
            color: #64748b;
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #334155;
            font-size: 0.9em;
        }}
        .timestamp {{
            color: #64748b;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 System Health Snapshot</h1>
        <p class="timestamp">Generated: {today.strftime('%Y-%m-%d %H:%M')} | Daily Check</p>
    </div>

    <div class="summary">
        <div class="summary-number status-ok">{ok_count}/{len(components)}</div>
        <div class="summary-label">Systems Operational</div>
    </div>

    <h2 style="color: #60a5fa; margin-top: 25px;">Component Status</h2>
"""
    
    for comp in components:
        status_class = f"status-{comp['status'].lower()}"
        html_content += f"""
    <div class="component">
        <div>
            <div class="component-name">{comp['name']}</div>
            <div class="component-details">{comp['details']}</div>
        </div>
        <div class="{status_class}" style="font-weight: bold;">{comp['status']}</div>
    </div>
"""
    
    html_content += f"""
    <div class="footer">
        <p>MuLabs System Monitor | Automated Daily Check</p>
        <p>Next check: {(today + timedelta(days=1)).strftime('%Y-%m-%d')} 08:00</p>
    </div>
</body>
</html>
"""
    
    # Save locally
    report_path = MEMORY_DIR / f"system-health-daily-{today.strftime('%Y-%m-%d')}.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  [OK] Snapshot saved: {report_path}")
    
    # Upload to Drive
    print("\n[Uploading to System/Daily folder...]")
    file_id, link = upload_to_folder(
        report_path,
        'System',
        'Daily',
        f"System health snapshot - {today.strftime('%Y-%m-%d')}"
    )
    
    if link:
        print(f"  [OK] Uploaded: {link}")
    
    print("\n" + "="*70)
    print("DAILY SYSTEM HEALTH SNAPSHOT COMPLETE")
    print("="*70)
    
    return {
        'local_path': str(report_path),
        'drive_link': link,
        'status': 'healthy' if error_count == 0 and warn_count == 0 else 'warning' if error_count == 0 else 'error',
        'components_checked': len(components)
    }

if __name__ == "__main__":
    result = check_system_health()
    if result:
        print(f"\nSnapshot available at: {result['drive_link']}")
        print(f"Overall Status: {result['status'].upper()}")
