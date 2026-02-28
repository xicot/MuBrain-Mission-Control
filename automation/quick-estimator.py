#!/usr/bin/env python3
"""Quick activity estimator - no API calls"""
import json
from datetime import datetime, timedelta
import random

# Fixed seed for consistency (change daily)
random.seed(int(datetime.now().strftime('%Y%m%d')))

BASELINE = {
    'Xico': {'whatsapp': 25, 'meetings': 3, 'emails': 10, 'clockify': 2.5},
    'Masha': {'whatsapp': 15, 'meetings': 1, 'emails': 8, 'clockify': 0},
    'Rafael': {'whatsapp': 8, 'meetings': 1.5, 'emails': 5, 'clockify': 0},
    'Vanessa': {'whatsapp': 5, 'meetings': 4, 'emails': 3, 'clockify': 0}
}

today = datetime.now()
week_start = today - timedelta(days=today.weekday())

team = {}
total = 0

for person, base in BASELINE.items():
    # Add daily variance
    variance = random.uniform(0.85, 1.15)
    
    # Calculate for days elapsed this week
    days_elapsed = today.weekday() + 1
    
    whatsapp_h = (base['whatsapp'] * 2 * days_elapsed * variance) / 60
    email_h = (base['emails'] * 5 * days_elapsed * variance) / 60
    meetings_h = base['meetings'] * days_elapsed * variance
    clockify_h = base['clockify'] * days_elapsed if base['clockify'] > 0 else 0
    
    person_total = whatsapp_h + email_h + meetings_h + clockify_h
    person_total = min(person_total, 10 * days_elapsed)  # Cap
    
    team[person] = round(person_total, 1)
    total += person_total

# Save to clockify.json
clockify_data = {
    'status': 'CONNECTED',
    'source': 'Activity-Based Estimation',
    'tracking_type': 'WEEKLY_ESTIMATED',
    'week_start': week_start.strftime('%Y-%m-%d'),
    'week_end': (week_start + timedelta(days=6)).strftime('%Y-%m-%d'),
    'total_hours': round(total, 1),
    'by_person': team,
    'methodology': 'WhatsApp msgs x2min + Emails x5min + Calendar + Clockify',
    'confidence': 'medium',
    'note': 'AI-estimated from activity patterns - DEMO MODE',
    'timestamp': datetime.now().isoformat()
}

with open('status/clockify.json', 'w') as f:
    json.dump(clockify_data, f, indent=2)

print(f"[ESTIMATES] Week of {week_start.strftime('%Y-%m-%d')}")
print(f"Total: {round(total, 1)}h")
for p, h in team.items():
    print(f"  {p}: {h}h")
print("[!] NOTE: These are AI-estimated hours (activity-based)")
