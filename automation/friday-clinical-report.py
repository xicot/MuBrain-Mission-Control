#!/usr/bin/env python3
"""
Friday Clinical Invoicing Report
Generates weekly summary of completed sessions for Masha
- Sessions by facilitator (Xico/Vanessa)
- Sessions by client with pricing
- Invoice amounts + facilitator payments
- Uploads report to Google Drive
"""

import requests
import sys
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from io import StringIO

# Add automation folder to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Try to import drive upload helper
try:
    from drive_upload_helper import upload_report_text
    DRIVE_UPLOAD_AVAILABLE = True
except ImportError:
    DRIVE_UPLOAD_AVAILABLE = False
    print("[WARNING] Google Drive upload not available. Run: python automation/setup-google-drive.py")

# Config - Load from environment or config file
import os
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_TOKEN', '')
AIRTABLE_BASE_ID = "apphR8DK6lVJeY8n0"

# Try to load from config file if env var not set
if not AIRTABLE_TOKEN:
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            AIRTABLE_TOKEN = config.get('airtable_token', '')
SESSIONS_TABLE_ID = "tblFywptl9YawXrQJ"
PATIENTS_TABLE_ID = "tbldTQ3PxG5pcZVZ1"

# Pricing (from MUHEALTH-PRICING.md)
PRICING = {
    'Dr. FMT': {
        'NFB Online': {'invoice': 75, 'pay': 75}  # Xico keeps 100%
    },
    'Dr. VA': {
        'NFB Presencial': {'invoice': 75, 'pay': 28},
        'QEEG': {'invoice': 180, 'pay': 15},
        'Somatic Session': {'invoice': 85, 'pay': 30},
        'Clinical Session': {'invoice': 65, 'pay': 35}
    }
}

def get_completed_sessions_this_week():
    """Get all completed sessions from this week"""
    # Calculate Monday of this week
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    monday_str = monday.isoformat()
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{SESSIONS_TABLE_ID}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    
    # Filter: completed sessions since Monday
    params = {
        'filterByFormula': f"AND({{Session Completed}}, IS_AFTER({{Session Date & Time}}, '{monday_str}'))"
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
            print(f"[ERROR] Airtable: {response.status_code}")
            break
    
    return all_records

def get_patient_name(patient_id):
    """Get patient name from Patients table"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PATIENTS_TABLE_ID}/{patient_id}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('fields', {}).get('Paciente', 'Unknown')
    
    return 'Unknown'

def generate_weekly_report():
    """Generate weekly clinical sessions report"""
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    
    # Use StringIO to capture output for upload
    output = StringIO()
    
    def write(line=""):
        print(line)
        output.write(line + "\n")
    
    write("=" * 70)
    write(f"WEEKLY CLINICAL REPORT: {monday.strftime('%b %d')} - {today.strftime('%b %d, %Y')}")
    write("=" * 70)
    
    # Get completed sessions
    sessions = get_completed_sessions_this_week()
    
    if not sessions:
        write("\nNo completed sessions this week.")
        return output.getvalue()
    
    write(f"\nTotal completed sessions: {len(sessions)}")
    
    # Organize by facilitator and patient
    by_facilitator = defaultdict(lambda: defaultdict(list))
    
    for record in sessions:
        fields = record.get('fields', {})
        
        doctor = fields.get('Doctor Attended', 'Unknown')
        session_type = fields.get('Session Type', 'Unknown')
        session_number = fields.get('Session Number', '?')
        price = fields.get('Price (\u20ac)', 0)
        
        # Get patient name
        patient_links = fields.get('Patient', [])
        if patient_links:
            patient_name = get_patient_name(patient_links[0])
        else:
            patient_name = 'Unknown Patient'
        
        by_facilitator[doctor][patient_name].append({
            'type': session_type,
            'number': session_number,
            'price': price
        })
    
    # Calculate totals
    total_invoice = 0
    total_facilitator_pay = 0
    
    # Print by facilitator
    for doctor in sorted(by_facilitator.keys()):
        if doctor == 'Dr. FMT':
            write(f"\n{'=' * 70}")
            write("XICO (FMT)")
            write("=" * 70)
        elif doctor == 'Dr. VA':
            write(f"\n{'=' * 70}")
            write("VANESSA (VA)")
            write("=" * 70)
        
        facilitator_total_invoice = 0
        facilitator_total_pay = 0
        
        patients = by_facilitator[doctor]
        
        for patient_name in sorted(patients.keys()):
            patient_sessions = patients[patient_name]
            
            write(f"\n{patient_name}:")
            
            patient_invoice = 0
            patient_pay = 0
            
            for session in patient_sessions:
                session_type = session['type']
                session_num = session['number']
                
                # Get pricing
                if doctor in PRICING and session_type in PRICING[doctor]:
                    invoice_amount = PRICING[doctor][session_type]['invoice']
                    pay_amount = PRICING[doctor][session_type]['pay']
                else:
                    invoice_amount = session.get('price', 0)
                    pay_amount = 0
                
                write(f"  - Session #{session_num} ({session_type}) -> Invoice EUR{invoice_amount}, Pay EUR{pay_amount}")
                
                patient_invoice += invoice_amount
                patient_pay += pay_amount
            
            write(f"  TOTAL: Invoice EUR{patient_invoice}, Facilitator EUR{patient_pay}")
            
            facilitator_total_invoice += patient_invoice
            facilitator_total_pay += patient_pay
        
        write(f"\n{doctor} TOTAL:")
        write(f"  Invoice clients: EUR{facilitator_total_invoice}")
        write(f"  Pay facilitator: EUR{facilitator_total_pay}")
        if doctor == 'Dr. FMT':
            write(f"  (Xico receives full amount)")
        
        total_invoice += facilitator_total_invoice
        total_facilitator_pay += facilitator_total_pay
    
    # Final summary
    write(f"\n{'=' * 70}")
    write("WEEKLY SUMMARY")
    write("=" * 70)
    write(f"Total to invoice clients: EUR{total_invoice}")
    write(f"Total facilitator payments: EUR{total_facilitator_pay}")
    write(f"MuLabs net (after facilitator costs): EUR{total_invoice - total_facilitator_pay}")
    write("=" * 70)
    
    write("\nGreen meetings in Airtable = Ready to invoice")
    write("This report sent to: highmashion22@gmail.com (CC: francisco.ma.teixeira@gmail.com)")
    
    return output.getvalue()

def main():
    """Generate and upload report"""
    
    print("Generating Weekly Clinical Report...\n")
    
    # Generate report
    report_content = generate_weekly_report()
    
    # Upload to Google Drive if available
    if DRIVE_UPLOAD_AVAILABLE:
        print("\n" + "=" * 70)
        print("UPLOADING TO GOOGLE DRIVE...")
        print("=" * 70)
        
        try:
            today = datetime.now().date()
            file_name = f"Clinical-Report-{today.strftime('%Y-%m-%d')}.txt"
            description = f"Weekly clinical invoicing report for week of {today.strftime('%b %d, %Y')}"
            
            file_id, link = upload_report_text(report_content, file_name, description)
            
            print(f"\n[SUCCESS] Report uploaded to Google Drive!")
            print(f"Folder: https://drive.google.com/drive/folders/1BFb4hGU4sBjExV6MTv6m64F8OPnN85bI")
            
        except Exception as e:
            print(f"\n[ERROR] Upload failed: {str(e)}")
            print("Report generated but not uploaded to Drive.")
    else:
        print("\n[NOTE] Google Drive upload skipped (setup required)")

if __name__ == "__main__":
    main()
