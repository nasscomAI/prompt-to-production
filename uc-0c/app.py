import csv
import os
import sys

def process_budget(input_file, output_file):
    print(f"Reading budget data from: {input_file}...")
    aggregated = {}
    
    try:
        with open(input_file, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # Dynamically identify columns to handle any case sensitivity in the CSV
            fieldnames = {name.lower(): name for name in reader.fieldnames}
            
            ward_col = fieldnames.get('ward', 'Ward')
            category_col = fieldnames.get('category', 'Category')
            budget_col = fieldnames.get('budget', fieldnames.get('amount', 'Budget'))

            for row in reader:
                ward = row.get(ward_col, 'Unknown').strip()
                category = row.get(category_col, 'Unknown').strip()
                
                # Extract numeric value safely
                try:
                    raw_val = row.get(budget_col, '0').replace(',', '').replace('$', '').strip()
                    budget = float(raw_val) if raw_val else 0.0
                except ValueError:
                    continue
                    
                # Group by (Ward, Category) to prevent silent aggregation loss
                key = (ward, category)
                aggregated[key] = aggregated.get(key, 0.0) + budget
                
        # Write output file
        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Ward', 'Category', 'Total_Budget'])
            for (ward, category), total in aggregated.items():
                writer.writerow([ward, category, total])
                
        print(f"Successfully aggregated budget without data loss to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find the input file at {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Define paths relative to the uc-0c directory
    in_path = os.path.join('..', 'data', 'budget', 'ward_budget.csv')
    out_path = 'growth_output.csv'
    
    process_budget(in_path, out_path)