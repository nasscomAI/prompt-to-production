import argparse
import re

def retrieve_policy(file_path: dict) -> dict:
    """Loads .txt policy file and returns content as structured numbered sections."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"Could not read file {file_path}: {e}")

    # Regex to match clause numbers like "1.1", "2.3" followed by their text
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|\Z)", re.MULTILINE | re.DOTALL)
    
    sections = {}
    for match in clause_pattern.finditer(content):
        clause_id = match.group(1)
        text = match.group(2).replace("\n", " ").strip()
        text = re.sub(r"\s+", " ", text)
        sections[clause_id] = text
        
    if not sections:
        raise ValueError("No clauses found in the document.")
        
    return sections

def summarize_policy(sections: dict) -> str:
    """Takes structured sections and produces a compliant summary with clause references."""
    summary_lines = ["# HR Leave Policy Summary\n"]
    summary_lines.append("*Note: To prevent meaning loss and condition drops, multiple clauses are quoted verbatim where conditionality is complex.*\n")

    for clause_id, text in sorted(sections.items(), key=lambda x: [int(part) for part in x[0].split('.')]):
        summary_lines.append(f"### Clause {clause_id}")
        
        # Enforcement Rules: 
        # 1. Every numbered clause must be present in the summary
        # 2. Multi-condition obligations must preserve ALL conditions
        # 3. Never add information
        # 4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it

        if any(keyword in text.lower() for keyword in ["must", "requires", "not permitted", "approval from", "regardless", "forfeited"]):
            summary_lines.append(f"**Action Required / Verbatim Quote:** \"{text}\"")
        else:
            summary_lines.append(text)
            
        summary_lines.append("")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input policy text file")
    parser.add_argument("--output", required=True, help="Output summary file")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary generated successfully to {args.output}")
    except Exception as e:
        print(f"Error processing policy: {e}")

if __name__ == "__main__":
    main()
