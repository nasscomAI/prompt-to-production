import os
import csv
import json
import sys
import argparse

try:
    from google import genai
except ImportError:
    print("Error: The 'google-generativeai' package is required. Install it using `pip install google-generativeai`.")
    sys.exit(1)
    
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def load_dataset(filepath: str) -> list:
    """
    Reads CSV dataset, validates columns, and reports null count and missing rows.
    """
    if not os.path.exists(filepath):
        print(f"Error: Dataset not found at {filepath}")
        sys.exit(1)
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_count = 0
    null_rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames is None or not set(fieldnames).issuperset(required_cols):
            print(f"Error: Dataset missing required columns. Required: {required_cols}")
            sys.exit(1)
            
        for row in reader:
            data.append(row)
            if not row.get('actual_spend') or str(row['actual_spend']).strip() == '' or str(row['actual_spend']).strip().lower() == 'null':
                null_count = null_count + 1
                null_rows.append(row)
                
    print(f"Dataset validation complete. Found {null_count} rows with explicitly null actual_spend.")
    for r in null_rows:
        print(f"  - Null found: Period={r['period']}, Ward={r['ward']}, Category={r['category']}, Notes={r['notes']}")
        
    return data

def compute_growth(dataset: list, ward: str, category: str, growth_type: str, agents_text: str, skills_text: str) -> str:
    """
    Constructs the prompt and sends it to Gemini to compute the growth table.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Please set the GEMINI_API_KEY environment variable (or add it to a .env file).")
        sys.exit(1)
        
    genai.configure(api_key=api_key)
    
    system_instruction = f"AGENT INSTRUCTIONS:\n{agents_text}\n\nSKILLS OVERVIEW:\n{skills_text}"
    
    growth_req = growth_type if growth_type else "NOT SPECIFIED"
    
    prompt = f"Please calculate the {growth_req} growth for Ward: '{ward}' and Category: '{category}'.\n"
    prompt += "Strictly follow the enforcement rules: DO NOT aggregate across wards/categories. Flag every null with the reason from 'notes'. Show formula used in every output row.\n\n"
    prompt += "Dataset:\n"
    prompt += json.dumps(dataset, indent=2)
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.0}
        )
        return response.text
    except Exception as e:
        print(f"Error generating computation from Gemini: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV dataset")
    parser.add_argument("--ward", required=True, help="Ward name to filter by")
    parser.add_argument("--category", required=True, help="Category name to filter by")
    parser.add_argument("--growth-type", required=False, help="Growth type to compute (e.g. MoM, YoY). Left optional to test refusal.")
    parser.add_argument("--output", required=True, help="Path to write the output report")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(script_dir, "agents.md")
    skills_path = os.path.join(script_dir, "skills.md")
    
    try:
        with open(agents_path, 'r', encoding='utf-8') as f:
            agents_text = f.read()
        with open(skills_path, 'r', encoding='utf-8') as f:
            skills_text = f.read()
    except Exception as e:
        print(f"Error reading configuration files: {e}")
        sys.exit(1)

    print(f"Loading and validating dataset from {args.input}...")
    dataset = load_dataset(args.input)
    
    print("Computing growth report using Gemini...")
    output_report = compute_growth(dataset, args.ward, args.category, args.growth_type, agents_text, skills_text)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output_report)
        
    print(f"Growth report successfully generated and saved to {args.output}")

if __name__ == "__main__":
    main()
