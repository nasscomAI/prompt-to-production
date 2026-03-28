"""
UC-0C app.py — Starter file.
Implementation based on the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

def build_system_prompt() -> str:
    """Loads agents.md and skills.md to form the RICE prompt."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(base_dir, "agents.md")
    skills_path = os.path.join(base_dir, "skills.md")
    
    with open(agents_path, "r", encoding="utf-8") as f:
        agents_text = f.read()
    with open(skills_path, "r", encoding="utf-8") as f:
        skills_text = f.read()
        
    return (
        "You are an AI Budget Analyst bound by the following RICE architecture:\n\n"
        f"=== AGENTS.MD (RICE INSTRUCTIONS) ===\n{agents_text}\n\n"
        f"=== SKILLS.MD (I/O SPEC) ===\n{skills_text}\n\n"
        "Please compute the requested growth metrics according strictly to these rules."
    )

def mock_load_dataset(file_path: str):
    data = []
    nulls = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
                if not row.get("actual_spend") or row["actual_spend"].strip() == "":
                    nulls.append(row)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)
        
    print(f"Loaded {len(data)} rows.")
    if nulls:
        print(f"WARNING: {len(nulls)} deliberately null 'actual_spend' values detected in the following rows:")
        for n in nulls:
            print(f" - {n.get('period')} · {n.get('ward')} · {n.get('category')} reason: {n.get('notes')}")
    return data

def mock_compute_growth(data, ward, category, growth_type):
    if not growth_type:
        return "Refused: Please explicitly specify the growth type (e.g., MoM, YoY)."
    if not ward or not category:
        return "Refused: Cannot compute aggregated metrics across wards or categories."
        
    filtered = [d for d in data if d.get("ward") == ward and d.get("category") == category]
    filtered.sort(key=lambda x: x.get("period", ""))
    
    output_lines = [
        f"Growth Report: {ward} | {category} | Metric: {growth_type}",
        "-" * 80,
        "Period    | Actual Spend (Lakh) | Growth % | Formula used",
        "-" * 80
    ]
    
    prev_val = None
    for row in filtered:
        period = row.get("period")
        spend_str = row.get("actual_spend", "").strip()
        notes = row.get("notes", "")
        
        if not spend_str:
            output_lines.append(f"{period}   | NULL                | Flagged  | Cannot compute. Reason: {notes}")
            prev_val = None
            continue
            
        try:
            curr_val = float(spend_str)
        except ValueError:
            output_lines.append(f"{period}   | INVALID             | Flagged  | Cannot parse float")
            prev_val = None
            continue
            
        if prev_val is None:
            output_lines.append(f"{period}   | {curr_val:<19} | N/A      | No previous period data for {growth_type}")
        else:
            growth_pct = ((curr_val - prev_val) / prev_val) * 100
            sign = "+" if growth_pct > 0 else ""
            formula_used = f"({curr_val} - {prev_val}) / {prev_val} * 100"
            output_lines.append(f"{period}   | {curr_val:<19} | {sign}{growth_pct:.1f}%   | Formula used: {formula_used}")
            
        prev_val = curr_val
        
    return "\n".join(output_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Target Ward")
    parser.add_argument("--category", required=False, help="Target Category")
    parser.add_argument("--growth-type", required=False, help="Growth Type (MoM, YoY, etc)")
    parser.add_argument("--output", required=True, help="Path to write output")
    args = parser.parse_args()
    
    client = None
    if HAS_OPENAI and os.environ.get("OPENAI_API_KEY"):
        try:
            client = openai.OpenAI()
            print("Using Live OpenAI API...")
        except BaseException:
            pass
    
    if not client:
        print("Note: OPENAI_API_KEY not set. Using local mock engine to produce expected output.")
        
    print(f"Retrieving data from {args.input}...")
    data = mock_load_dataset(args.input)
    
    print("Computing metrics...")
    if not client:
        summary = mock_compute_growth(data, args.ward, args.category, args.growth_type)
    else:
        # Construct dynamic prompt for the real LLM usage
        system_prompt = build_system_prompt()
        prompt = f"Run compute_growth for ward='{args.ward}', category='{args.category}', growth_type='{args.growth_type}'. Dataset info:\n"
        for d in data:
            if d.get("ward") == args.ward and d.get("category") == args.category:
                prompt += str(d) + "\n"
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0.0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            summary = response.choices[0].message.content
        except Exception as e:
            summary = f"System API Error: {e}"
    
    print(f"Writing output to {args.output}...")
    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print("Done!")

if __name__ == "__main__":
    main()
