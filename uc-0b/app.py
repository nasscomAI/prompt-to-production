import argparse
import os

def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def summarize_policy(lines):
    mandatory_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    extracted = {c: "" for c in mandatory_clauses}
    
    current_clause = None
    
    # Skip the header (first few lines)
    for i, line in enumerate(lines):
        if i < 10: continue # Skip initial CMC header and version info
        
        # Check if line starts with a clause number
        stripped = line.strip()
        if not stripped: continue
        
        # Match "x.x " at the start of a stripped line
        parts = stripped.split(' ', 1)
        if len(parts) > 0 and parts[0] in mandatory_clauses:
            current_clause = parts[0]
            extracted[current_clause] = parts[1] if len(parts) > 1 else ""
        elif current_clause and not (parts[0][0].isdigit() and '.' in parts[0]):
            # Append to current clause if it's not a new clause number
            extracted[current_clause] += " " + stripped
        else:
            # It's a different clause or header, stop collecting for current
            current_clause = None

    summary_lines = ["City Municipal Corporation - Policy Summary (Mandatory Clauses Only)\n"]
    for c in mandatory_clauses:
        val = extracted[c].strip()
        # Clean up multi-space
        val = " ".join(val.split())
        summary_lines.append(f"Clause {c}: {val}")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    lines = retrieve_policy(args.input)
    if not lines:
        print(f"Error: Input file {args.input} not found.")
        return
        
    summary = summarize_policy(lines)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary generated successfully in {args.output}")

if __name__ == "__main__":
    main()
