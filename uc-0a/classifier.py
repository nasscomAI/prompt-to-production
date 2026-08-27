import csv
import json
import argparse

def classify_text(text):
    text_lower = text.lower() if text else ""
    if any(w in text_lower for w in ["water", "pipe", "leak", "drain", "sewer"]):
        return "Water & Sanitation", "High"
    elif any(w in text_lower for w in ["road", "pothole", "street", "traffic"]):
        return "Roads & Infrastructure", "Medium"
    elif any(w in text_lower for w in ["garbage", "waste", "clean", "trash"]):
        return "Solid Waste Management", "Medium"
    elif any(w in text_lower for w in ["light", "power", "electric", "wire"]):
        return "Electricity", "High"
    else:
        return "General Civic", "Low"

def batch_classify(input_file, output_file):
    results = []
    
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get('description') or row.get('complaint') or list(row.values())[0]
            category, priority = classify_text(text)
            
            output_row = dict(row)
            output_row['category'] = category
            output_row['priority_flag'] = priority
            results.append(output_row)
            
    if output_file.endswith('.json'):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
    else:
        if results:
            keys = results[0].keys()
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(results)
                
    print(f"Successfully processed {len(results)} records into {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    batch_classify(args.input, args.output)