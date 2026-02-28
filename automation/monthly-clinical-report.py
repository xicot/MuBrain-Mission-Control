#!/usr/bin/env python3
"""
Monthly Clinical Summary Report
Generates monthly summary of all completed sessions
"""

import requests
import sys
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from io import StringIO

sys.path.insert(0, os.path.dirname(__file__))

try:
    from drive_upload_helper import upload_report_text
    DRIVE_UPLOAD_AVAILABLE = True
except ImportError:
    DRIVE_UPLOAD_AVAILABLE = False

# Config
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_TOKEN', '')
AIRTABLE_BASE_ID = "apphR8DK6lVJeY8n0"

if not AIRTABLE_TOKEN:
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            AIRTABLE_TOKEN = config.get('airtable_token', '')

SESSIONS_TABLE_ID = "tblFywptl9YawXrQJ"
PATIENTS_TABLE_ID = "tbldTQ3PxG5pcZVZ1"

PRICING = {
    'Dr. FMT': {'NFB Online': {'invoice': 75, 'pay': 75}},
    'Dr. VA': {
        'NFB Presencial': {'invoice': 75, 'pay': 28},
        'QEEG': {'invoice': 180, 'pay': 15},
        'Somatic Session': {'invoice': 85, 'pay': 30},
        'Clinical Session': {'invoice': 65, 'pay': 35}
    }
}

def get_completed_sessions_this_month():
    today = datetime.now().date()
    first_day = today.replace(day=1)
    first_day_str = first_day.isoformat()
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{SESSIONS_TABLE_ID}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    params = {'filterByFormula': f"AND({{Session Completed}}, IS_AFTER({{Session Date & Time}}, '{first_day_str}'))"}
    
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
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PATIENTS_TABLE_ID}/{patient_id}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('fields', {}).get('Paciente', 'Unknown')
    return 'Unknown'

def generate_monthly_report():
    today = datetime.now().date()
    first_day = today.replace(day=1)
    output = StringIO()
    
    def write(line=""):
        print(line)
        output.write(line + "\n")
    
    write("=" * 70)
    write(f"MONTHLY CLINICAL SUMMARY: {first_day.strftime('%B %Y')}")
    write("=" * 70)
    
    sessions = get_completed_sessions_this_month()
    if not sessions:
        write("\nNo completed sessions this month.")
        return output.getvalue()
    
    write(f"\nTotal sessions: {len(sessions)}")
    
    by_facilitator = defaultdict(lambda: defaultdict(list))
    by_session_type = defaultdict(int)
    total_invoice = 0
    total_pay = 0
    
    for record in sessions:
        fields = record.get('fields', {})
        doctor = fields.get('Doctor Attended', 'Unknown')
        session_type = fields.get('Session Type', 'Unknown')
        patient_links = fields.get('Patient', [])
        patient_name = get_patient_name(patient_links[0]) if patient_links else 'Unknown'
        
        by_facilitator[doctor][patient_name].append({'type': session_type})
        by_session_type[session_type] += 1
    
    for doctor in sorted(by_facilitator.keys()):
        write(f"\n{'=' * 70}")
        write(f"{doctor}")
        write("=" * 70)
        
        doc_invoice = 0
        doc_pay = 0
        
        for patient, sess_list in by_facilitator[doctor].items():
            p_inv = sum(PRICING.get(doctor, {}).get(s['type'], {}).get('invoice', 0) for s in sess_list)
            p_pay = sum(PRICING.get(doctor, {}).get(s['type'], {}).get('pay', 0) for s in sess_list)
            write(f"  {patient}: {len(sess_list)} sessions | Invoice EUR{p_inv}, Pay EUR{p_pay}")
            doc_invoice += p_inv
            doc_pay += p_pay
        
        write(f"\n  Subtotal: Invoice EUR{doc_invoice}, Pay EUR{doc_pay}")
        total_invoice += doc_invoice
        total_pay += doc_pay
    
    write(f"\n{'=' * 70}")
    write("SESSION TYPES")
    write("=" * 70)
    for st, count in sorted(by_session_type.items()):
        write(f"  {st}: {count}")
    
    write(f"\n{'=' * 70}")
    write("FINANCIAL SUMMARY")
    write("=" * 70)
    write(f"Total Invoice: EUR{total_invoice}")
    write(f"Total Payments: EUR{total_pay}")
    write(f"Net Margin: EUR{total_invoice - total_pay}")
    write("=" * 70)
    
    return output.getvalue()

def main():
    print("Generating Monthly Clinical Summary...\n")
    report = generate_monthly_report()
    
    if DRIVE_UPLOAD_AVAILABLE:
        print("\nUploading to Google Drive...")
        try:
            today = datetime.now().date()
            file_id, link = upload_report_text(report, f"Monthly-Summary-{today.strftime('%Y-%m')}.txt", f"Summary for {today.strftime('%B %Y')}")
            print(f"Uploaded: {link}")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
