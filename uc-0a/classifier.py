import csv

def classify_complaint(description):
    categories = ['Pothole', 'Water Leakage', 'Garbage', 'Streetlight', 'Flooding']
    urgent_keywords = ['injury', 'child', 'hospital', 'school']

    description_lower = description.lower()

    for category in categories:
        if category.lower() in description_lower:
            assigned_category = category
            break
    else:
        assigned_category = 'Other'

    priority = 'Normal'
    for keyword in urgent_keywords:
        if keyword in description_lower:
            priority = 'Urgent'
            break

    reasons = [kw for kw in urgent_keywords if kw in description_lower]
    reason_text = ', '.join(reasons) if reasons else 'No urgent keywords found'

    return assigned_category, priority, reason_text


def main():
    input_file = 'data/city-test-files/test_pune.csv'
    output_file = 'results_pune.csv'

    with open(input_file, newline='', encoding='utf-8') as csv_in, \
         open(output_file, 'w', newline='', encoding='utf-8') as csv_out:

        reader = csv.DictReader(csv_in)
        fieldnames = reader.fieldnames + ['Category', 'Priority', 'Reason']
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            description = row.get('description', '')
            category, priority, reason = classify_complaint(description)
            row['Category'] = category
            row['Priority'] = priority
            row['Reason'] = reason
            writer.writerow(row)

    print(f"Classification completed. Results saved to {output_file}")


if __name__ == "__main__":
    main()