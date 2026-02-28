#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Clinical Reports - Complete Package
Generates PDF + Excel reports and uploads to Google Drive
Run every Friday at 5 PM via cron
"""

import sys
import io
from pathlib import Path

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

sys.path.insert(0, str(Path(__file__).parent))

from clinical_reports_manager import save_and_upload_report
from excel_reports_generator import generate_and_upload_excel_report


def generate_weekly_package():
    """Generate complete weekly report package"""
    print("="*70)
    print("WEEKLY CLINICAL REPORTS PACKAGE")
    print("="*70)
    
    results = {}
    
    # 1. Generate PDF Report
    print("\n[1/2] Generating PDF Clinical Report...")
    print("-"*70)
    pdf_result = save_and_upload_report('weekly')
    
    if pdf_result:
        results['pdf'] = pdf_result
        print(f"[OK] PDF: {pdf_result['drive_link']}")
    else:
        print("[WARN] PDF generation had issues")
    
    # 2. Generate Excel Report
    print("\n[2/2] Generating Excel Evolution Report...")
    print("-"*70)
    excel_result = generate_and_upload_excel_report()
    
    if excel_result:
        results['excel'] = excel_result
        print(f"[OK] Excel: {excel_result['drive_link']}")
    else:
        print("[WARN] Excel generation had issues")
    
    # Summary
    print("\n" + "="*70)
    print("REPORTS PACKAGE COMPLETE")
    print("="*70)
    print(f"\nPDF Report:")
    print(f"  Sessions: {results.get('pdf', {}).get('metadata', {}).get('total_sessions', 'N/A')}")
    print(f"  Net Margin: EUR {results.get('pdf', {}).get('metadata', {}).get('net_margin', 'N/A')}")
    print(f"  Link: {results.get('pdf', {}).get('drive_link', 'N/A')}")
    
    print(f"\nExcel Evolution:")
    print(f"  Total Revenue (6mo): EUR {results.get('excel', {}).get('metadata', {}).get('total_revenue', 'N/A')}")
    print(f"  Total Sessions (6mo): {results.get('excel', {}).get('metadata', {}).get('total_sessions', 'N/A')}")
    print(f"  Link: {results.get('excel', {}).get('drive_link', 'N/A')}")
    
    print("\n[ALL REPORTS UPLOADED TO GOOGLE DRIVE]")
    print("="*70)
    
    return results


if __name__ == "__main__":
    generate_weekly_package()
