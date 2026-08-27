import csv

input_file = "data/budget/ward_budget.csv"
output_file = "growth_output.csv"

with open(input_file, newline='', encoding='utf-8') as csv_in, \
     open(output_file, 'w', newline='', encoding='utf-8') as csv_out:

    reader = csv.DictReader(csv_in)
    fieldnames = reader.fieldnames + ['Verified', 'Flag']
    writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        try:
            values = [float(row[col]) for col in reader.fieldnames if col != 'Ward']
            total = sum(values)
            verified = 'Yes' if total >= 0 else 'No'
            flag = '' if verified == 'Yes' else 'NEEDS_REVIEW'
        except:
            verified = 'No'
            flag = 'NEEDS_REVIEW'

        row['Verified'] = verified
        row['Flag'] = flag
        writer.writerow(row)

print(f"Number verification completed. Results saved to {output_file}")