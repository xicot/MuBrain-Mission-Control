#!/usr/bin/env python3
"""
Clinical Reports Manager
Generates weekly/monthly clinical reports and saves to Google Drive
Accessible through Mission Control
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Fix Windows encoding
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Configuration
MEMORY_DIR = Path("C:/Users/MuLabs/.openclaw/workspace/memory")
REPORTS_DIR = MEMORY_DIR / "clinical-reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Google Drive Config
DRIVE_CONFIG_FILE = Path("C:/Users/MuLabs/.openclaw/workspace/automation/google-drive-config.json")
REPORTS_FOLDER_ID = None

if DRIVE_CONFIG_FILE.exists():
    with open(DRIVE_CONFIG_FILE, 'r') as f:
        drive_config = json.load(f)
        REPORTS_FOLDER_ID = drive_config.get('reports_folder_id')

# Airtable Config
AIRTABLE_TOKEN = "patAthNmGc9Zzx1cc.0f09c44dbc5f639bd905528782d62bab045154e48b2b0d5f40f6d0e0570a80fc"
AIRTABLE_BASE_ID = "apphR8DK6lVJeY8n0"
SESSIONS_TABLE_ID = "tblFywptl9YawXrQJ"
PATIENTS_TABLE_ID = "tbldTQ3PxG5pcZVZ1"

# Pricing
PRICING = {
    'Dr. FMT': {'NFB Online': {'invoice': 75, 'pay': 75}},
    'Dr. VA': {
        'NFB Presencial': {'invoice': 75, 'pay': 28},
        'QEEG': {'invoice': 180, 'pay': 15},
        'Somatic Session': {'invoice': 85, 'pay': 30},
        'Clinical Session': {'invoice': 65, 'pay': 35}
    }
}


def get_google_drive_service():
    """Get authenticated Google Drive service"""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import pickle
        
        token_path = Path("C:/Users/MuLabs/.openclaw/workspace/automation/google-drive-token.pickle")
        if not token_path.exists():
            print("❌ Google Drive token not found")
            return None
        
        # Load credentials from pickle file
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed credentials
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Drive service error: {e}")
        return None


def upload_to_drive(service, file_path, folder_id, mime_type='text/html'):
    """Upload file to Google Drive with proper UTF-8 encoding"""
    try:
        from googleapiclient.http import MediaFileUpload
        import io
        
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create temp file with explicit UTF-8 BOM for Windows compatibility
        temp_path = file_path.with_suffix('.tmp.html')
        with open(temp_path, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        
        file_metadata = {
            'name': file_path.name,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(str(temp_path), mimetype=mime_type, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        # Explicitly close media before cleanup (Windows file lock fix)
        if hasattr(media, '_fd') and media._fd:
            media._fd.close()
        
        # Clean up temp file
        import time
        time.sleep(0.5)  # Small delay for Windows file handle release
        temp_path.unlink(missing_ok=True)
        
        return {
            'id': file['id'],
            'link': file['webViewLink']
        }
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_sessions_from_airtable(start_date, end_date):
    """Get completed sessions from Airtable"""
    import requests
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{SESSIONS_TABLE_ID}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    
    params = {
        'filterByFormula': f"AND({{Session Completed}}, IS_AFTER({{Session Date & Time}}, '{start_date}'), IS_BEFORE({{Session Date & Time}}, '{end_date}T23:59:59'))"
    }
    
    all_records = []
    offset = None
    
    while True:
        if offset:
            params['offset'] = offset
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            all_records.extend(data.get('records', []))
            offset = data.get('offset')
            if not offset:
                break
        else:
            print(f"❌ Airtable error: {response.status_code}")
            break
    
    return all_records


def get_patient_name(patient_id):
    """Get patient name from Airtable"""
    import requests
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PATIENTS_TABLE_ID}/{patient_id}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('fields', {}).get('Paciente', 'Unknown')
    
    return 'Unknown'


def generate_weekly_report():
    """Generate weekly clinical report"""
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    
    sessions = get_sessions_from_airtable(monday.isoformat(), today.isoformat())
    
    # Build report data
    by_facilitator = defaultdict(lambda: defaultdict(list))
    total_invoice = 0
    total_facilitator_pay = 0
    
    for record in sessions:
        fields = record.get('fields', {})
        doctor = fields.get('Doctor Attended', 'Unknown')
        session_type = fields.get('Session Type', 'Unknown')
        session_number = fields.get('Session Number', '?')
        
        patient_links = fields.get('Patient', [])
        patient_name = get_patient_name(patient_links[0]) if patient_links else 'Unknown'
        
        if doctor in PRICING and session_type in PRICING[doctor]:
            invoice_amount = PRICING[doctor][session_type]['invoice']
            pay_amount = PRICING[doctor][session_type]['pay']
        else:
            invoice_amount = fields.get('Price (€)', 0)
            pay_amount = 0
        
        by_facilitator[doctor][patient_name].append({
            'type': session_type,
            'number': session_number,
            'invoice': invoice_amount,
            'pay': pay_amount
        })
        
        total_invoice += invoice_amount
        total_facilitator_pay += pay_amount
    
    # Generate HTML report
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Weekly Clinical Report - {monday.strftime('%b %d')} to {today.strftime('%b %d, %Y')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; max-width: 1000px; margin: 0 auto; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #00d4ff, #0099cc); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 2em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .card {{ background: white; border-radius: 10px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #0099cc; margin-top: 0; border-bottom: 2px solid #00d4ff; padding-bottom: 10px; }}
        .facilitator {{ margin-bottom: 30px; }}
        .facilitator h3 {{ color: #333; margin-bottom: 15px; }}
        .patient {{ margin: 15px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; border-left: 4px solid #00d4ff; }}
        .patient strong {{ color: #0099cc; }}
        .session {{ margin: 5px 0; color: #666; font-size: 0.95em; }}
        .summary {{ background: linear-gradient(135deg, #00d4ff22, #0099cc22); padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .summary-row {{ display: flex; justify-content: space-between; margin: 10px 0; font-size: 1.1em; }}
        .summary-row.total {{ font-size: 1.3em; font-weight: bold; color: #0099cc; border-top: 2px solid #00d4ff; padding-top: 10px; margin-top: 15px; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; background: #00d4ff; color: white; }}
        .footer {{ text-align: center; margin-top: 40px; color: #999; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Weekly Clinical Report</h1>
        <p>{monday.strftime('%B %d')} - {today.strftime('%B %d, %Y')} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
"""
    
    # Add facilitator sections
    for doctor in sorted(by_facilitator.keys()):
        facilitator_name = "Xico (FMT)" if doctor == 'Dr. FMT' else "Vanessa (VA)"
        html_content += f'<div class="card">\n<h2>👨‍⚕️ {facilitator_name}</h2>\n'
        
        patients = by_facilitator[doctor]
        facilitator_invoice = 0
        facilitator_pay = 0
        
        for patient_name in sorted(patients.keys()):
            patient_sessions = patients[patient_name]
            html_content += f'<div class="patient">\n<strong>{patient_name}</strong>\n'
            
            patient_invoice = 0
            patient_pay = 0
            
            for session in patient_sessions:
                html_content += f'<div class="session">• Session #{session["number"]} ({session["type"]}) - Invoice: €{session["invoice"]}, Pay: €{session["pay"]}</div>\n'
                patient_invoice += session['invoice']
                patient_pay += session['pay']
            
            html_content += f'<div style="margin-top: 8px; color: #0099cc; font-weight: 600;">Patient Total: Invoice €{patient_invoice} | Facilitator €{patient_pay}</div>\n</div>\n'
            
            facilitator_invoice += patient_invoice
            facilitator_pay += patient_pay
        
        html_content += f'<div class="summary">\n<div class="summary-row"><span>Total to Invoice:</span><span>€{facilitator_invoice}</span></div>\n'
        html_content += f'<div class="summary-row"><span>Total to Pay Facilitator:</span><span>€{facilitator_pay}</span></div>\n'
        if doctor == 'Dr. FMT':
            html_content += '<div style="font-size: 0.9em; color: #666; margin-top: 10px;">Xico receives 100% of invoiced amount</div>\n'
        html_content += '</div>\n</div>\n'
    
    # Add final summary
    html_content += f'''<div class="card">
<h2>📊 Weekly Summary</h2>
<div class="summary">
    <div class="summary-row"><span>Total Sessions:</span><span>{len(sessions)}</span></div>
    <div class="summary-row"><span>Total to Invoice Clients:</span><span>€{total_invoice}</span></div>
    <div class="summary-row"><span>Total Facilitator Payments:</span><span>€{total_facilitator_pay}</span></div>
    <div class="summary-row total"><span>MuLabs Net Margin:</span><span>€{total_invoice - total_facilitator_pay}</span></div>
</div>
</div>

<div class="footer">
<p>Generated by MuBrain Clinical Reports System</p>
<p>📧 Sent to: highmashion22@gmail.com | CC: francisco.ma.teixeira@gmail.com</p>
</div>
</body>
</html>'''
    
    return html_content, {
        'week_start': monday.isoformat(),
        'week_end': today.isoformat(),
        'total_sessions': len(sessions),
        'total_invoice': total_invoice,
        'total_facilitator_pay': total_facilitator_pay,
        'net_margin': total_invoice - total_facilitator_pay
    }


