#!/usr/bin/env python3
"""
Financial Reports Generator
Creates comprehensive financial reports for MuLabs
Uploads to Financial/Weekly or Financial/Monthly folders
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

def generate_financial_report(period='weekly'):
    """Generate financial report for specified period"""
    print("="*70)
    print(f"GENERATING {period.upper()} FINANCIAL REPORT")
    print("="*70)
    
    today = datetime.now()
    
    # Load data sources
    print("\n[Loading Financial Data...]")
    
    # Clinical data (revenue source)
    clinical_manifest = load_json_file(MEMORY_DIR / "clinical-reports" / "reports-manifest.json", {})
    reports = clinical_manifest.get('reports', [])
    
    # Cost tracking
    costs = load_json_file(MEMORY_DIR / "cost-tracking.json", {})
    
    # Calculate revenue
    total_revenue = 0
    total_sessions = 0
    xico_revenue = 0
    vanessa_revenue = 0
    
    # Get period range
    if period == 'weekly':
        start_date = today - timedelta(days=7)
    else:  # monthly
        start_date = today - timedelta(days=30)
    
    for report in reports:
        if report.get('type') == 'clinical_weekly':
            metadata = report.get('metadata', {})
            date_str = report.get('date', '')
            try:
                report_date = datetime.strptime(date_str, '%Y-%m-%d')
                if report_date >= start_date:
                    total_revenue += metadata.get('net_margin', 0)
                    total_sessions += metadata.get('total_sessions', 0)
            except:
                pass
    
    print(f"  [OK] Revenue calculated: EUR {total_revenue}")
    print(f"  [OK] Sessions tracked: {total_sessions}")
    
    # Load Airtable cache for detailed session data
    airtable_cache = load_json_file(MEMORY_DIR / "airtable-sessions-cache.json", {})
    sessions = airtable_cache.get('sessions', [])
    
    # Calculate by facilitator
    xico_sessions = 0
    vanessa_sessions = 0
    
    for session in sessions:
        facilitator = session.get('Facilitador', '')
        if 'Xico' in facilitator or 'Francisco' in facilitator:
            xico_sessions += 1
        elif 'Vanessa' in facilitator or 'VA' in facilitator:
            vanessa_sessions += 1
    
    print(f"  [OK] Xico sessions: {xico_sessions}")
    print(f"  [OK] Vanessa sessions: {vanessa_sessions}")
    
    # Calculate costs
    monthly_costs = costs.get('monthly_spend', 0)
    projected = costs.get('projected_monthly', 0)
    
    print(f"  [OK] Monthly costs: ${monthly_costs}")
    
    # Generate HTML report
    print("\n[Generating HTML Report...]")
    
    period_label = "Week" if period == 'weekly' else "Month"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MuLabs Financial Report - {period_label} of {today.strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #0f172a;
            color: #e2e8f0;
        }}
        h1 {{ color: #10b981; border-bottom: 2px solid #10b981; padding-bottom: 10px; }}
        h2 {{ color: #34d399; margin-top: 30px; border-left: 4px solid #10b981; padding-left: 15px; }}
        .header {{
            background: linear-gradient(135deg, #064e3b 0%, #0f172a 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid #10b981;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
            font-size: 2.2em;
            font-weight: bold;
            color: #10b981;
        }}
        .metric-label {{
            color: #94a3b8;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .revenue {{ color: #10b981; }}
        .cost {{ color: #f87171; }}
        .profit {{ color: #60a5fa; }}
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
        .positive {{ color: #10b981; }}
        .negative {{ color: #f87171; }}
        .footer {{
            text-align: center;
            color: #64748b;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }}
        .highlight {{
            background: #064e3b;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #10b981;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>💰 MuLabs Financial Report</h1>
        <p>Period: {period_label} of {today.strftime('%B %d, %Y')}</p>
        <p style="color: #94a3b8;">Revenue, costs, and profitability analysis</p>
    </div>

    <h2>Revenue Summary</h2>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value revenue">EUR {total_revenue}</div>
            <div class="metric-label">Total Revenue ({period_label})</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{total_sessions}</div>
            <div class="metric-label">Total Sessions</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">EUR {total_revenue / total_sessions if total_sessions > 0 else 0:.2f}</div>
            <div class="metric-label">Average per Session</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">EUR {total_revenue * 4 if period == 'weekly' else total_revenue}</div>
            <div class="metric-label">Projected Monthly</div>
        </div>
    </div>

    <h2>By Facilitator</h2>
    <div class="section">
        <table>
            <tr>
                <th>Facilitator</th>
                <th>Sessions</th>
                <th>Revenue Share</th>
                <th>Percentage</th>
            </tr>
            <tr>
                <td><strong>Xico (Dr. FMT)</strong></td>
                <td>{xico_sessions}</td>
                <td>EUR {xico_sessions * 75}</td>
                <td>{(xico_sessions / (xico_sessions + vanessa_sessions) * 100) if (xico_sessions + vanessa_sessions) > 0 else 0:.1f}%</td>
            </tr>
            <tr>
                <td><strong>Vanessa (Dr. VA)</strong></td>
                <td>{vanessa_sessions}</td>
                <td>EUR {vanessa_sessions * 47}</td>
                <td>{(vanessa_sessions / (xico_sessions + vanessa_sessions) * 100) if (xico_sessions + vanessa_sessions) > 0 else 0:.1f}%</td>
            </tr>
        </table>
    </div>

    <h2>Cost Analysis</h2>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value cost">${monthly_costs:.2f}</div>
            <div class="metric-label">Monthly AI/Tool Costs</div>
        </div>
        <div class="metric-card">
            <div class="metric-value cost">${projected:.2f}</div>
            <div class="metric-label">Projected Monthly</div>
        </div>
        <div class="metric-card">
            <div class="metric-value profit">EUR {total_revenue - monthly_costs:.2f}</div>
            <div class="metric-label">Net ({period_label})</div>
        </div>
    </div>

    <h2>Profit & Loss ({period_label})</h2>
    <div class="section">
        <table>
            <tr>
                <th>Category</th>
                <th>Amount</th>
                <th>Notes</th>
            </tr>
            <tr>
                <td>Clinical Revenue</td>
                <td class="positive">+ EUR {total_revenue}</td>
                <td>Patient sessions</td>
            </tr>
            <tr>
                <td>Operating Costs</td>
                <td class="negative">- ${monthly_costs:.2f}</td>
                <td>AI tools, services</td>
            </tr>
            <tr style="background: #0f172a; font-weight: bold;">
                <td>Net Profit</td>
                <td class="{('positive' if (total_revenue - monthly_costs) > 0 else 'negative')}">EUR {total_revenue - monthly_costs:.2f}</td>
                <td>After costs</td>
            </tr>
        </table>
    </div>

    <div class="highlight">
        <strong>Key Insights:</strong>
        <ul>
            <li>Revenue per session: EUR {total_revenue / total_sessions if total_sessions > 0 else 0:.2f}</li>
            <li>Cost per session: ${monthly_costs / total_sessions if total_sessions > 0 else 0:.2f}</li>
            <li>Net margin: {((total_revenue - monthly_costs) / total_revenue * 100) if total_revenue > 0 else 0:.1f}%</li>
        </ul>
    </div>

    <div class="footer">
        <p>MuLabs Financial Department | Generated by MuBrain</p>
        <p>Report covers {period_label.lower()} period ending {today.strftime('%Y-%m-%d')}</p>
    </div>
</body>
</html>
"""
    
    # Save locally
    report_path = MEMORY_DIR / f"financial-report-{period}-{today.strftime('%Y-%m-%d')}.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  [OK] Report saved: {report_path}")
    
    # Upload to Drive
    print(f"\n[Uploading to Financial/{period.capitalize()} folder...]")
    folder_period = 'Weekly' if period == 'weekly' else 'Monthly'
    file_id, link = upload_to_folder(
        report_path,
        'Financial',
        folder_period,
        f"Financial {period} report - {today.strftime('%Y-%m-%d')}"
    )
    
    if link:
        print(f"  [OK] Uploaded: {link}")
    
    print("\n" + "="*70)
    print(f"FINANCIAL {period.upper()} REPORT COMPLETE")
    print("="*70)
    
    return {'local_path': str(report_path), 'drive_link': link}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('period', nargs='?', default='weekly', choices=['weekly', 'monthly'])
    args = parser.parse_args()
    
    result = generate_financial_report(args.period)
    if result:
        print(f"\nReport available at: {result['drive_link']}")
