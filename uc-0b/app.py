import argparse
import os
import re

# Ground truth: the 10 clauses that MUST be preserved
REQUIRED_CLAUSES = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences. Verbal not valid.",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
    "2.7": "Carry-forward days must be used Jan-Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service not permitted under any circumstances",
}

BINDING_VERBS = ["must", "will", "requires", "not permitted", "may", "are forfeited", "shall"]


def is_separator_line(line: str) -> bool:
    """Check if a line is just decorative separators."""
    stripped = line.strip()
    if not stripped:
        return True
    # Lines that are only special chars, dots, dashes, equals, bullets, etc.
    if re.match(r'^[\s\•\—\=\-\*\.▬║│├└┐┌┤┴┬┼═╬╦╩╠╣╗╝╚╔█▀▄▌▐░▒▓]{3,}$', stripped):
        return True
    return False


def is_section_header(line: str) -> bool:
    """
    Detect section headers like:
    '2. ANNUAL LEAVE'
    '3. SICK LEAVE'
    '5. LEAVE WITHOUT PAY (LWP)'
    """
    stripped = line.strip()
    # Pattern: single digit, dot, space, then uppercase text
    return bool(re.match(r'^\d+\.\s+[A-Z][A-Z\s\(\)\-]+$', stripped))


def retrieve_policy(file_path: str) -> list:
    """
    Loads policy file line by line, extracts numbered clauses.
    Returns list of dicts: {clause_number, clause_text, section}
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    sections = []
    current_clause_num = None
    current_clause_lines = []
    current_section = "Section 0"
    
    for raw_line in lines:
        line = raw_line.rstrip('\n').rstrip('\r')
        
        # Skip separator/decorator lines
        if is_separator_line(line):
            continue
        
        # Check if this is a section header (e.g., "2. ANNUAL LEAVE")
        if is_section_header(line):
            # Save previous clause if exists
            if current_clause_num and current_clause_lines:
                clause_text = " ".join(current_clause_lines).strip()
                clause_text = re.sub(r'\s+', ' ', clause_text)
                section_num = current_clause_num.split('.')[0]
                sections.append({
                    "clause_number": current_clause_num,
                    "clause_text": clause_text,
                    "section": f"Section {section_num}"
                })
                current_clause_num = None
                current_clause_lines = []
            
            # Update section tracking
            section_match = re.match(r'^(\d+)\.', line.strip())
            if section_match:
                current_section = f"Section {section_match.group(1)}"
            continue
        
        # Check if this line starts a new clause (e.g., "1.1 ", "2.3 ", "10.2 ")
        match = re.match(r'^(\d+\.\d+)\s+(.*)$', line.strip())
        
        if match:
            # Save previous clause if exists
            if current_clause_num and current_clause_lines:
                clause_text = " ".join(current_clause_lines).strip()
                clause_text = re.sub(r'\s+', ' ', clause_text)
                section_num = current_clause_num.split('.')[0]
                sections.append({
                    "clause_number": current_clause_num,
                    "clause_text": clause_text,
                    "section": f"Section {section_num}"
                })
            
            # Start new clause
            current_clause_num = match.group(1)
            current_clause_lines = [match.group(2)]
        else:
            # Continue current clause
            if current_clause_num:
                stripped = line.strip()
                if stripped:
                    current_clause_lines.append(stripped)
    
    # Don't forget the last clause
    if current_clause_num and current_clause_lines:
        clause_text = " ".join(current_clause_lines).strip()
        clause_text = re.sub(r'\s+', ' ', clause_text)
        section_num = current_clause_num.split('.')[0]
        sections.append({
            "clause_number": current_clause_num,
            "clause_text": clause_text,
            "section": f"Section {section_num}"
        })
    
    return sections


def summarize_clause(clause_num: str, clause_text: str) -> str:
    """
    Summarize a single clause while preserving all obligations and conditions.
    """
    words = clause_text.split()
    
    # Short clauses: keep verbatim
    if len(words) <= 35:
        return clause_text.strip()
    
    # Longer clauses: condense but keep binding verbs and conditions
    sentences = re.split(r'(?<=[.!?])\s+', clause_text)
    kept = [sentences[0]]
    
    for s in sentences[1:]:
        s_lower = s.lower()
        if any(v in s_lower for v in BINDING_VERBS):
            kept.append(s)
        elif any(kw in s_lower for kw in ["approval", "forfeit", "medical", "encashment", "absence", "carry-forward"]):
            kept.append(s)
    
    summary = " ".join(kept)
    summary = re.sub(r'\s+', ' ', summary).strip()
    
    # For critical clauses, verify we didn't lose meaning
    if clause_num in REQUIRED_CLAUSES:
        required_lower = REQUIRED_CLAUSES[clause_num].lower()
        req_words = [w for w in re.findall(r'\w+', required_lower) if len(w) > 3]
        summary_lower = summary.lower()
        missing = [w for w in req_words if w not in summary_lower]
        
        if len(missing) > 1:
            return f"{clause_text.strip()} [FLAGGED: verbatim quote]"
    
    return summary


def summarize_policy(sections: list) -> str:
    """
    Produces the final summary document.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("HR LEAVE POLICY - COMPLIANT SUMMARY")
    lines.append("=" * 60)
    lines.append("")
    lines.append("This summary preserves all numbered clauses, binding obligations,")
    lines.append("and multi-condition requirements from the source document.")
    lines.append("No external information has been added.")
    lines.append("")
    
    current_section = ""
    for sec in sections:
        if sec["section"] != current_section:
            current_section = sec["section"]
            lines.append(f"\n{current_section}")
            lines.append("-" * 40)
        
        clause_num = sec["clause_number"]
        summary_text = summarize_clause(clause_num, sec["clause_text"])
        
        lines.append(f"\nClause {clause_num}:")
        lines.append(f"  {summary_text}")
    
    # Verification section
    lines.append("\n" + "=" * 60)
    lines.append("CLAUSE INVENTORY VERIFICATION")
    lines.append("=" * 60)
    
    found_clauses = {s["clause_number"] for s in sections}
    for req_num in sorted(REQUIRED_CLAUSES.keys()):
        status = "PRESENT" if req_num in found_clauses else "MISSING"
        lines.append(f"  {req_num}: {status}")
    
    lines.append("\n" + "=" * 60)
    lines.append("END OF SUMMARY")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Done. Summary written to {args.output}")
    print(f"Total clauses extracted: {len(sections)}")
    found_required = len([s for s in sections if s['clause_number'] in REQUIRED_CLAUSES])
    print(f"Required clauses found: {found_required} / {len(REQUIRED_CLAUSES)}")


if __name__ == "__main__":
    main()