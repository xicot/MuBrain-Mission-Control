#!/usr/bin/env python3
"""
Tasks & Team Reports Generator
Creates team productivity and task tracking reports
Uploads to Tasks/Weekly or Tasks/Monthly folders
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

def generate_tasks_report(period='weekly'):
    """Generate tasks/team report for specified period"""
    print("="*70)
    print(f"GENERATING {period.upper()} TASKS & TEAM REPORT")
    print("="*70)
    
    today = datetime.now()
    
    # Load data
    print("\n[Loading Team Data...]")
    
    # Team velocity
    velocity = load_json_file(MEMORY_DIR / "team-velocity.json", {})
    print(f"  [OK] Velocity data loaded")
    
    # Waiting on tracker
    waiting = load_json_file(MEMORY_DIR / "waiting-on.json", {})
    print(f"  [OK] Waiting items: {len(waiting.get('blocked_items', []))}")
    
    # Clockify time tracking
    clockify = load_json_file(STATUS_DIR / "clockify.json", {})
    print(f"  [OK] Clockify data loaded")
    
    # Task board
    task_board = load_json_file(MEMORY_DIR / "task-board.json", {})
    
    # Calculate metrics
    masha_completed = velocity.get('masha_completed', 0)
    masha_total = velocity.get('masha_total', 0)
    masha_rate = velocity.get('masha_completion_rate', 0)
    
    rafael_completed = velocity.get('rafael_completed', 0)
    rafael_total = velocity.get('rafael_total', 0)
    rafael_rate = velocity.get('rafael_completion_rate', 0)
    
    total_hours = clockify.get('total_hours_this_week', 0)
    
    print(f"\n  Masha: {masha_completed}/{masha_total} ({masha_rate}%)")
    print(f"  Rafael: {rafael_completed}/{rafael_total} ({rafael_rate}%)")
    
    # Generate HTML report
    print("\n[Generating HTML Report...]")
    
    period_label = "Week" if period == 'weekly' else "Month"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MuLabs Team & Tasks Report - {period_label} of {today.strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #0f172a;
            color: #e2e8f0;
        }}
        h1 {{ color: #8b5cf6; border-bottom: 2px solid #8b5cf6; padding-bottom: 10px; }}
        h2 {{ color: #a78bfa; margin-top: 30px; border-left: 4px solid #8b5cf6; padding-left: 15px; }}
        .header {{
            background: linear-gradient(135deg, #4c1d95 0%, #0f172a 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid #8b5cf6;
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
            color: #8b5cf6;
        }}
        .metric-label {{
            color: #94a3b8;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .team-member {{
            background: #1e293b;
            padding: 25px;
            border-radius: 10px;
            margin: 15px 0;
            border: 1px solid #334155;
        }}
        .team-name {{
            font-size: 1.5em;
            font-weight: bold;
            color: #a78bfa;
            margin-bottom: 15px;
        }}
        .progress-bar {{
            background: #334155;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #8b5cf6, #a78bfa);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s;
        }}
        .section {{
            background: #1e293b;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #334155;
        }}
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
        th {{ color: #94a3b8; font-weight: 600; background: #0f172a; }}
        .footer {{
            text-align: center;
            color: #64748b;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }}
        .status-good {{ color: #10b981; }}
        .status-warn {{ color: #fbbf24; }}
        .status-bad {{ color: #f87171; }}
        .highlight {{
            background: #4c1d95;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #8b5cf6;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>👥 MuLabs Team & Tasks Report</h1>
        <p>Period: {period_label} of {today.strftime('%B %d, %Y')}</p>
        <p style="color: #94a3b8;">Team velocity, task completion, and productivity metrics</p>
    </div>

    <h2>Team Overview</h2>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{masha_rate}%</div>
            <div class="metric-label">Masha Completion</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{rafael_rate}%</div>
            <div class="metric-label">Rafael Completion</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{total_hours:.1f}h</div>
            <div class="metric-label">Total Hours Tracked</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(waiting.get('blocked_items', []))}</div>
            <div class="metric-label">Blocked Items</div>
        </div>
    </div>

    <h2>Team Members</h2>
    
    <div class="team-member">
        <div class="team-name">Masha - Operations</div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span>Tasks Completed: <strong>{masha_completed}/{masha_total}</strong></span>
            <span class="{('status-good' if masha_rate >= 80 else 'status-warn' if masha_rate >= 50 else 'status-bad')}">{masha_rate}%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {masha_rate}%"></div>
        </div>
        <p style="color: #94a3b8; margin-top: 10px;">
            Cross-functional operations across MuHealth, MuConsultancy, and MuEducation.
            Handles accounting, admin, scheduling, social media, and newsletters.
        </p>
    </div>

    <div class="team-member">
        <div class="team-name">Rafael - MuConsultancy</div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span>Tasks Completed: <strong>{rafael_completed}/{rafael_total}</strong></span>
            <span class="{('status-good' if rafael_rate >= 80 else 'status-warn' if rafael_rate >= 50 else 'status-bad')}">{rafael_rate}%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {rafael_rate}%"></div>
        </div>
        <p style="color: #94a3b8; margin-top: 10px;">
            Research specialist for MuConsultancy. Handles research, data analysis, 
            writing, client materials, and literature reviews.
        </p>
    </div>

    <h2>Time Tracking (Clockify)</h2>
    <div class="section">
        <table>
            <tr>
                <th>Project</th>
                <th>Hours</th>
                <th>Percentage</th>
            </tr>
            <tr>
                <td>Administração & Marcações (Masha)</td>
                <td>{clockify.get('projects', {}).get('Administração & Marcações', 0):.1f}h</td>
                <td>--</td>
            </tr>
            <tr>
                <td>Clínica & Operações (Vanessa)</td>
                <td>{clockify.get('projects', {}).get('Clínica & Operações', 0):.1f}h</td>
                <td>--</td>
            </tr>
            <tr>
                <td>Consultoria (Rafael)</td>
                <td>{clockify.get('projects', {}).get('Consultoria', 0):.1f}h</td>
                <td>--</td>
            </tr>
            <tr>
                <td>Direção Clínica (Xico)</td>
                <td>{clockify.get('projects', {}).get('Direção Clínica', 0):.1f}h</td>
                <td>--</td>
            </tr>
            <tr style="background: #0f172a; font-weight: bold;">
                <td>Total</td>
                <td>{total_hours:.1f}h</td>
                <td>100%</td>
            </tr>
        </table>
    </div>

    <h2>Blocked / Waiting On</h2>
    <div class="section">
        <table>
            <tr>
                <th>Task</th>
                <th>Waiting For</th>
                <th>Status</th>
            </tr>
"""
    
    for item in waiting.get('blocked_items', [])[:10]:
        html_content += f"""
            <tr>
                <td>{item.get('task', 'Unknown')}</td>
                <td>{item.get('waiting_for', 'Unknown')}</td>
                <td class="status-warn">⏳ {item.get('days', 0)} days</td>
            </tr>
"""
    
    if not waiting.get('blocked_items'):
        html_content += '<tr><td colspan="3" style="text-align:center;color:#10b981;">No blocked items - Team is unblocked! 🎉</td></tr>'
    
    html_content += f"""
        </table>
    </div>

    <div class="highlight">
        <strong>Weekly Insights:</strong>
        <ul>
            <li>Team completion rate: {((masha_rate + rafael_rate) / 2):.1f}% average</li>
            <li>Total hours logged: {total_hours:.1f}h</li>
            <li>Blocked items: {len(waiting.get('blocked_items', []))} (review recommended)</li>
            <li>Productivity trend: {'Improving' if masha_rate + rafael_rate > 120 else 'Stable' if masha_rate + rafael_rate > 80 else 'Needs attention'}</li>
        </ul>
    </div>

    <div class="footer">
        <p>MuLabs Team Management | Generated by MuBrain</p>
        <p>Report covers {period_label.lower()} period ending {today.strftime('%Y-%m-%d')}</p>
    </div>
</body>
</html>
"""
    
    # Save locally
    report_path = MEMORY_DIR / f"tasks-team-report-{period}-{today.strftime('%Y-%m-%d')}.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  [OK] Report saved: {report_path}")
    
    # Upload to Drive
    print(f"\n[Uploading to Tasks/{period.capitalize()} folder...]")
    folder_period = 'Weekly' if period == 'weekly' else 'Monthly'
    file_id, link = upload_to_folder(
        report_path,
        'Tasks',
        folder_period,
        f"Tasks & Team {period} report - {today.strftime('%Y-%m-%d')}"
    )
    
    if link:
        print(f"  [OK] Uploaded: {link}")
    
    print("\n" + "="*70)
    print(f"TASKS & TEAM {period.upper()} REPORT COMPLETE")
    print("="*70)
    
    return {'local_path': str(report_path), 'drive_link': link}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('period', nargs='?', default='weekly', choices=['weekly', 'monthly'])
    args = parser.parse_args()
    
    result = generate_tasks_report(args.period)
    if result:
        print(f"\nReport available at: {result['drive_link']}")
