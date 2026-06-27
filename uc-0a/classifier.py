import argparse
import csv
import re
import sys

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']


def _word_match(text: str, keyword: str) -> bool:
    if ' ' in keyword:
        return keyword in text
    return bool(re.search(r'(?<![a-z])' + re.escape(keyword) + r'[a-z]*', text))


CATEGORY_RULES = [
    ('Heritage Damage', ['heritage']),
    ('Heat Hazard', ['heat hazard', 'extreme heat', 'heatwave', 'melting', 'bubbling', 'burns', '°C', 'temperature']),
    ('Streetlight', ['streetlight', 'street light', 'light out', 'lights out', 'flickering', 'sparking', 'unlit', 'wiring', 'substation', 'darkness', 'power outage']),
    ('Noise', ['noise', 'noisy', 'loud music', 'loudspeaker', 'playing music', 'drilling', 'playing', 'music', 'amplifier']),
    ('Pothole', ['pothole']),
    ('Drain Blockage', ['drain blocked', 'drain block', 'drainage', 'sewer', 'drain clog', 'drain 100% blocked', 'stormwater drain']),
    ('Flooding', ['flood', 'flooded', 'floods', 'waterlog', 'submerged', 'knee-deep', 'rainwater']),
    ('Waste', ['garbage', 'waste', 'trash', 'litter', 'bin', 'dumping', 'dead animal']),
    ('Road Damage', ['road damage', 'cracked', 'sinking', 'sank', 'road surface', 'manhole cover', 'footpath', 'broken', 'subsided', 'collapsed', 'crater']),
]


def _extract_phrase(desc: str, kw: str) -> str:
    desc_lower = desc.lower()
    if ' ' in kw:
        idx = desc_lower.find(kw)
    else:
        match = re.search(r'(?<![a-z])' + re.escape(kw) + r'[a-z]*', desc_lower)
        idx = match.start() if match else -1
    if idx == -1:
        return kw
    words = desc.split()
    char_count = 0
    word_idx = -1
    for i, w in enumerate(words):
        if char_count <= idx < char_count + len(w) + 1:
            word_idx = i
            break
        char_count += len(w) + 1
    if word_idx < 0:
        return kw
    start = max(0, word_idx - 1)
    end = min(len(words), word_idx + 4)
    return ' '.join(words[start:end])


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get('complaint_id', '').strip()
    description = (row.get('description') or '').strip()

    if not complaint_id or not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Standard',
            'reason': '',
            'flag': 'NEEDS_REVIEW',
        }

    desc_lower = description.lower()

    priority = 'Standard'
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = 'Urgent'
            break

    category = 'Other'
    for cat_name, keywords in CATEGORY_RULES:
        for kw in keywords:
            if _word_match(desc_lower, kw):
                category = cat_name
                break
        if category != 'Other':
            break

    flag = ''
    if category == 'Other':
        flag = 'NEEDS_REVIEW'

    reason = _generate_reason(description, desc_lower, category)

    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag,
    }


def _generate_reason(desc: str, desc_lower: str, category: str) -> str:
    for cat_name, keywords in CATEGORY_RULES:
        if cat_name != category:
            continue
        for kw in keywords:
            if _word_match(desc_lower, kw):
                phrase = _extract_phrase(desc, kw)
                return f'Complaint describes "...{phrase}..." — classified as {category}.'
    if category == 'Other':
        return 'No matching category keywords found in description — flagged for review.'
    return f'Complaint classified as {category} based on description.'


def batch_classify(input_path: str, output_path: str):
    rows = []
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                if not row.get('complaint_id', '').strip() and not row.get('description', '').strip():
                    print(f"Warning: Row {i} is empty — skipping", file=sys.stderr)
                    continue
                try:
                    rows.append(classify_complaint(row))
                except Exception as e:
                    print(f"Warning: Row {i} (ID: {row.get('complaint_id', 'N/A')}) failed — {e}", file=sys.stderr)
                    rows.append({
                        'complaint_id': row.get('complaint_id', ''),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': '',
                        'flag': 'NEEDS_REVIEW',
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found — {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read input file — {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("Error: No valid rows to process", file=sys.stderr)
        sys.exit(1)

    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. {len(rows)} complaints classified. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
