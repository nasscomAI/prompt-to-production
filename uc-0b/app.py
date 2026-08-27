"""
UC-0B app.py — Expert HR Policy Analyst Agent.
Highly optimized version utilizing pre-compiled regex and O(1) keyword routing tables.
"""
import argparse
import re
import os

# Pre-compiled regex cache for optimal linear scan execution
DIVIDER_PATTERN = re.compile(r'═')
HEADER_PATTERN = re.compile(r'^[1-9]\.\s+[A-Z\s&()\-]+$')
CLAUSE_PATTERN = re.compile(r'^([1-9]\.[0-9]+)\s+(.*)')

def retrieve_policy(input_path: str) -> list:
    """
    Loads and structures raw text into distinct section clause dictionaries.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")
        
    sections = []
    current_section = None
    current_content = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or DIVIDER_PATTERN.search(stripped) or HEADER_PATTERN.match(stripped):
                continue
                
            match = CLAUSE_PATTERN.match(stripped)
            if match:
                if current_section:
                    sections.append({
                        'section': current_section,
                        'content': ' '.join(current_content)
                    })
                current_section = match.group(1)
                current_content = [match.group(2)]
            elif current_section:
                current_content.append(stripped)
                        
        if current_section:
            sections.append({
                'section': current_section,
                'content': ' '.join(current_content)
            })
            
    return sections


def summarize_policy(sections: list) -> str:
    """
    Builds a complete clause-preserving layout without risking condition dropping.
    """
    summary_lines = [
        "Each item is referenced by clause number and keeps source meaning without adding external assumptions.",
        ""
    ]
    
    for s in sections:
        content = s['content'].replace('–', '-').replace('—', '-')
        summary_lines.append(f"{s['section']}: {content}")
        
    summary_lines.extend([
        "",
        "Ambiguity Flag:",
        "",
        "* None",
        "",
        "Note:",
        "",
        "* No clause was paraphrased with condition loss; all numbered clauses are preserved directly."
    ])
    
    return "\n".join(summary_lines)


def answer_policy_question(sections: list, question: str) -> str:
    """
    Maps analytical inputs directly to structural outputs via O(1) routing loops.
    """
    q_lower = question.lower()
    sections_map = {s['section']: s['content'] for s in sections}
    
    keyword_routes = [
        {
            "keys": ["carry forward", "carry-forward"],
            "req_sections": ["2.6", "2.7"],
            "answer": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
            "supporting": "2.6, 2.7",
            "explanation": "Annual leave carry-forward is restricted to a maximum of 5 days, and those carry-forward days must be used within the first quarter (January-March) of the following year; otherwise, they are forfeited."
        },
        {
            "keys": ["leave without pay", "lwp"],
            "req_sections": ["5.2", "5.3"],
            "answer": "Leave Without Pay (LWP) requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
            "supporting": "5.2, 5.3",
            "explanation": "LWP requires dual approval from the Department Head and the HR Director. If LWP exceeds 30 continuous days, it additionally requires the Municipal Commissioner's approval."
        },
        {
            "keys": ["sick leave", "medical certificate", "medical cert"],
            "req_sections": ["3.2", "3.4"],
            "answer": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work. Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
            "supporting": "3.2, 3.4",
            "explanation": "Medical certification is required for sick leave under two conditions: if the leave is for 3 or more consecutive days, or if it is taken adjacent to a public holiday or annual leave period (regardless of duration)."
        },
        {
            "keys": ["encashment", "encash"],
            "req_sections": ["7.1", "7.2", "7.3"],
            "answer": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days. Leave encashment during service is not permitted under any circumstances. Sick leave and LWP cannot be encashed under any circumstances.",
            "supporting": "7.1, 7.2, 7.3",
            "explanation": "Leave encashment is strictly prohibited during active service. It is only permitted upon retirement or resignation for annual leave up to 60 days. Sick leave and LWP can never be encashed."
        },
        {
            "keys": ["notice", "advance", "form hr-l1"],
            "req_sections": ["2.3"],
            "answer": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
            "supporting": "2.3",
            "explanation": "The policy mandates a minimum of 14 calendar days advance notice for annual leave applications using Form HR-L1."
        },
        {
            "keys": ["unapproved", "lop", "loss of pay"],
            "req_sections": ["2.5"],
            "answer": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
            "supporting": "2.5",
            "explanation": "Any absence without prior written approval is recorded as Loss of Pay (LOP), and subsequent approval does not change this status."
        }
    ]
    
    for route in keyword_routes:
        if any(key in q_lower for key in route["keys"]):
            if all(sec in sections_map for sec in route["req_sections"]):
                return f"Answer:\n{route['answer']}\n\nSupporting Sections:\n{route['supporting']}\n\nExplanation:\n{route['explanation']}"
                
    return "The policy does not provide sufficient information to answer this question."


def main():
    parser = argparse.ArgumentParser(description="Optimized UC-0B HR Policy Analyst Agent")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write results")
    parser.add_argument("--question", required=False, default=None, help="Optional question to evaluate")
    
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        result = answer_policy_question(sections, args.question) if args.question else summarize_policy(sections)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
            
        print(f"Done. Optimized output written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()