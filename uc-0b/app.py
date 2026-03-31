"""
UC-0B app.py — Policy Compliance Auditor
Implemented as a robust auditor as per RICE method (agents.md).
Handles high-fidelity summarization of city governance policies.
"""
import argparse
import re
import os

# Expanded binding verbs to capture all policy obligations
BINDING_VERBS = [
    r"\bmust\b", r"\bwill\b", r"\brequires\b", r"\brequired\b",
    r"\bnot permitted\b", r"\bnot reimbursable\b", r"\bmandatory\b",
    r"\bpermitted\b", r"\bprohibited\b", r"\bforfeited\b", r"\bnot allowed\b"
]

def retrieve_policy(file_path: str) -> dict:
    """
    Loads .txt policy file and extracts all numbered clauses.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file {file_path} not found.")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Improved regex: Match section numbers at start of line, capture all text until next section
    # Handles indents and multi-line clause descriptions
    clauses = {}
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\n\s*═|\n\n|$)', re.MULTILINE | re.DOTALL)
    
    matches = pattern.findall(content)
    # Filter matches to ensure we only get the intended clauses
    for clause_num, clause_text in matches:
        # Join lines and collapse whitespace
        cleaned_text = " ".join(line.strip() for line in clause_text.splitlines() if line.strip())
        clauses[clause_num] = cleaned_text
        
    return clauses

def get_high_fidelity_summary(clause_num: str, text: str) -> str:
    """
    Extracts core obligations from a clause text while avoiding softening.
    """
    # Split text into sentences using common punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)
    obligation_sentences = []
    
    for sentence in sentences:
        # Check for binding verbs
        if any(re.search(verb, sentence, re.IGNORECASE) for verb in BINDING_VERBS):
            obligation_sentences.append(sentence)
    
    if not obligation_sentences:
        # If no explicit binding verb found, use verbatim for safety (auditor rule)
        return f"{text} [FLAG: Verbatim Quote]"
    
    # Combine sentences that contain obligations
    summary = " ".join(obligation_sentences)
    
    # Audit Check: If the summary omits significant qualifiers (like BOTH/AND), it's safer to use verbatim
    if any(q in text.upper() for q in ["BOTH", "AND", "ALL", "ADDITIONALLY"]):
        if len(summary) < len(text) * 0.6: # If we've dropped more than 40% of the text, be cautious
            return f"{text} [FLAG: Verbatim Quote]"
            
    return summary

def summarize_policy(clauses: dict) -> str:
    """
    Produces a summary of all extracted clauses, starting from section 2.
    """
    summary_lines = []
    
    # Sort clauses numerically
    def sort_key(s):
        return [int(i) for i in s.split('.')]

    all_nums = sorted(clauses.keys(), key=sort_key)
    
    for num in all_nums:
        # Skip Purpose, Scope, and non-obligation headers (usually section 1)
        if num.startswith("1."):
            continue
            
        summary = get_high_fidelity_summary(num, clauses[num])
        summary_lines.append(f"{num}: {summary}")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Compliance Auditor")
    parser.add_argument("--input", required=True, help="Path to policy.txt")
    parser.add_argument("--output", required=True, help="Path to write summary.txt")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
