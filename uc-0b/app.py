"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

# Required clauses that must be present in the summary
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file and returns content as structured numbered sections.
    Handles various document formats robustly.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error reading policy file: {str(e)}")
    
    if not content.strip():
        return {"sections": {}, "full_text": ""}
    
    # Parse sections by finding numbered clauses (e.g., 2.3, 3.2, etc.)
    sections = {}
    lines = content.split('\n')
    current_clause = None
    current_content = []
    
    for line in lines:
        stripped = line.strip()
        # Skip separator lines (any line with only = or similar characters)
        if re.match(r'^[═=_\-]+$', stripped):
            continue
        # Skip section headers like "3. SICK LEAVE" (single digit + dot + text, no second digit)
        # But keep actual clauses like "3.2" (digit.digit pattern)
        if re.match(r'^\d+\.\s+[A-Z]', stripped) and not re.match(r'^\d+\.\d+\s+', stripped):
            continue
        # Match clause numbers like 2.3, 3.2, 5.2 - must have exactly 2 parts (digit.digit)
        match = re.match(r'^(\d+\.\d+)\s+(.+)$', stripped)
        if match:
            # Save previous clause
            if current_clause:
                sections[current_clause] = ' '.join(current_content)
            current_clause = match.group(1)
            current_content = [match.group(2)]
        elif current_clause:
            # Continuation of previous clause - append to content
            if stripped:
                current_content.append(stripped)
    
    # Save last clause
    if current_clause:
        sections[current_clause] = ' '.join(current_content)
    
    return {"sections": sections, "full_text": content}


def summarize_policy(sections: dict, required_clauses: list) -> str:
    """
    Takes structured policy sections and produces a compliant summary with clause references.
    Preserves all obligations, conditions, and binding verbs.
    """
    summary_lines = []
    missing_clauses = []
    
    for clause_num in required_clauses:
        if clause_num in sections:
            content = sections[clause_num].strip()
            # Always preserve full content - no arbitrary truncation
            summary_lines.append(f"[{clause_num}] {content}")
        else:
            missing_clauses.append(clause_num)
            summary_lines.append(f"[{clause_num}] [MISSING - could not extract]")
    
    summary = "HR LEAVE POLICY SUMMARY\n" + "=" * 40 + "\n\n"
    summary += "\n\n".join(summary_lines)
    
    # Fail if any required clauses are missing
    if missing_clauses:
        summary += f"\n\nERROR: The following required clauses could not be extracted: {', '.join(missing_clauses)}"
        raise ValueError(f"Missing required clauses: {', '.join(missing_clauses)}")
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()
    
    # Retrieve policy
    policy_data = retrieve_policy(args.input)
    
    # Summarize policy
    summary = summarize_policy(policy_data["sections"], REQUIRED_CLAUSES)
    
    # Write output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
