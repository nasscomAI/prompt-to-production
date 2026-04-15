"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
from typing import Dict, List

VALID_CATEGORIES = {
    'Pothole',
    'Flooding',
    'Streetlight',
    'Waste',
    'Noise',
    'Road Damage',
    'Heritage Damage',
    'Heat Hazard',
    'Drain Blockage',
    'Other',
}

CATEGORY_KEYWORDS = {
    'pothole': 'Pothole',
    'potholes': 'Pothole',
    'pothole(s)': 'Pothole',
    'flood': 'Flooding',
    'flooding': 'Flooding',
    'streetlight': 'Streetlight',
    'street lights': 'Streetlight',
    'light': 'Streetlight',
    'waste': 'Waste',
    'garbage': 'Waste',
    'trash': 'Waste',
    'noise': 'Noise',
    'music': 'Noise',
    'road damage': 'Road Damage',
    'road': 'Road Damage',
    'heritage': 'Heritage Damage',
    'heat': 'Heat Hazard',
    'temperature': 'Heat Hazard',
    'temprature': 'Heat Hazard',
    'drain': 'Drain Blockage',
    'drainage': 'Drain Blockage',
    'sewer': 'Drain Blockage',
    'blocked drain': 'Drain Blockage',
}

PRIORITY_KEYWORDS = {
    'Urgent': [
        'injury',
        'child',
        'school',
        'hospital',
        'ambulance',
        'fire',
        'heat hazard',
        'fell',
        'collapse',
    ],
    'Standard': ['road', 'pothole', 'dark', 'flood'],
    'Low': ['paving', 'heritage', 'waste', 'crater', 'music'],
}

REQUIRED_FIELDS = [
    'complaint_id',
    'date_raised',
    'city',
    'ward',
    'location',
    'description',
    'reported_by',
    'days_open',
]


def classify_complaint(row: Dict[str, str]) -> dict:
    """Classify a single complaint row and return required output fields."""
    description = (row.get('description') or '').strip()
    desc_lower = description.lower()

    if not description:
        return {
            'complaint_id': row.get('complaint_id', ''),
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'No description provided.',
            'flag': 'NEEDS_REVIEW',
        }

    matched_categories: List[str] = []
    matched_words: List[str] = []
    for keyword in sorted(CATEGORY_KEYWORDS, key=len, reverse=True):
        if keyword in desc_lower:
            category = CATEGORY_KEYWORDS[keyword]
            if category not in matched_categories:
                matched_categories.append(category)
            matched_words.append(keyword)

    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ''
    else:
        category = 'Other'
        flag = 'NEEDS_REVIEW'

    priority = 'Standard'
    if any(keyword in desc_lower for keyword in PRIORITY_KEYWORDS['Urgent']):
        priority = 'Urgent'
    elif any(keyword in desc_lower for keyword in PRIORITY_KEYWORDS['Standard']):
        priority = 'Standard'
    elif any(keyword in desc_lower for keyword in PRIORITY_KEYWORDS['Low']):
        priority = 'Low'

    if matched_words:
        cited_keywords = ', '.join(f"'{word}'" for word in matched_words[:3])
        reason = f"Mentions {cited_keywords} in the description."
    else:
        excerpt = description[:80].replace('\n', ' ').strip()
        reason = f"No clear keywords found; excerpt: '{excerpt}'."

    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, and write the output CSV."""
    with open(input_path, newline='', encoding='utf-8') as inf:
        reader = csv.DictReader(inf)
        if reader.fieldnames is None:
            raise ValueError('Input CSV file is missing a header row')

        missing_fields = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
        if missing_fields:
            raise ValueError(f"Input CSV is missing required columns: {', '.join(missing_fields)}")

        with open(output_path, 'w', newline='', encoding='utf-8') as outf:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outf, fieldnames=fieldnames)
            writer.writeheader()

            for row_index, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                except Exception as error:
                    sys.stderr.write(f"Row {row_index} classification error: {error}\n")
                    result = {
                        'complaint_id': row.get('complaint_id', ''),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': 'Classification failed for this row.',
                        'flag': 'NEEDS_REVIEW',
                    }
                writer.writerow({key: result.get(key, '') for key in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser(description='UC-0A Complaint Classifier')
    parser.add_argument('--input', required=True, help='Path to test_[city].csv')
    parser.add_argument('--output', required=True, help='Path to write results CSV')
    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
    except Exception as error:
        sys.stderr.write(f"Error: {error}\n")
        sys.exit(1)

    print(f"Done. Results written to {args.output}")


if __name__ == '__main__':
    main()
