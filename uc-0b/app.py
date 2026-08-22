"""
UC-0B app.py — Final Strict Implementation.
"""
import argparse
import os
import urllib.request
import json
import re

MANDATORY_CLAUSES = {
    "2.3": ["14", "advance"],
    "2.4": ["written", "verbal"],
    "2.5": ["unapproved", "lop", "loss of pay"],
    "2.6": ["5", "carry", "forfeited"],
    "2.7": ["jan", "mar", "quarter", "forfeited"],
    "3.2": ["3", "medical", "48"],
    "3.4": ["holiday", "cert"],
    "5.2": ["department head", "hr director"],
    "5.3": ["30", "commissioner"],
    "7.2": ["encashment", "permitted"]
}

def extract_clause_verbatim(policy_text: str, clause_num: str) -> str:
    lines = policy_text.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith(clause_num):
            clause_text = [line.strip()]
            for next_line in lines[i+1:]:
                if re.match(r'^\d+\.\d+', next_line.strip()) or next_line.strip().startswith('══'):
                    break
                if next_line.strip():
                    clause_text.append(next_line.strip())
            return " ".join(clause_text)
    return ""

def validate_and_repair(summary: str, policy_text: str) -> str:
    summary_lower = summary.lower()
    repairs = []
    
    for clause, keywords in MANDATORY_CLAUSES.items():
        missing_keys = [k for k in keywords if k not in summary_lower]
        
        # Explicit protection for 5.2
        if clause == "5.2":
            if "department head" not in summary_lower or "hr director" not in summary_lower:
                repairs.append(clause)
        else:
            # Deterministic detection of weakened language / missing conditions
            if len(missing_keys) >= max(1, len(keywords) // 2):
                repairs.append(clause)
                
    if repairs:
        repair_text = "\n\n--- DETERMINISTIC REPAIRS (VERBATIM QUOTES REQUIRED DUE TO MEANING LOSS) ---\n"
        for r in repairs:
            verbatim = extract_clause_verbatim(policy_text, r)
            repair_text += f"[FLAGGED: Clause {r} omitted or meaning altered] {verbatim}\n"
        summary += repair_text
        
    return summary

def summarize_strict(text: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Phase 2 Deterministic test mock
        # Simulates an LLM that drops Clause 2.5 entirely and fails Clause 5.2's two-approver trap.
        mock_summary = """HR Leave Policy Summary:

2. Annual Leave
Employees get 18 days annual leave. (2.3) Must submit application 14 days in advance. (2.4) Written approval is required. (2.6) Max 5 days can be carried forward, otherwise forfeited. (2.7) Must be used Jan-Mar.

3. Sick Leave
12 days sick leave. (3.2) 3+ days require medical cert within 48 hours. (3.4) Cert also required before/after holiday.

5. Leave Without Pay
(5.2) LWP requires Department Head approval. (5.3) >30 days requires Municipal Commissioner.

7. Leave Encashment
(7.2) Not permitted during service.
"""
        return validate_and_repair(mock_summary, text)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = (
        "Summarize this HR leave policy. "
        "You MUST explicitly include information for clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2. "
        "Do NOT soften mandatory language (use 'must', not 'should'). "
        "For 5.2, explicitly mention BOTH the Department Head and HR Director. "
        "Keep exact numbers, conditions, and penalties intact. "
        "Do not invent external facts.\n\n"
        f"{text}"
    )
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            llm_summary = result["candidates"][0]["content"]["parts"][0]["text"]
            return validate_and_repair(llm_summary, text)
    except Exception as e:
        return f"Error: {e}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    with open(args.input, "r", encoding="utf-8") as f:
        policy_text = f.read()
        
    summary = summarize_strict(policy_text)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
        
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
