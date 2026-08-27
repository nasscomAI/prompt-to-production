"""
UC-0C app.py
Implemented using the RICE + agents.md + skills.md workflow.
"""
import argparse
import os
import sys
import yaml
import csv
import json
from pathlib import Path

def load_agent_prompt(agents_file: str) -> str:
    """Loads and formats the RICE prompt from agents.md."""
    if not os.path.exists(agents_file):
        raise FileNotFoundError(f"Agent specification missing: {agents_file}")
        
    with open(agents_file, 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
        
    prompt = []
    if 'role' in content: 
        prompt.append(f"ROLE:\n{content['role'].strip()}\n")
    if 'intent' in content: 
        prompt.append(f"INTENT:\n{content['intent'].strip()}\n")
    if 'context' in content: 
        prompt.append(f"CONTEXT:\n{content['context'].strip()}\n")
    if 'enforcement' in content:
        prompt.append("ENFORCEMENT RULES:")
        for idx, rule in enumerate(content['enforcement'], 1):
            prompt.append(f"{idx}. {rule}")
            
    return "\n".join(prompt)

def load_dataset(filepath: str):
    """Skill 1: Reads CSV, validates columns, and identifies null actual_spend rows."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset missing: {filepath}")
    
    data = []
    null_rows = []
    mandatory_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Check columns
        if not all(col in reader.fieldnames for col in mandatory_columns):
            missing = [col for col in mandatory_columns if col not in reader.fieldnames]
            raise ValueError(f"Missing mandatory columns: {missing}")
            
        for row in reader:
            if not row['actual_spend'].strip():
                null_rows.append(row)
            data.append(row)
            
    return data, null_rows

def summarize_growth(data: list, null_rows: list, ward: str, category: str, growth_type: str, system_instruction: str) -> str:
    """Skill 2: Produces a compliant growth table using AI with offline fallback."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Filter data for specific ward/category
    filtered_data = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    if not filtered_data:
        return f"Error: No data found for Ward: '{ward}' and Category: '{category}'."

    # Sort by period to ensure growth calculation is correct
    filtered_data.sort(key=lambda x: x['period'])

    # Format the data for the prompt
    data_json = json.dumps(filtered_data, indent=2)
    
    prompt = (
        f"DATASET (Filtered for {ward} / {category}):\n{data_json}\n\n"
        f"REQUEST: Calculate {growth_type} growth. Remember to flag null rows and show formulas.\n"
    )

    # ---------- TRY API FIRST ----------
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"{system_instruction}\n\n{prompt}"
            )

            return response.text

        except Exception as e:
            print(f"API failed ({e}), switching to offline mode...\n", file=sys.stderr)

    # ---------- FALLBACK (OFFLINE) ----------
    print("Using offline growth calculator...", file=sys.stderr)
    
    output = []
    output.append(f"Growth Analysis: {ward} | {category} | {growth_type}")
    output.append("-" * 80)
    output.append(f"{'Period':<10} | {'Actual Spend':<15} | {'Growth':<10} | {'Formula/Note'}")
    output.append("-" * 80)

    prev_val = None
    
    for row in filtered_data:
        period = row['period']
        actual_str = row['actual_spend'].strip()
        
        if not actual_str:
            output.append(f"{period:<10} | {'NULL':<15} | {'N/A':<10} | FLAG: {row['notes']}")
            prev_val = None
            continue
            
        try:
            current_val = float(actual_str)
        except ValueError:
            output.append(f"{period:<10} | {actual_str:<15} | {'ERROR':<10} | Invalid numeric value")
            prev_val = None
            continue

        if prev_val is not None and prev_val != 0:
            growth = ((current_val - prev_val) / prev_val) * 100
            formula = f"({current_val} - {prev_val}) / {prev_val}"
            output.append(f"{period:<10} | {current_val:<15.2f} | {growth:>+7.1f}% | {formula}")
        else:
            output.append(f"{period:<10} | {current_val:<15.2f} | {'-':<10} | First data point or prev null")
            
        prev_val = current_val

    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Analysis")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to save output")
    args = parser.parse_args()

    # Refusal condition: missing growth type
    if not args.growth_type:
        print("Refusal: --growth-type (MoM or YoY) must be specified. I cannot guess the growth calculation method.", file=sys.stderr)
        sys.exit(1)

    # Locate agents.md in the current script directory
    script_dir = Path(__file__).parent
    agents_file = script_dir / "agents.md"
    
    try:
        print(f"Loading RICE agent specs from {agents_file.name}...")
        system_instruction = load_agent_prompt(str(agents_file))
        
        print(f"Skill 1: Loading dataset from {args.input}...")
        data, null_rows = load_dataset(args.input)
        print(f"Identified {len(null_rows)} null rows in dataset.")
        
        print(f"Skill 2: Computing {args.growth_type} growth for '{args.ward}'...")
        result = summarize_growth(data, null_rows, args.ward, args.category, args.growth_type, system_instruction)
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
            
        print(f"Success! Analysis written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
