#!/usr/bin/env python3
"""
Google Drive Upload Helper for MuBrain Reports
Uploads generated reports to the MuLabs Reports folder
"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import pickle
import json
from datetime import datetime

# Token path
TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'google-drive-token.pickle')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'google-drive-config.json')

def get_drive_service():
    """Authenticate and return Drive service"""
    
    creds = None
    
    # Check if we have saved credentials
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid creds, raise error
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed credentials
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        else:
            raise Exception("Google Drive not authenticated. Run: python automation/setup-google-drive.py")
    
    return build('drive', 'v3', credentials=creds)

def get_reports_folder_id():
    """Get the reports folder ID from config"""
    
    if not os.path.exists(CONFIG_PATH):
        raise Exception("Google Drive config not found. Run: python automation/setup-google-drive.py")
    
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    return config.get('reports_folder_id')

def upload_report(file_path, file_name=None, description=None):
    """
    Upload a report file to Google Drive Reports folder
    
    Args:
        file_path: Path to the file to upload
        file_name: Optional custom name for the file
        description: Optional description for the file
    
    Returns:
        tuple: (file_id, web_view_link)
    """
    
    service = get_drive_service()
    folder_id = get_reports_folder_id()
    
    if not file_name:
        file_name = os.path.basename(file_path)
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    if description:
        file_metadata['description'] = description
    
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    file_id = file.get('id')
    web_link = file.get('webViewLink')
    
    print(f"[OK] Uploaded to Google Drive: {file_name}")
    print(f"  Link: {web_link}")
    
    return file_id, web_link

def upload_report_text(content, file_name, description=None):
    """
    Upload text content as a file to Google Drive
    
    Args:
        content: Text content to upload
        file_name: Name for the file (e.g., 'report.txt')
        description: Optional description
    
    Returns:
        tuple: (file_id, web_view_link)
    """
    
    # Create temp file
    temp_path = os.path.join(os.path.dirname(__file__), 'temp_report.txt')
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    try:
        file_id, web_link = upload_report(temp_path, file_name, description)
        return file_id, web_link
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    # Test upload
    print("Testing Google Drive upload...")
    
    test_content = f"""MuBrain Test Report
Generated: {datetime.now().isoformat()}

This is a test upload to verify Google Drive integration.
"""
    
    try:
        file_id, link = upload_report_text(test_content, f"test-report-{datetime.now().strftime('%Y%m%d')}.txt")
        print(f"\nTest successful!")
        print(f"File ID: {file_id}")
        print(f"Link: {link}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
