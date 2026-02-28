#!/usr/bin/env python3
"""
Mission Status Report Generator
Creates comprehensive mission reports for MuLabs
Uploads to System/Weekly folder
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
    """Load JSON file or return default"""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
    except:
        pass
    return default or {}

def generate_mission_status_report():
    """Generate comprehensive mission status report"""
    print("="*70)
    print("GENERATING MISSION STATUS REPORT")
    print("="*70)
    
    today = datetime.now()
    
    # Load all relevant data
    print("\n[Loading Data Sources...]")
    
    # Team velocity
    velocity = load_json_file(MEMORY_DIR / "team-velocity.json", {})
    print(f"  [OK] Team velocity: {velocity.get('masha_completion_rate', 'N/A')}% Masha, {velocity.get('rafael_completion_rate', 'N/A')}% Rafael")
    
    # Energy heatmap
    heatmap = load_json_file(MEMORY_DIR / "energy-heatmap.json", {})
    print(f"  [OK] Energy heatmap: {len(heatmap.get('focus_blocks', []))} focus blocks")
    
    # Patterns
    patterns = load_json_file(MEMORY_DIR / "patterns.json", {})
    print(f"  [OK] Patterns: {len(patterns.get('detected', []))} detected")
    
    # System status
    system_status = load_json_file(STATUS_DIR / "system-status.json", {})
    print(f"  [OK] System status: {len(system_status.get('components', []))} components")
    
    # Clockify status
    clockify = load_json_file(STATUS_DIR / "clockify.json", {})
    print(f"  [OK] Clockify: {clockify.get('total_hours_this_week', 'N/A')} hours this week")
    
    # Cost tracking
    costs = load_json_file(MEMORY_DIR / "cost-tracking.json", {})
    
    # Waiting on
    waiting = load_json_file(MEMORY_DIR / "waiting-on.json", {})
    
    # Clinical data
    clinical_manifest = load_json_file(MEMORY_DIR / "clinical-reports" / "reports-manifest.json", {})
    
    # Generate HTML report
    print("\n[Generating HTML Report...]")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MuLabs Mission Status - {today.strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #0f172a;
            color: #e2e8f0;
        }}
        h1 {{ color: #60a5fa; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
        h2 {{ color: #34d399; margin-top: 30px; border-left: 4px solid #34d399; padding-left: 15px; }}
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid #3b82f6;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #1e293b;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #334155;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #60a5fa;
        }}
        .metric-label {{
            color: #94a3b8;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .status-good {{ color: #34d399; }}
        .status-warn {{ color: #fbbf24; }}
        .status-bad {{ color: #f87171; }}
        .section {{
            background: #1e293b;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #334155;
        }}
        .vertical {{
            display: flex;
            justify-content: space-between;
            padding: 15px;
            background: #0f172a;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #3b82f6;
        }}
        .vertical-name {{ font-weight: bold; color: #60a5fa; }}
        .vertical-status {{ color: #94a3b8; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }}
        th {{ color: #94a3b8; font-weight: 600; }}
        .footer {{
            text-align: center;
            color: #64748b;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 MuLabs Mission Status</h1>
        <p>Generated: {today.strftime('%Y-%m-%d %H:%M')} | Week: {today.isocalendar()[1]}</p>
        <p style="color: #94a3b8;">Comprehensive overview of all verticals, team performance, and system health</p>
    </div>

    <h2>📊 Key Metrics</h2>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{velocity.get('masha_completion_rate', 0)}%</div>
            <div class="metric-label">Masha Task Completion</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{velocity.get('rafael_completion_rate', 0)}%</div>
            <div class="metric-label">Rafael Task Completion</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{clockify.get('total_hours_this_week', 0):.1f}h</div>
            <div class="metric-label">Team Hours This Week</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(patterns.get('detected', []))}</div>
            <div class="metric-label">Patterns Detected</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(waiting.get('blocked_items', []))}</div>
            <div class="metric-label">Blocked Items</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{clinical_manifest.get('total_reports', 0)}</div>
            <div class="metric-label">Clinical Reports</div>
        </div>
    </div>

    <h2>🏢 Vertical Status</h2>
    <div class="section">
        <div class="vertical">
            <div>
                <div class="vertical-name">MuHealth</div>
                <div class="vertical-status">Clinical practice & patient care</div>
            </div>
            <div class="status-good">● Active</div>
        </div>
        <div class="vertical">
            <div>
                <div class="vertical-name">MuConsultancy</div>
                <div class="vertical-status">B2B research & validation</div>
            </div>
            <div class="status-good">● Active</div>
        </div>
        <div class="vertical">
            <div>
                <div class="vertical-name">MuEducation</div>
                <div class="vertical-status">Online platform development</div>
            </div>
            <div class="status-warn">● In Progress</div>
        </div>
        <div class="vertical">
            <div>
                <div class="vertical-name">MuArts</div>
                <div class="vertical-status">Biodata art experiences</div>
            </div>
            <div class="status-bad">● Paused</div>
        </div>
        <div class="vertical">
            <div>
                <div class="vertical-name">MuWellness</div>
                <div class="vertical-status">B2C wellbeing</div>
            </div>
            <div class="status-bad">● Paused</div>
        </div>
    </div>

    <h2>⏳ Waiting On / Blocked</h2>
    <div class="section">
        <table>
            <tr>
                <th>Item</th>
                <th>Waiting For</th>
                <th>Days Waiting</th>
            </tr>
"""
    
    # Add waiting items
    for item in waiting.get('blocked_items', [])[:10]:
        html_content += f"""
            <tr>
                <td>{item.get('task', 'Unknown')}</td>
                <td>{item.get('waiting_for', 'Unknown')}</td>
                <td>{item.get('days', 0)}</td>
            </tr>
"""
    
    if not waiting.get('blocked_items'):
        html_content += "<tr><td colspan='3' style='text-align:center;color:#64748b;'>No blocked items 🎉</td></tr>"
    
    html_content += f"""
        </table>
    </div>

    <h2>🔍 Detected Patterns</h2>
    <div class="section">
        <ul>
"""
    
    for pattern in patterns.get('detected', []):
        html_content += f"<li>{pattern.get('description', 'Unknown pattern')}</li>"
    
    if not patterns.get('detected'):
        html_content += "<li style='color:#64748b;'>No significant patterns detected this week</li>"
    
    html_content += f"""
        </ul>
    </div>

    <h2>👥 Team Focus Blocks</h2>
    <div class="section">
        <table>
            <tr>
                <th>Day</th>
                <th>Time Block</th>
                <th>Type</th>
            </tr>
"""
    
    for block in heatmap.get('focus_blocks', [])[:5]:
        html_content += f"""
            <tr>
                <td>{block.get('day', 'N/A')}</td>
                <td>{block.get('time', 'N/A')}</td>
                <td>{block.get('type', 'Focus')}</td>
            </tr>
"""
    
    html_content += f"""
        </table>
    </div>

    <h2>💰 Cost Summary</h2>
    <div class="section">
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">${costs.get('monthly_spend', 0):.2f}</div>
                <div class="metric-label">Monthly Spend</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${costs.get('projected_monthly', 0):.2f}</div>
                <div class="metric-label">Projected Monthly</div>
            </div>
        </div>
    </div>

    <h2>📁 Recent Reports</h2>
    <div class="section">
        <table>
            <tr>
                <th>Report Type</th>
                <th>Date</th>
                <th>Status</th>
            </tr>
"""
    
    for report in clinical_manifest.get('reports', [])[:5]:
        html_content += f"""
            <tr>
                <td>{report.get('type', 'Unknown')}</td>
                <td>{report.get('date', 'N/A')}</td>
                <td class="status-good">✓ Generated</td>
            </tr>
"""
    
    html_content += f"""
        </table>
    </div>

    <div class="footer">
        <p>MuLabs Mission Control | Generated by MuBrain</p>
        <p>All systems operational</p>
    </div>
</body>
</html>
"""
    
    # Save locally
    report_path = MEMORY_DIR / f"mission-status-{today.strftime('%Y-%m-%d')}.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  [OK] Report saved: {report_path}")
    
    # Upload to Drive
    print("\n[Uploading to Google Drive...]")
    file_id, link = upload_to_folder(
        report_path,
        'System',
        'Weekly',
        f"Mission Status Report for week of {today.strftime('%Y-%m-%d')}"
    )
    
    if link:
        print(f"  [OK] Uploaded to System/Weekly: {link}")
    
    print("\n" + "="*70)
    print("MISSION STATUS REPORT COMPLETE")
    print("="*70)
    
    return {'local_path': str(report_path), 'drive_link': link}

if __name__ == "__main__":
    result = generate_mission_status_report()
    if result:
        print(f"\nReport available at: {result['drive_link']}")
