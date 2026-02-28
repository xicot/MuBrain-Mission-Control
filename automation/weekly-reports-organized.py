#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Clinical Reports - Complete Package (Organized)
Generates PDF + Excel reports and uploads to organized Google Drive folders
Run every Friday at 5 PM via cron
"""

import sys
import io
from pathlib import Path
from datetime import datetime

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

sys.path.insert(0, str(Path(__file__).parent))

from clinical_reports_manager import save_and_upload_report
from excel_reports_generator import generate_and_upload_excel_report
from reports_organizer import upload_to_folder, get_folder_id

MEMORY_DIR = Path("C:/Users/MuLabs/.openclaw/workspace/memory")
REPORTS_DIR = MEMORY_DIR / "clinical-reports"


def generate_weekly_package():
    """Generate complete weekly report package with organized uploads"""
    print("="*70)
    print("WEEKLY CLINICAL REPORTS PACKAGE (ORGANIZED)")
    print("="*70)
    
    results = {}
    
    # 1. Generate PDF Report
    print("\n[1/3] Generating PDF Clinical Report...")
    print("-"*70)
    pdf_result = save_and_upload_report('weekly')
    
    if pdf_result:
        # Move to organized folder
        print("[UPLOAD] Moving PDF to Clinical/Weekly folder...")
        file_id, link = upload_to_folder(
            pdf_result['local_path'],
            'Clinical',
            'Weekly',
            f"Clinical report for week of {datetime.now().strftime('%Y-%m-%d')}"
        )
        if link:
            results['pdf'] = {
                'drive_link': link,
                'metadata': pdf_result['metadata']
            }
            print(f"[OK] PDF in Clinical/Weekly: {link}")
    else:
        print("[WARN] PDF generation had issues")
    
    # 2. Generate Excel Report
    print("\n[2/3] Generating Excel Evolution Report...")
    print("-"*70)
    excel_result = generate_and_upload_excel_report()
    
    if excel_result:
        # Move to organized folder
        print("[UPLOAD] Moving Excel to Clinical/Weekly folder...")
        file_id, link = upload_to_folder(
            excel_result['filepath'],
            'Clinical',
            'Weekly',
            f"Evolution report with charts for week of {datetime.now().strftime('%Y-%m-%d')}"
        )
        if link:
            results['excel'] = {
                'drive_link': link,
                'metadata': excel_result['metadata']
            }
            print(f"[OK] Excel in Clinical/Weekly: {link}")
    else:
        print("[WARN] Excel generation had issues")
    
    # Summary
    print("\n" + "="*70)
    print("REPORTS PACKAGE COMPLETE - ORGANIZED")
    print("="*70)
    
    # Get folder links
    clinical_weekly = get_folder_id('Clinical', 'Weekly')
    clinical_monthly = get_folder_id('Clinical', 'Monthly')
    
    print(f"\nPDF Report (Clinical/Weekly):")
    print(f"  Sessions: {results.get('pdf', {}).get('metadata', {}).get('total_sessions', 'N/A')}")
    print(f"  Net Margin: EUR {results.get('pdf', {}).get('metadata', {}).get('net_margin', 'N/A')}")
    print(f"  Link: {results.get('pdf', {}).get('drive_link', 'N/A')}")
    
    print(f"\nExcel Evolution (Clinical/Weekly):")
    print(f"  Total Revenue (6mo): EUR {results.get('excel', {}).get('metadata', {}).get('total_revenue', 'N/A')}")
    print(f"  Total Sessions (6mo): {results.get('excel', {}).get('metadata', {}).get('total_sessions', 'N/A')}")
    print(f"  Link: {results.get('excel', {}).get('drive_link', 'N/A')}")
    
    print("\n" + "="*70)
    print("FOLDER STRUCTURE")
    print("="*70)
    print("\nClinical/")
    print("  Weekly/   <- PDF + Excel reports (this week's reports)")
    print("  Monthly/  <- Aggregated monthly reports")
    print("\nFinancial/")
    print("  Weekly/   <- Revenue, invoices, payments")
    print("  Monthly/  <- P&L, balance sheets")
    print("\nTasks/")
    print("  Weekly/   <- Masha & Rafael task summaries")
    print("  Monthly/  <- Team velocity reports")
    print("\nSystem/")
    print("  Daily/    <- Health checks, monitoring")
    print("  Weekly/   <- Performance summaries")
    print("\nMarketing/")
    print("  Weekly/   <- Social media, newsletter stats")
    print("  Monthly/  <- Campaign reports")
    
    print("\n" + "="*70)
    print("[ALL REPORTS ORGANIZED IN GOOGLE DRIVE]")
    print("="*70)
    
    return results


if __name__ == "__main__":
    result = generate_weekly_package()
    if result:
        print(f"\n[COMPLETE] Reports organized and uploaded!")
