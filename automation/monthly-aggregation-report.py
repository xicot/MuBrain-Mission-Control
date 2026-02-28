#!/usr/bin/env python3
"""
Monthly Aggregation Report
Aggregates all monthly data across all categories
Uploads to Monthly folders
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from calendar import monthrange

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

def generate_monthly_aggregation():
    """Generate comprehensive monthly aggregation report"""
    print("="*70)
    print("GENERATING MONTHLY AGGREGATION REPORT")
    print("="*70)
    
    today = datetime.now()
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])
    days_in_month = monthrange(today.year, today.month)[1]
    
    print(f"\n[Period: {today.strftime('%B %Y')}]")
    print(f"  From: {first_day.strftime('%Y-%m-%d')}")
    print(f"  To: {last_day.strftime('%Y-%m-%d')}")
    
    # Collect all data
    print("\n[Collecting Monthly Data...]")
    
    # Clinical data
    clinical_manifest = load_json_file(MEMORY_DIR / "clinical-reports" / "reports-manifest.json", {})
    monthly_revenue = 0
    monthly_sessions = 0
    for report in clinical_manifest.get('reports', []):
        try:
            report_date = datetime.strptime(report.get('date', ''), '%Y-%m-%d')
            if report_date.month == today.month and report_date.year == today.year:
                metadata = report.get('metadata', {})
                monthly_revenue += metadata.get('net_margin', 0)
                monthly_sessions += metadata.get('total_sessions', 0)
        except:
            pass
    
    print(f"  [OK] Clinical: EUR {monthly_revenue} from {monthly_sessions} sessions")
    
    # Team metrics
    velocity = load_json_file(MEMORY_DIR / "team-velocity.json", {})
    masha_rate = velocity.get('masha_completion_rate', 0)
    rafael_rate = velocity.get('rafael_completion_rate', 0)
    avg_completion = (masha_rate + rafael_rate) / 2
    
    print(f"  [OK] Team completion: {avg_completion:.1f}% average")
    
    # Costs
    costs = load_json_file(MEMORY_DIR / "cost-tracking.json", {})
    monthly_costs = costs.get('monthly_spend', 0)
    
    print(f"  [OK] Costs: ${monthly_costs:.2f}")
    
    # Patterns detected
    patterns = load_json_file(MEMORY_DIR / "patterns.json", {})
    patterns_count = len(patterns.get('detected', []))
    
    print(f"  [OK] Patterns: {patterns_count} detected")
    
    # Generate comprehensive HTML report
    print("\n[Generating HTML Report...]")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MuLabs Monthly Aggregation - {today.strftime('%B %Y')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #0f172a;
            color: #e2e8f0;
        }}
        h1 {{ color: #f472b6; border-bottom: 2px solid #f472b6; padding-bottom: 10px; }}
        h2 {{ color: #f9a8d4; margin-top: 30px; border-left: 4px solid #f472b6; padding-left: 15px; }}
        h3 {{ color: #60a5fa; margin-top: 20px; }}
        .header {{
            background: linear-gradient(135deg, #831843 0%, #0f172a 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid #f472b6;
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
            color: #f472b6;
        }}
        .metric-label {{
            color: #94a3b8;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .section {{
            background: #1e293b;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #334155;
        }}
        .category {{
            background: #0f172a;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #f472b6;
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
        .revenue {{ color: #10b981; }}
        .cost {{ color: #f87171; }}
        .profit {{ color: #60a5fa; }}
        .footer {{
            text-align: center;
            color: #64748b;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }}
        .highlight {{
            background: #831843;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #f472b6;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📅 MuLabs Monthly Aggregation</h1>
        <p>Period: {today.strftime('%B %Y')}</p>
        <p style="color: #94a3b8;">Comprehensive monthly summary across all verticals</p>
    </div>

    <h2>Executive Summary</h2>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value revenue">EUR {monthly_revenue}</div>
            <div class="metric-label">Monthly Revenue</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{monthly_sessions}</div>
            <div class="metric-label">Total Sessions</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{avg_completion:.0f}%</div>
            <div class="metric-label">Team Completion Rate</div>
        </div>
        <div class="metric-card">
            <div class="metric-value cost">${monthly_costs:.0f}</div>
            <div class="metric-label">Monthly Costs</div>
        </div>
        <div class="metric-card">
            <div class="metric-value profit">EUR {monthly_revenue - monthly_costs:.0f}</div>
            <div class="metric-label">Net Profit</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{patterns_count}</div>
            <div class="metric-label">Patterns Detected</div>
        </div>
    </div>

    <h2>By Category</h2>
    
    <div class="category">
        <h3>💰 Financial</h3>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Notes</th>
            </tr>
            <tr>
                <td>Gross Revenue</td>
                <td class="revenue">EUR {monthly_revenue}</td>
                <td>From clinical sessions</td>
            </tr>
            <tr>
                <td>Operating Costs</td>
                <td class="cost">${monthly_costs:.2f}</td>
                <td>AI tools, services</td>
            </tr>
            <tr>
                <td>Net Profit</td>
                <td class="profit">EUR {monthly_revenue - monthly_costs:.2f}</td>
                <td>After costs</td>
            </tr>
            <tr>
                <td>Profit Margin</td>
                <td>{((monthly_revenue - monthly_costs) / monthly_revenue * 100) if monthly_revenue > 0 else 0:.1f}%</td>
                <td>Revenue vs costs</td>
            </tr>
        </table>
    </div>

    <div class="category">
        <h3>🏥 Clinical (MuHealth)</h3>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Per Day Avg</th>
            </tr>
            <tr>
                <td>Total Sessions</td>
                <td>{monthly_sessions}</td>
                <td>{monthly_sessions / days_in_month:.1f}</td>
            </tr>
            <tr>
                <td>Revenue</td>
                <td>EUR {monthly_revenue}</td>
                <td>EUR {monthly_revenue / days_in_month:.0f}</td>
            </tr>
            <tr>
                <td>Avg per Session</td>
                <td>EUR {monthly_revenue / monthly_sessions if monthly_sessions > 0 else 0:.2f}</td>
                <td>-</td>
            </tr>
        </table>
    </div>

    <div class="category">
        <h3>👥 Team Performance</h3>
        <table>
            <tr>
                <th>Team Member</th>
                <th>Completion Rate</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Masha (Operations)</td>
                <td>{masha_rate}%</td>
                <td>{'Excellent' if masha_rate >= 80 else 'Good' if masha_rate >= 60 else 'Needs Attention'}</td>
            </tr>
            <tr>
                <td>Rafael (Consultancy)</td>
                <td>{rafael_rate}%</td>
                <td>{'Excellent' if rafael_rate >= 80 else 'Good' if rafael_rate >= 60 else 'Needs Attention'}</td>
            </tr>
            <tr style="background: #0f172a; font-weight: bold;">
                <td>Team Average</td>
                <td>{avg_completion:.1f}%</td>
                <td>{'Excellent' if avg_completion >= 80 else 'Good' if avg_completion >= 60 else 'Needs Attention'}</td>
            </tr>
        </table>
    </div>

    <h2>Monthly Insights</h2>
    <div class="highlight">
        <strong>Key Takeaways:</strong>
        <ul>
            <li>Revenue per day: EUR {monthly_revenue / days_in_month:.0f} average</li>
            <li>Sessions per day: {monthly_sessions / days_in_month:.1f} average</li>
            <li>Cost efficiency: ${monthly_costs / monthly_sessions if monthly_sessions > 0 else 0:.2f} per session</li>
            <li>Team productivity: {avg_completion:.0f}% task completion rate</li>
            <li>Profitability: {((monthly_revenue - monthly_costs) / monthly_revenue * 100) if monthly_revenue > 0 else 0:.0f}% margin</li>
        </ul>
    </div>

    <h2>Trends & Patterns</h2>
    <div class="section">
        <p><strong>Patterns Detected This Month:</strong> {patterns_count}</p>
        <ul>
"""
    
    for pattern in patterns.get('detected', [])[:5]:
        html_content += f"<li>{pattern.get('description', 'Unknown pattern')}</li>"
    
    if not patterns.get('detected'):
        html_content += "<li style='color:#64748b;'>No significant patterns detected this month</li>"
    
    html_content += f"""
        </ul>
    </div>

    <h2>Goals vs Reality</h2>
    <div class="section">
        <table>
            <tr>
                <th>Goal</th>
                <th>Target</th>
                <th>Actual</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Monthly Revenue</td>
                <td>EUR {(monthly_revenue * 1.2):.0f}</td>
                <td>EUR {monthly_revenue}</td>
                <td>{'On Track' if monthly_revenue > 0 else 'Needs Work'}</td>
            </tr>
            <tr>
                <td>Team Completion</td>
                <td>85%</td>
                <td>{avg_completion:.0f}%</td>
                <td>{'On Track' if avg_completion >= 85 else 'Below Target'}</td>
            </tr>
            <tr>
                <td>Cost Control</td>
                <td>${monthly_revenue * 0.1:.0f}</td>
                <td>${monthly_costs:.0f}</td>
                <td>{'On Track' if monthly_costs < monthly_revenue * 0.1 else 'Over Budget'}</td>
            </tr>
        </table>
    </div>

    <div class="footer">
        <p>MuLabs Monthly Review | Generated by MuBrain</p>
        <p>Report covers {today.strftime('%B %Y')} (complete month)</p>
    </div>
</body>
</html>
"""
    
    # Save locally
    report_path = MEMORY_DIR / f"monthly-aggregation-{today.strftime('%Y-%m')}.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  [OK] Report saved: {report_path}")
    
    # Upload to all monthly folders for visibility
    print("\n[Uploading to Monthly folders...]")
    
    uploaded_links = []
    for category in ['Clinical', 'Financial', 'Tasks', 'System']:
        file_id, link = upload_to_folder(
            report_path,
            category,
            'Monthly',
            f"Monthly aggregation report - {today.strftime('%B %Y')}"
        )
        if link:
            uploaded_links.append((category, link))
            print(f"  [OK] {category}/Monthly: {link}")
    
    print("\n" + "="*70)
    print("MONTHLY AGGREGATION REPORT COMPLETE")
    print("="*70)
    
    return {
        'local_path': str(report_path),
        'uploaded_to': uploaded_links
    }

if __name__ == "__main__":
    result = generate_monthly_aggregation()
    if result:
        print(f"\nReport uploaded to {len(result['uploaded_to'])} folders")
        for cat, link in result['uploaded_to']:
            print(f"  - {cat}/Monthly")
