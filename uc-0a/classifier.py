import csv
import argparse

def classify_complaint(text):
    text_lower = text.lower()
    
    # Determine category
    if any(word in text_lower for word in ['road', 'pothole', 'street', 'footpath', 'crater', 'underpass', 'collapsed']):
        category = 'Roads'
        reason = 'keyword: ' + next(word for word in ['road', 'pothole', 'street', 'footpath', 'crater', 'underpass', 'collapsed'] if word in text_lower)
    elif any(word in text_lower for word in ['water', 'pipe', 'drain', 'sewage', 'flood', 'flooded', 'flooding', 'stormwater']):
        category = 'Water'
        reason = 'keyword: ' + next(word for word in ['water', 'pipe', 'drain', 'sewage', 'flood', 'flooded', 'flooding', 'stormwater'] if word in text_lower)
    elif any(word in text_lower for word in ['garbage', 'waste', 'sanitation', 'trash']):
        category = 'Sanitation'
        reason = 'keyword: ' + next(word for word in ['garbage', 'waste', 'sanitation', 'trash'] if word in text_lower)
    elif any(word in text_lower for word in ['electricity', 'power', 'light', 'electric']):
        category = 'Electricity'
        reason = 'keyword: ' + next(word for word in ['electricity', 'power', 'light', 'electric'] if word in text_lower)
    elif any(word in text_lower for word in ['safety', 'crime', 'accident', 'fire', 'drilling', 'noise']):
        category = 'Safety'
        reason = 'keyword: ' + next(word for word in ['safety', 'crime', 'accident', 'fire', 'drilling', 'noise'] if word in text_lower)
    else:
        category = 'Other'
        reason = 'no matching keyword'

    # Determine severity
    high_words = ['ambulance', 'hospitalised', 'hospitalized', 'lives at risk', 'dengue', 'school', 'school bus', 'lives', 'risk', 'collapsed', 'crater', 'diverted']
    medium_words = ['many', 'days', 'weeks', 'multiple', 'several', 'regularly', 'daily', 'suffering', 'unusable', 'struggling']

    if any(word in text_lower for word in high_words):
        severity = 'HIGH'
        reason += ' | severity: ' + next(word for word in high_words if word in text_lower)
    elif any(word in text_lower for word in medium_words):
        severity = 'MEDIUM'
        reason += ' | severity: ' + next(word for word in medium_words if word in text_lower)
    else:
        severity = 'LOW'
        reason += ' | severity: no urgent keywords'

    return category, severity, reason

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    high_count = 0
    medium_count = 0
    low_count = 0
    total = 0

    with open(args.input, 'r') as infile, open(args.output, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['category', 'severity', 'reason']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            text = row.get('description', '') or row.get('complaint', '') or row.get('text', '') or list(row.values())[0]
            category, severity, reason = classify_complaint(text)
            row['category'] = category
            row['severity'] = severity
            row['reason'] = reason
            writer.writerow(row)
            total += 1
            if severity == 'HIGH':
                high_count += 1
            elif severity == 'MEDIUM':
                medium_count += 1
            else:
                low_count += 1

    print(f"\n✅ Total complaints: {total}")
    print(f"🔴 HIGH severity:   {high_count}")
    print(f"🟡 MEDIUM severity: {medium_count}")
    print(f"🟢 LOW severity:    {low_count}")
    print(f"\nResults saved to {args.output}\n")

if __name__ == '__main__':
    main()
