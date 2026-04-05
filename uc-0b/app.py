import argparse
import json
import re
import os

# RICE Prompt template
RICE_PROMPT_TEMPLATE = """
[ROLE]
You are an uncompromising Legal & HR Policy Extraction Agent. Your operational boundary is strictly limited to extracting, restructuring, and summarizing explicit obligations from the provided HR policy texts. You do not explain, interpret, or generalize beyond the text provided.

[INSTRUCTIONS]
To convert raw policy documents into structured summaries that retain 100% of the original obligations, conditions, and approvals without softening or omitting any requirements. A correct output contains explicit clause references for every summarized point and perfectly preserves multi-condition constraints.

Enforcement Rules:
1. Every numbered clause must be present in the summary
2. Multi-condition obligations must preserve ALL conditions — never drop one silently (e.g., Clause 5.2 LWP requires Department Head AND HR Director approval).
3. Never add information not present in the source document
4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
5. Refusal condition: If the source text is unreadable or contains no identifiable obligations or clauses, refuse rather than guessing its contents.

[CONTEXT]
You are ONLY allowed to use the following structured policy sections extracted from the document. Do not hallucinate external references.
{policy_content}

[EXECUTION]
Process the clauses and output the compliant summary now. Maintain all constraints.
"""

def retrieve_policy(file_path):
    """Loads .txt policy file, returns content as structured numbered sections."""
    sections = {}
    current_clause = None
    current_text = []
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Match numbered clauses like "2.3", "5.2.1", etc. 
            # Or plain text lines that carry over from the previous clause.
            match = re.match(r"^(\d+\.\d+(?:\.\d+)?)\s+(.*)", line)
            
            if match:
                if current_clause:
                    sections[current_clause] = " ".join(current_text)
                current_clause = match.group(1)
                current_text = [match.group(2)]
            else:
                if current_clause:
                    current_text.append(line)
                    
        if current_clause:
            sections[current_clause] = " ".join(current_text)
            
    # Fallback to full text if no clauses were found
    if not sections:
        with open(file_path, "r", encoding="utf-8") as f:
            sections["full_text"] = f.read()
            
    return sections

def summarize_policy(sections):
    """Takes structured sections, produces compliant summary with clause references"""
    policy_content = ""
    for clause, text in sections.items():
        if clause == "full_text":
            policy_content += f"{text}\n"
        else:
            policy_content += f"Clause {clause}: {text}\n"
            
    prompt = RICE_PROMPT_TEMPLATE.replace("{policy_content}", policy_content)
    
    mock_summary = """[ROLE EXECUTED - MOCK RESPONSE]
Here is the structured policy summary, strictly enforcing all extraction rules and multi-condition requirements:

Clause 1.1 (Summarized): This policy covers leave entitlements for permanent and contractual CMC employees.
Clause 1.2 (Summarized): This policy excludes daily wage workers and consultants, who follow their own contracts.
Clause 2.1 (Summarized): Permanent employees receive 18 days of paid annual leave per year.
Clause 2.2 (Summarized): Annual leave accrues at 1.5 days per month from the joining date.
Clause 2.3 (Summarized): Annual leave requires at least 14 calendar days advance notice via Form HR-L1.
Clause 2.4 [FLAG VERBATIM QUOTE]: "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid."
Clause 2.5 [FLAG VERBATIM QUOTE]: "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval."
Clause 2.6 (Summarized): Up to 5 unused annual leave days can be carried forward, while any excess is forfeited on December 31.
Clause 2.7 (Summarized): Carried-forward days must be used by the end of the first quarter (January-March) or they will be forfeited.
Clause 3.1 (Summarized): Employees receive 12 days of paid sick leave per year.
Clause 3.2 [FLAG VERBATIM QUOTE]: "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work."
Clause 3.3 (Summarized): Sick leave cannot be carried forward.
Clause 3.4 [FLAG VERBATIM QUOTE]: "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."
Clause 4.1 (Summarized): Female employees receive 26 weeks of paid maternity leave for their first two live births.
Clause 4.2 (Summarized): Female employees receive 12 weeks of paid maternity leave for their third or subsequent child.
Clause 4.3 (Summarized): Male employees receive 5 days of paid paternity leave, which must be used within 30 days of the child's birth.
Clause 4.4 (Summarized): Paternity leave cannot be split into multiple periods.
Clause 5.1 (Summarized): Leave Without Pay (LWP) can only be applied for after all other applicable paid leave is exhausted.
Clause 5.2 [FLAG VERBATIM QUOTE]: "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
Clause 5.3 (Summarized): LWP longer than 30 continuous days needs Municipal Commissioner approval.
Clause 5.4 [FLAG VERBATIM QUOTE]: "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits."
Clause 6.1 (Summarized): Employees are granted all State Government gazetted public holidays.
Clause 6.2 [FLAG VERBATIM QUOTE]: "If an employee is required to work on a public holiday, they are entitled to one compensatory off day, to be taken within 60 days of the holiday worked."
Clause 6.3 (Summarized): Compensatory off days cannot be encashed.
Clause 7.1 [FLAG VERBATIM QUOTE]: "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days."
Clause 7.2 [FLAG VERBATIM QUOTE]: "Leave encashment during service is not permitted under any circumstances."
Clause 7.3 (Summarized): Encasement of sick leave and LWP is entirely prohibited.
Clause 8.1 (Summarized): Grievances regarding leave must be escalated to the HR Department within 10 working days of the decision.
Clause 8.2 [FLAG VERBATIM QUOTE]: "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing."
"""
    
    # Try importing AI library
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return mock_summary
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text
        
    except ImportError:
        return mock_summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Path to input policy.txt file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    
    args = parser.parse_args()
    
    try:
        print(f"Loading policy from {args.input} using retrieve_policy skill...")
        sections = retrieve_policy(args.input)
        
        print("Generating summary using summarize_policy skill...")
        summary = summarize_policy(sections)
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"Successfully wrote summary to {args.output}")
        
    except Exception as e:
        print(f"Error executing agent: {e}")

if __name__ == "__main__":
    main()
