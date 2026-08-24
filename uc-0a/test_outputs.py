#!/usr/bin/env python3
"""Validate output files against enforcement rules."""
import csv

def validate_output(city):
    with open(f'results_{city}.csv', 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f'{city}: {len(rows)} rows')

        valid_cats = {'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise',
                      'Road Damage', 'Heritage Damage', 'Heat Hazard',
                      'Drain Blockage', 'Other'}
        valid_pris = {'Urgent', 'Standard', 'Low'}
        sev_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance',
                        'fire', 'hazard', 'fell', 'collapse']

        for r in rows:
            assert r['category'] in valid_cats, f'Invalid category: {r["category"]}'
            assert r['priority'] in valid_pris, f'Invalid priority: {r["priority"]}'
            assert r['reason'], f'Missing reason: {r}'
            assert r['flag'] in ('NEEDS_REVIEW', ''), f'Invalid flag: {r["flag"]}'

            if r['priority'] == 'Urgent':
                desc = r['description'].lower()
                assert any(kw in desc for kw in sev_keywords), \
                    f'Urgent without severity keyword: {r}'

        print(f'  All validations passed')

if __name__ == '__main__':
    for city in ['pune', 'kolkata', 'hyderabad', 'ahmedabad']:
        validate_output(city)
    print('\nAll tests passed!')