import argparse
import csv
import sys
import os

def parse_simple_yaml(filepath: str) -> dict:
    """Basic YAML parser for key-value structures from our agents.md files."""
    config = {"enforcement": []}
    with open(filepath, "r", encoding="utf-8") as f:
        for auto_line in f:
            line = auto_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("- "):
                rule = line[2:].strip("\"' ")
                config["enforcement"].append(rule)
            elif ":" in auto_line:
                key, val = auto_line.split(":", 1)
                key = key.strip()
                val = val.strip().strip("\"' ")
                if key and key != "enforcement":
                    config[key] = val
    return config

def load_dataset(filepath: str) -> list:
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    dataset = []
    null_count = 0
    null_records = []
    
    expected_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            # Validate Columns
            if not expected_cols.issubset(set(reader.fieldnames or [])):
                print(f"Error: Dataset is missing expected columns. Found: {reader.fieldnames}")
                sys.exit(1)
                
            for i, row in enumerate(reader):
                # Clean strings
                cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                
                # Check for nulls (empty or 'null' string)
                actual = cleaned_row.get("actual_spend", "")
                if not actual or actual.lower() == "null":
                    null_count += 1
                    null_records.append(f"Row {i+1} | {cleaned_row.get('period')} | {cleaned_row.get('ward')}: {cleaned_row.get('notes')}")
                    cleaned_row["actual_spend"] = None
                else:
                    try:
                        cleaned_row["actual_spend"] = float(actual)
                    except ValueError:
                        cleaned_row["actual_spend"] = None
                        null_count += 1
                        
                dataset.append(cleaned_row)
                
    except FileNotFoundError:
        print(f"Error: Dataset file '{filepath}' not found.")
        sys.exit(1)
        
    print(f"[Skill: load_dataset] Loaded {len(dataset)} rows successfully.")
    print(f"[Skill: load_dataset] Handled {null_count} null actual_spend rows:")
    for nr in null_records:
        print(f"   => {nr}")
        
    return dataset


def compute_growth(dataset: list, ward: str, category: str, growth_type: str, agent_config: dict) -> list:
    """
    Skill: compute_growth
    Enforces rules and returns per-period table with formulas.
    """
    # ENFORCEMENT: 4. If --growth-type not specified - refuse and ask
    if not growth_type:
        print("AGENT REFUSAL: 'growth_type' was not specified. I cannot silently guess the formula. Please specify --growth-type (e.g., MoM).")
        sys.exit(1)
        
    # ENFORCEMENT: 1. Never aggregate across wards or categories unless explicitly instructed
    if not ward or not category or ward.lower() == "all" or category.lower() == "all":
        print("AGENT REFUSAL: Cannot aggregate across wards or categories. I am restricted to strictly per-ward and per-category calculations. Please specify explicit --ward and --category.")
        sys.exit(1)

    # Filter Dataset to exact ward and category
    subset = sorted(
        [r for r in dataset if r.get("ward") == ward and r.get("category") == category],
        key=lambda x: x.get("period")
    )
    
    if not subset:
        print(f"Warning: No data found for Ward: '{ward}' and Category: '{category}'")
    
    output_rows = []
    
    for i, current_row in enumerate(subset):
        period = current_row["period"]
        actual = current_row["actual_spend"]
        notes = current_row["notes"]
        
        # Base row structure
        out_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend": actual if actual is not None else "NULL",
            "Growth": "n/a",
            "Formula": "n/a",
            "Notes": notes
        }
        
        # ENFORCEMENT: 2. Flag every null row before computing (we also did this in load_dataset)
        if actual is None:
            out_row["Growth"] = "FLAGGED NULL"
            out_row["Formula"] = "Skipped (Null Value handling)"
            output_rows.append(out_row)
            continue
            
        if growth_type.lower() == "mom":
            if i == 0:
                out_row["Formula"] = "First period (no prior data)"
            else:
                prev_actual = subset[i-1]["actual_spend"]
                
                if prev_actual is None:
                    out_row["Growth"] = "Cannot compute"
                    out_row["Formula"] = "Previous period was NULL"
                elif prev_actual == 0:
                    out_row["Growth"] = "∞"
                    out_row["Formula"] = "Division by zero (previous spend was 0)"
                else:
                    growth = ((actual / prev_actual) - 1.0) * 100
                    
                    # Add +/- sign and 1 decimal point
                    sign = "+" if growth > 0 else ""
                    out_row["Growth"] = f"{sign}{growth:.1f}%"
                    
                    # ENFORCEMENT: 3. Show formula used in every output row
                    out_row["Formula"] = f"(({actual} / {prev_actual}) - 1) * 100"
                    
        else:
            # Only MoM is currently implemented natively, anything else we fallback or reject
            print(f"AGENT REFUSAL: The requested growth type '{growth_type}' is not supported in the explicit rules engine yet.")
            sys.exit(1)
            
        output_rows.append(out_row)
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right (MoM Calculator)")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Explicit ward name")
    parser.add_argument("--category", required=False, help="Explicit category name")
    parser.add_argument("--growth-type", required=False, help="Growth type e.g. MoM")
    parser.add_argument("--output", required=True, help="Path to save output CSV")
    
    args = parser.parse_args()

    # Load agent configuration
    agent_path = os.path.join(os.path.dirname(__file__), "agents.md")
    try:
        agent_config = parse_simple_yaml(agent_path)
    except FileNotFoundError:
        print(f"Warning: {agent_path} not found. Running with baseline rules only.")
        agent_config = {}

    # Execute Skills
    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type, agent_config)

    # Save to CSV
    try:
        with open(args.output, "w", encoding="utf-8", newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            else:
                f.write("No data generated.\n")
        print(f"\n[Skill: compute_growth] Done. Results written safely to {args.output}")
    except IOError as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()
