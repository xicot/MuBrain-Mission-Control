#!/usr/bin/env python3
"""
Activity-Based Hour Estimator for MuLabs Team
Combines WhatsApp, Calendar, Email, and Clockify data to estimate hours worked.

Estimation Rules:
- WhatsApp: 1 message ≈ 2 minutes (reading + response time)
- Calendar events: Actual duration (if marked busy/meeting)
- Emails: 1 email ≈ 5 minutes (reading + response)
- Calls: Actual duration from calendar/notes
- Clockify: Real tracked time (if available)

Output: Weekly estimated hours per person
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Activity multipliers (minutes per activity)
MULTIPLIERS = {
    'whatsapp_message': 2,      # 2 min per message
    'email': 5,                  # 5 min per email
    'calendar_event': 1,         # 1x actual duration (minutes)
    'clockify_minute': 1         # 1x actual tracked minutes
}

# Team members and their identifiers
TEAM = {
    'Xico': {
        'whatsapp_ids': ['947053818'],  # Your WhatsApp ID
        'emails': ['francisco.ma.teixeira@gmail.com'],
        'calendar_keywords': ['Xico', 'Francisco', 'Dr. FMT'],
        'clockify_projects': ['Direção Clínica', 'MuLabs']
    },
    'Masha': {
        'whatsapp_ids': ['351967709683'],
        'emails': ['highmashion22@gmail.com'],
        'calendar_keywords': ['Masha'],
        'clockify_projects': ['Administração & Marcações']
    },
    'Rafael': {
        'whatsapp_ids': ['351966664998'],
        'emails': ['reesteves.mulabs@gmail.com'],
        'calendar_keywords': ['Rafael'],
        'clockify_projects': ['Consultoria']
    },
    'Vanessa': {
        'whatsapp_ids': [],
        'emails': [],
        'calendar_keywords': ['Vanessa', 'Dr. VA'],
        'clockify_projects': ['Clínica & Operações']
    }
}


def get_week_boundaries(week_start=None):
    """Get Monday-Sunday for the specified week"""
    if week_start:
        start = datetime.strptime(week_start, "%Y-%m-%d")
    else:
        today = datetime.now()
        start = today - timedelta(days=today.weekday())
    
    end = start + timedelta(days=6, hours=23, minutes=59)
    return start, end


def estimate_from_whatsapp(person, start_date, end_date):
    """Estimate hours from WhatsApp activity"""
    # For now, this is a placeholder - in production would read from WhatsApp logs
    # Currently returning 0 until we implement WhatsApp log parsing
    
    whatsapp_ids = TEAM[person].get('whatsapp_ids', [])
    if not whatsapp_ids:
        return 0
    
    # Placeholder: In real implementation, read from WhatsApp message logs
    # message_count = count_messages(whatsapp_ids, start_date, end_date)
    # estimated_minutes = message_count * MULTIPLIERS['whatsapp_message']
    
    return 0  # Placeholder until WhatsApp log integration


def estimate_from_calendar(person, start_date, end_date):
    """Estimate hours from calendar events"""
    keywords = TEAM[person].get('calendar_keywords', [])
    if not keywords:
        return 0
    
    # Try to read from calendar data if available
    calendar_file = Path("status/calendar-events.json")
    if not calendar_file.exists():
        return 0
    
    try:
        with open(calendar_file) as f:
            events = json.load(f)
        
        total_minutes = 0
        for event in events:
            event_start = datetime.fromisoformat(event.get('start', '').replace('Z', '+00:00'))
            event_end = datetime.fromisoformat(event.get('end', '').replace('Z', '+00:00'))
            
            # Check if event falls within week
            if start_date <= event_start <= end_date:
                # Check if event mentions this person
                event_text = f"{event.get('summary', '')} {event.get('description', '')}".lower()
                if any(kw.lower() in event_text for kw in keywords):
                    duration = (event_end - event_start).total_seconds() / 60
                    total_minutes += duration
        
        return total_minutes
    except Exception as e:
        print(f"[WARN] Calendar read error: {e}")
        return 0


def estimate_from_emails(person, start_date, end_date):
    """Estimate hours from email activity"""
    # Placeholder until email integration
    # Would count emails sent/received and apply multiplier
    return 0


def get_clockify_hours(person, start_date, end_date):
    """Get real tracked hours from Clockify"""
    clockify_file = Path("status/clockify-realtime.json")
    if not clockify_file.exists():
        return 0
    
    try:
        with open(clockify_file) as f:
            data = json.load(f)
        
        # Check if this is current week data
        week_start = datetime.fromisoformat(data.get('week_start', '2000-01-01'))
        if abs((week_start - start_date).days) <= 1:
            return data.get('by_person', {}).get(person, 0) * 60  # Convert hours to minutes
        
        return 0
    except Exception as e:
        return 0


def calculate_estimated_hours(person, start_date, end_date):
    """Calculate total estimated hours for a person"""
    
    # Get real Clockify time (if any)
    clockify_minutes = get_clockify_hours(person, start_date, end_date)
    
    # Estimate from other activities
    whatsapp_minutes = estimate_from_whatsapp(person, start_date, end_date)
    calendar_minutes = estimate_from_calendar(person, start_date, end_date)
    email_minutes = estimate_from_emails(person, start_date, end_date)
    
    # Total estimated minutes
    total_minutes = clockify_minutes + whatsapp_minutes + calendar_minutes + email_minutes
    
    # Cap at realistic daily limits (10 hours/day = 70 hours/week max)
    max_minutes = 70 * 60
    total_minutes = min(total_minutes, max_minutes)
    
    return {
        'total_hours': round(total_minutes / 60, 1),
        'breakdown': {
            'clockify': round(clockify_minutes / 60, 1),
            'whatsapp': round(whatsapp_minutes / 60, 1),
            'calendar': round(calendar_minutes / 60, 1),
            'email': round(email_minutes / 60, 1)
        },
        'confidence': 'low' if total_minutes == 0 else ('medium' if clockify_minutes == 0 else 'high')
    }


def generate_weekly_report(week_start=None):
    """Generate weekly activity-based hour estimates"""
    start_date, end_date = get_week_boundaries(week_start)
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'week_start': start_date.strftime('%Y-%m-%d'),
        'week_end': end_date.strftime('%Y-%m-%d'),
        'method': 'activity_based_estimation',
        'note': 'Estimates based on digital activity patterns',
        'team': {}
    }
    
    for person in TEAM:
        report['team'][person] = calculate_estimated_hours(person, start_date, end_date)
    
    # Calculate totals
    total_hours = sum(p['total_hours'] for p in report['team'].values())
    report['total_team_hours'] = round(total_hours, 1)
    
    return report


def save_report(report):
    """Save report to status file"""
    output_file = Path("status/activity-hours.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return output_file


def update_dashboard_with_estimates():
    """Update dashboard display with estimated hours"""
    report = generate_weekly_report()
    save_report(report)
    
    # Also update clockify.json to include estimates
    clockify_file = Path("status/clockify.json")
    if clockify_file.exists():
        with open(clockify_file) as f:
            clockify_data = json.load(f)
    else:
        clockify_data = {}
    
    clockify_data.update({
        'status': 'CONNECTED',
        'source': 'Activity-Based Estimation',
        'tracking_type': 'WEEKLY_ESTIMATED',
        'week_start': report['week_start'],
        'week_end': report['week_end'],
        'total_hours': report['total_team_hours'],
        'by_person': {p: data['total_hours'] for p, data in report['team'].items()},
        'methodology': 'Combined WhatsApp + Calendar + Clockify',
        'confidence': 'medium',
        'note': 'AI-estimated from activity patterns',
        'timestamp': datetime.now().isoformat()
    })
    
    with open(clockify_file, 'w') as f:
        json.dump(clockify_data, f, indent=2)
    
    return report


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'weekly':
        week = sys.argv[2] if len(sys.argv) > 2 else None
        report = generate_weekly_report(week)
    else:
        report = update_dashboard_with_estimates()
    
    # Print summary
    print(f"\n[ACTIVITY ESTIMATES] Week of {report['week_start']}")
    print(f"Method: {report['method']}")
    print(f"Total Team Hours: {report['total_team_hours']}")
    print("\nBy Person:")
    for person, data in report['team'].items():
        conf_emoji = {'high': '[+]', 'medium': '[~]', 'low': '[?]'}.get(data['confidence'], '[?]')
        print(f"  {conf_emoji} {person}: {data['total_hours']}h")
        if data['total_hours'] > 0:
            breakdown = ', '.join([f"{k}: {v}h" for k, v in data['breakdown'].items() if v > 0])
            print(f"       ({breakdown})")
    
    print(f"\nSaved to: status/activity-hours.json")
    return 0


if __name__ == "__main__":
    exit(main())
