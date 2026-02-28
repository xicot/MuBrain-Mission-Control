#!/usr/bin/env python3
"""
Google Drive Reports Organizer
Creates folder structure and manages report uploads by type
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Load Drive config
DRIVE_CONFIG_FILE = Path(__file__).parent / 'google-drive-config.json'
REPORTS_FOLDER_ID = None

if DRIVE_CONFIG_FILE.exists():
    with open(DRIVE_CONFIG_FILE, 'r') as f:
        drive_config = json.load(f)
        REPORTS_FOLDER_ID = drive_config.get('reports_folder_id')

# Folder structure
FOLDER_STRUCTURE = {
    'Clinical': {
        'Weekly': None,
        'Monthly': None
    },
    'Financial': {
        'Weekly': None,
        'Monthly': None
    },
    'System': {
        'Daily': None,
        'Weekly': None
    },
    'Tasks': {
        'Weekly': None,
        'Monthly': None
    },
    'Marketing': {
        'Weekly': None,
        'Monthly': None
    }
}


def get_drive_service():
    """Get Google Drive service"""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import pickle
        
        token_path = Path(__file__).parent / 'google-drive-token.pickle'
        if not token_path.exists():
            print("[ERROR] Token not found")
            return None
        
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"[ERROR] Drive service: {e}")
        return None


def create_folder(service, name, parent_id):
    """Create a folder in Google Drive"""
    try:
        # Check if folder exists
        query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        
        if results['files']:
            return results['files'][0]['id']
        
        # Create new folder
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = service.files().create(body=metadata, fields='id').execute()
        return folder['id']
    except Exception as e:
        print(f"[ERROR] Creating folder {name}: {e}")
        return None


def setup_folder_structure():
    """Create complete folder structure"""
    service = get_drive_service()
    if not service or not REPORTS_FOLDER_ID:
        print("[ERROR] Cannot access Drive")
        return None
    
    print("="*60)
    print("SETTING UP REPORTS FOLDER STRUCTURE")
    print("="*60)
    
    structure = {}
    
    for category, subfolders in FOLDER_STRUCTURE.items():
        print(f"\n[Category] {category}")
        
        # Create main category folder
        cat_folder_id = create_folder(service, category, REPORTS_FOLDER_ID)
        if not cat_folder_id:
            continue
        
        structure[category] = {'id': cat_folder_id, 'subfolders': {}}
        
        # Create subfolders (Weekly/Monthly/Daily)
        for subfolder_name in subfolders.keys():
            sub_id = create_folder(service, subfolder_name, cat_folder_id)
            if sub_id:
                structure[category]['subfolders'][subfolder_name] = sub_id
                print(f"  [OK] {category}/{subfolder_name}: {sub_id}")
    
    # Save structure to config
    config_path = Path(__file__).parent / 'reports-folder-structure.json'
    with open(config_path, 'w') as f:
        json.dump(structure, f, indent=2)
    
    print("\n" + "="*60)
    print("FOLDER STRUCTURE COMPLETE")
    print(f"Config saved: {config_path}")
    print("="*60)
    
    return structure


def get_folder_id(category, period):
    """Get folder ID for a specific category and period"""
    config_path = Path(__file__).parent / 'reports-folder-structure.json'
    
    if not config_path.exists():
        print("[WARN] Folder structure not set up yet. Running setup...")
        setup_folder_structure()
    
    with open(config_path, 'r') as f:
        structure = json.load(f)
    
    return structure.get(category, {}).get('subfolders', {}).get(period)


def upload_to_folder(file_path, category, period, description=""):
    """Upload file to specific folder"""
    from drive_upload_helper import get_drive_service, upload_report
    
    folder_id = get_folder_id(category, period)
    if not folder_id:
        print(f"[ERROR] Folder not found: {category}/{period}")
        return None, None
    
    # Use drive_upload_helper but with specific folder
    service = get_drive_service()
    if not service:
        return None, None
    
    try:
        from googleapiclient.http import MediaFileUpload
        
        file_path = Path(file_path)
        
        file_metadata = {
            'name': file_path.name,
            'parents': [folder_id],
            'description': description
        }
        
        # Determine mime type
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        if file_path.suffix == '.pdf':
            mime_type = 'application/pdf'
        elif file_path.suffix == '.html':
            mime_type = 'text/html'
        elif file_path.suffix == '.txt':
            mime_type = 'text/plain'
        
        media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return file['id'], file['webViewLink']
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return None, None


if __name__ == "__main__":
    setup_folder_structure()
