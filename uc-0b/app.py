"""
UC-0B — Policy Summarizer
Implementation guided by RICE framework, agents.md, and skills.md.
"""
import argparse
import os
import re

def retrieve_policy(file_path: str):
    """
    Loads a plain-text policy file and returns its content parsed into structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    structured = []
    current_clause = None
    current_text = []
    
    for line in lines:
        # Match numbered clauses like "1.1 ", "2.3 "
        match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
        if match:
            if current_clause:
                structured.append({"clause": current_clause, "text": " ".join(current_text)})
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
        # Append lines belonging to the current clause
        elif current_clause and line.strip() and not line.startswith("══") and not re.match(r"^\d+\.\s+", line):
            current_text.append(line.strip())
        # Reset at headers or separators
        elif line.startswith("══") or re.match(r"^\d+\.\s+", line):
            if current_clause:
                structured.append({"clause": current_clause, "text": " ".join(current_text)})
                current_clause = None
                current_text = []
                
    if current_clause:
        structured.append({"clause": current_clause, "text": " ".join(current_text)})
        
    if not structured:
        with open(file_path, "r", encoding="utf-8") as f:
            return {"raw_text": f.read(), "flag": "NEEDS_REVIEW"}
            
    return structured


def summarize_policy(sections) -> str:
    """
    Takes structured numbered policy sections and produces a compliant summary.
    """
    if not sections:
        raise ValueError("No policy content was provided for summarization.")
        
    if isinstance(sections, dict) and "raw_text" in sections:
        return sections["raw_text"] + "\n\n[NEEDS_REVIEW: Document structure could not be parsed.]"
        
    summary_lines = [
        "HR LEAVE POLICY SUMMARY",
        "=======================\n"
    ]
    
    for section in sections:
        clause = section["clause"]
        text = section["text"]
        lower_text = text.lower()
        
        # Enforcement Rules:
        # 1. Every numbered clause must be present (we iterate over all).
        # 2. Multi-condition obligations preserve ALL conditions.
        # 3. Binding verbs must not be softened.
        # 4. Never add information not present in source.
        # 5. If a clause cannot be summarised without meaning loss, quote verbatim + NEEDS_REVIEW.
        
        has_binding_verb = any(v in lower_text for v in ["must", "will", "requires", "not permitted"])
        
        # Identify multi-condition or complex clauses that risk meaning loss if summarized
        complex_keywords = ["and", "or", "unless", "regardless", "subject to", "before or after", "only after", "consecutive"]
        has_complex_condition = any(kw in lower_text for kw in complex_keywords)
        
        if has_complex_condition or has_binding_verb:
            # Fallback to verbatim quote + flag to ensure no conditions or binding verbs are dropped
            summary_lines.append(f"Clause {clause}: \"{text}\" [NEEDS_REVIEW]")
        else:
            # Simple summarization formatting for safe clauses
            summary_lines.append(f"Clause {clause}: {text}")
            
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (e.g. policy_hr_leave.txt)")
    parser.add_argument("--output", required=True, help="Path to write the summary output")
    args = parser.parse_args()
    
    try:
        # Skill 1: Retrieve Policy
        sections = retrieve_policy(args.input)
        
        # Skill 2: Summarize Policy
        summary = summarize_policy(sections)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"Successfully generated summary at {args.output}")
        
    except Exception as e:
        print(f"Error processing policy: {e}")
        exit(1)

if __name__ == "__main__":
    main()
