# app.py - UC-0B Policy Document Summarizer
import argparse
import re


def retrieve_policy(input_path):
    """Load policy document and return structured clauses."""
    with open(input_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Extract clauses using regex (e.g., 2.3, 3.2) and ignore section headers
    clause_pattern = re.compile(r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\d+\.\s|\n═|\Z)", re.DOTALL)
    clauses = clause_pattern.findall(content)
    
    structured_clauses = {}
    for clause_num, clause_text in clauses:
        # Clean up whitespace, newlines, and section headers
        cleaned_text = " ".join(clause_text.split()).strip()
        if cleaned_text and not re.match(r"^\d+\.\s|^═", cleaned_text):
            structured_clauses[clause_num] = cleaned_text
    
    return structured_clauses


def summarize_policy(clauses, output_path):
    """Generate a summary of the policy document."""
    with open(output_path, "w", encoding="utf-8") as file:
        for clause_num, clause_text in sorted(clauses.items(), key=lambda x: [int(n) for n in x[0].split(".")]):
            # Check for multi-condition obligations (e.g., "Department Head AND HR Director")
            if " and " in clause_text.lower() or " both " in clause_text.lower() or "require approval from" in clause_text.lower():
                file.write(f"**Clause {clause_num}**: {clause_text} (MULTI-CONDITION: VERBATIM)\n")
            else:
                file.write(f"**Clause {clause_num}**: {clause_text}\n")
            file.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize policy documents.")
    parser.add_argument("--input", required=True, help="Path to input policy file.")
    parser.add_argument("--output", required=True, help="Path to output summary file.")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summarize_policy(clauses, args.output)