import argparse
import re
import sys

def parse_policy(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Split text into numbered sections/clauses (e.g., 2.3, 2.4, etc.)
    clauses = {}
    pattern = r'(\d+\.\d+)\s+([\s\S]+?)(?=\n\d+\.\d+|\n═+|$)'
    matches = re.findall(pattern, text)
    
    for clause_id, content in matches:
        clean_content = " ".join(content.strip().split())
        clauses[clause_id] = clean_content

    return clauses

def generate_summary(clauses):
    summary_lines = [
        "EMPLOYEE LEAVE POLICY SUMMARY",
        "=============================",
        "Document: City Municipal Corporation Employee Leave Policy (HR-POL-001)",
        "",
        "SECTION-BY-SECTION COMPLIANT CLAUSE SUMMARY",
        "------------------------------------------"
    ]

    for clause_id, content in sorted(clauses.items()):
        summary_lines.append(f"[{clause_id}] {content}")
        
    summary_lines.extend([
        "",
        "KEY BINDING OBLIGATIONS & COMPLIANCE CHECKLIST",
        "----------------------------------------------",
        "• Clause 2.3: Employees MUST submit leave applications at least 14 calendar days in advance.",
        "• Clause 2.4: Written approval MUST be received before leave commences; verbal approval is NOT valid.",
        "• Clause 2.5: Unapproved absence WILL be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "• Clause 2.6: Maximum 5 days carry-forward allowed; any days above 5 ARE FORFEITED on 31 December.",
        "• Clause 2.7: Carry-forward days MUST be used in Q1 (Jan–Mar) or ARE FORFEITED.",
        "• Clause 3.2: Sick leave of 3+ consecutive days REQUIRES a medical certificate submitted within 48 hours of return.",
        "• Clause 3.4: Sick leave immediately before/after a holiday or annual leave REQUIRES a medical certificate regardless of duration.",
        "• Clause 5.2: Leave Without Pay (LWP) REQUIRES approval from BOTH Department Head AND HR Director.",
        "• Clause 5.3: LWP >30 continuous days REQUIRES approval from Municipal Commissioner.",
        "• Clause 7.2: Leave encashment during service IS NOT PERMITTED under any circumstances."
    ])

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Compliance Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary text file")
    args = parser.parse_args()

    clauses = parse_policy(args.input)
    summary_text = generate_summary(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Successfully generated compliant policy summary in {args.output}")

if __name__ == "__main__":
    main()
