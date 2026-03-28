import csv
import os

input_path = '../data/city-test-files/test_kolkata.csv'
output_path = 'kolkata.csv'

classifications = {
    'KM-202401': ['Heritage Damage', 'Standard', 'Mentions heritage lamp post knocked over.', ''],
    'KM-202402': ['Heritage Damage', 'Standard', 'Describes historic tram road cobblestones broken.', ''],
    'KM-202405': ['Noise', 'Standard', 'Refers to wedding band playing at 11pm.', ''],
    'KM-202409': ['Pothole', 'Standard', 'Mentions airport access road full of potholes.', ''],
    'KM-202410': ['Pothole', 'Standard', 'States pothole causing tyre blowouts.', ''],
    'KM-202411': ['Pothole', 'Standard', 'Mentions deep pothole filling with rainwater.', ''],
    'KM-202415': ['Other', 'Standard', 'States complex draining directly onto public road.', 'NEEDS_REVIEW'],
    'KM-202418': ['Waste', 'Standard', 'Refers to waste overflowing in tourist zone.', ''],
    'KM-202421': ['Road Damage', 'Urgent', 'Mentions pedestrian fell and needed hospital visit.', ''],
    'KM-202422': ['Road Damage', 'Standard', 'States road surface buckled near bridge.', ''],
    'KM-202426': ['Heritage Damage', 'Standard', 'Mentions heritage residential building defaced.', ''],
    'KM-202430': ['Other', 'Standard', 'Mentions gas leak smell indicating a chemical issue.', 'NEEDS_REVIEW'],
    'KM-202434': ['Heritage Damage', 'Standard', 'Refers to heritage stone not being replaced.', ''],
    'KM-202436': ['Other', 'Standard', 'Mentions entire substation tripped causing darkness.', 'NEEDS_REVIEW'],
    'KM-202438': ['Noise', 'Standard', 'States street vendors using amplifiers illegally.', '']
}

with open(input_path, mode='r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
    
    with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            cid = row['complaint_id']
            if cid in classifications:
                c_data = classifications[cid]
                row['category'] = c_data[0]
                row['priority'] = c_data[1]
                row['reason'] = c_data[2]
                row['flag'] = c_data[3]
            writer.writerow(row)

print("Created kolkata.csv successfully.")
