"""
UC-0C — Number That Looks Right
Gemini integration that prevents silent formatting or dataset numerics execution failures via RICE rules.
"""
import argparse
import csv
import json
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: Please install: pip install google-genai")
    sys.exit(1)

def get_system_prompt() -> str:
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        agents_path = os.path.join(script_dir, 'agents.md')
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "Compute growth properly."

def load_dataset(filepath: str, ward: str, category: str):
    """Filter strictly so the LLM prevents cross-aggregation automatically."""
    filtered_rows = []
    null_count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('ward') == ward and row.get('category') == category:
                filtered_rows.append(row)
                if not row.get('actual_spend') or row.get('actual_spend').strip() == '':
                    null_count += 1
    return filtered_rows, null_count

def compute_growth(client, filtered_rows: list, ward: str, category: str, growth_type: str, system_prompt: str) -> str:
    # Programmatic rule enforcement: Refuse if ward or category are not specified
    if not ward or not category:
        return "ERROR: SYSTEM REFUSAL. Ward and Category must be explicitly specified to avoid silent aggregation."
        
    # Programmatic rule enforcement: Refuse if growth type is not specified
    if not growth_type:
        return "ERROR: SYSTEM REFUSAL. Growth Type must be explicitly specified (e.g. MoM or YoY)."

    dataset_json = json.dumps(filtered_rows, indent=2)
    prompt = (
        f"Filtered Data exclusively for {ward} - {category}:\n{dataset_json}\n\n"
        f"User Request: Compute {growth_type} growth for this dataset. "
        f"Output MUST be in markdown table format including Period, Actual Spend, Formula Used, Growth, and Notes columns. "
        f"Flag all null/missing actual spend values directly using the notes provided, do not silently skip them!"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0
            )
        )
        return response.text
    except Exception as e:
        print(f"Error computing growth: {e}")
        return "ERROR: Could not compute growth."

def main():
    parser = argparse.ArgumentParser(description="UC-0C Numeric Analyser")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output file")
    
    # Intentionally leaving these as optional so the script can demonstrate the failure mode catching
    parser.add_argument("--ward", required=False, help="Ward filter")
    parser.add_argument("--category", required=False, help="Category filter")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Type of growth (e.g., MoM)")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(">> WARNING: GEMINI_API_KEY is not set!")
        sys.exit(1)
        
    ward = getattr(args, 'ward', None)
    category = getattr(args, 'category', None)
    growth_type = getattr(args, 'growth_type', None)

    print(f"Reading {args.input} and filtering for Ward: {ward} / Category: {category}...")
    filtered_rows, null_count = load_dataset(args.input, ward, category)
    print(f"Loaded {len(filtered_rows)} strictly matched rows. Early warning: Found {null_count} null actual_spend rows.")
    
    client = genai.Client(api_key=api_key)
    system_prompt = get_system_prompt()
    
    print("Computing metrics via Gemini...")
    result_text = compute_growth(client, filtered_rows, ward, category, growth_type, system_prompt)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(result_text)
        
    print(f"Done! Evaluated metrics structured into {args.output}")

if __name__ == "__main__":
    main()
