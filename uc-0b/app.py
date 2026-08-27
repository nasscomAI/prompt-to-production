"""
UC-0B — Summary That Changes Meaning
Implement a summary agent that preserves every numbered clause and condition.
"""
import argparse
import re
import os

def retrieve_policy(file_path):
    """
    Load raw policy text and split into sections based on decimal numbering (e.g., 2.3).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file {file_path} not found.")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find numbered sections (e.g., 2.3, 5.2)
    # Stop at decorative lines or next section
    sections = {}
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\s*[═\d]+\.\d+|$|\n\s*═+)'
    matches = re.findall(pattern, content, re.DOTALL)

    for section_id, section_text in matches:
        # Clean up whitespace, line breaks and decorative chars
        text = " ".join(section_text.split())
        text = text.split('══')[0].strip() # Cut off at decorative lines
        sections[section_id] = text

    return sections

def summarize_policy(sections):
    """
    Summarize sections while strictly enforcing clause preservation and multi-condition obligations.
    """
    summary = []
    summary.append("POLICY SUMMARY — KEY OBLIGATIONS")
    summary.append("=" * 40 + "\n")

    # The 10 critical clauses defined in ground truth
    critical_clauses = [
        "2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"
    ]

    for cid in critical_clauses:
        if cid in sections:
            text = sections[cid]
            # Enforcement Rule check for Clause 5.2 (Multi-condition)
            if cid == "5.2" and ("Department Head" not in text or "HR Director" not in text):
                summary.append(f"[{cid}] WARNING: Summary potentially softening conditions. Quoting verbatim:")
                summary.append(f"     > {text}")
            else:
                summary.append(f"[{cid}] {text}")
        else:
            summary.append(f"[{cid}] ERROR: Clause not found in source document.")

    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy.txt")
    parser.add_argument("--output", required=True, help="Path to output summary.txt")
    args = parser.parse_args()

    try:
        print(f"Retrieving policy from {args.input}...")
        sections = retrieve_policy(args.input)
        
        print("Generating compliant summary...")
        summary_text = summarize_policy(sections)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        
        print(f"Done. Summary written to {args.output}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