def save_and_upload_report(report_type='weekly'):
    """Generate report, save locally, and upload to Google Drive"""
    print(f"🔄 Generating {report_type} clinical report...")
    
    # Generate report
    if report_type == 'weekly':
        html_content, metadata = generate_weekly_report()
        filename = f"clinical-weekly-{datetime.now().strftime('%Y-%m-%d')}.html"
    else:
        # Monthly report generation (similar structure)
        print("Monthly report - using weekly structure as base")
        html_content, metadata = generate_weekly_report()  # Extend for monthly
        filename = f"clinical-monthly-{datetime.now().strftime('%Y-%m-%d')}.html"
    
    # Save locally
    local_path = REPORTS_DIR / filename
    with open(local_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Saved locally: {local_path}")
    
    # Upload to Google Drive
    drive_service = get_google_drive_service()
    if drive_service and REPORTS_FOLDER_ID:
        print("☁️  Uploading to Google Drive...")
        upload_result = upload_to_drive(drive_service, local_path, REPORTS_FOLDER_ID, 'text/html')
        
        if upload_result:
            print(f"✅ Uploaded to Drive: {upload_result['link']}")
            
            # Update reports manifest
            manifest_file = MEMORY_DIR / "reports-manifest.json"
            manifest = {}
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
            
            if 'clinical_reports' not in manifest:
                manifest['clinical_reports'] = []
            
            report_entry = {
                'type': report_type,
                'date': datetime.now().isoformat(),
                'filename': filename,
                'local_path': str(local_path),
                'drive_id': upload_result['id'],
                'drive_link': upload_result['link'],
                'metadata': metadata
            }
            
            manifest['clinical_reports'].insert(0, report_entry)
            manifest['clinical_reports'] = manifest['clinical_reports'][:20]  # Keep last 20
            
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            print(f"✅ Reports manifest updated")
            return report_entry
    
    return None


if __name__ == "__main__":
    report_type = sys.argv[1] if len(sys.argv) > 1 else 'weekly'
    result = save_and_upload_report(report_type)
    
    if result:
        print(f"\n✅ Report complete!")
        print(f"   Type: {result['type']}")
        print(f"   Drive Link: {result['drive_link']}")
        print(f"   Sessions: {result['metadata']['total_sessions']}")
        print(f"   Net Margin: €{result['metadata']['net_margin']}")
    else:
        print("\n⚠️  Report generated but Drive upload may have failed")
