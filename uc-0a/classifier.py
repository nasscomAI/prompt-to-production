"""
UC-0A — Complaint Classifier
Complaint classifier for Hyderabad civic issues
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on description.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    # Get complaint_id and description
    complaint_id = row.get('complaint_id', 'UNKNOWN')
    description = row.get('description', '').strip()
    
    # Handle empty or missing description
    if not description:
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'Empty or missing description',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Define severity keywords that trigger Urgent priority
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 
                       'fire', 'hazard', 'fell', 'collapse']
    
    # Define category keywords mapping
    category_keywords = {
        'Pothole': ['pothole', 'potholes', 'crater'],
        'Flooding': ['flood', 'flooded', 'flooding', 'water logging', 'waterlogged'],
        'Streetlight': ['streetlight', 'light', 'lamp', 'street light'],
        'Waste': ['garbage', 'waste', 'trash', 'litter', 'rubbish', 'dump'],
        'Noise': ['noise', 'drilling', 'loud', 'sound', 'honking'],
        'Road Damage': ['road damage', 'road condition', 'damaged road', 'bad road'],
        'Heritage Damage': ['heritage', 'monument', 'historical'],
        'Heat Hazard': ['heat', 'temperature'],
        'Drain Blockage': ['drain', 'blocked', 'blockage', 'stormwater'],
        'Other': []
    }
    
    # Determine category based on keywords in description
    desc_lower = description.lower()
    category = 'Other'  # Default
    
    for cat, keywords in category_keywords.items():
        if cat == 'Other':
            continue
        if any(keyword in desc_lower for keyword in keywords):
            category = cat
            break
    
    # Determine priority based on urgent keywords
    if any(keyword in desc_lower for keyword in urgent_keywords):
        priority = 'Urgent'
    else:
        priority = 'Standard'  # Default, could be refined further
    
    # Generate reason sentence (cites specific words)
    # Find which urgent keyword triggered if any
    urgent_found = [kw for kw in urgent_keywords if kw in desc_lower]
    if urgent_found:
        reason = f"Complaint mentions '{urgent_found[0]}' requiring urgent attention."
    else:
        # Find which category keyword triggered
        for cat, keywords in category_keywords.items():
            if cat == 'Other':
                continue
            found = [kw for kw in keywords if kw in desc_lower]
            if found:
                reason = f"Complaint describes '{found[0]}' indicating {cat.lower()} issue."
                break
        else:
            reason = "Complaint description provided."
    
    # Determine if needs review
    flag = ''
    if category == 'Other' and not any(keyword in desc_lower for keyword in urgent_keywords):
        flag = 'NEEDS_REVIEW'
    
    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    success_count = 0
    error_count = 0
    
    try:
        # Read input CSV
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Process each row
            for row_num, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                    success_count += 1
                except Exception as e:
                    print(f"Error processing row {row_num}: {e}")
                    error_count += 1
                    # Add a placeholder for failed row
                    results.append({
                        'complaint_id': row.get('complaint_id', f'ROW_{row_num}'),
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f'Processing error: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
        
        # Write output CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Processed {success_count} rows successfully, {error_count} errors")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")