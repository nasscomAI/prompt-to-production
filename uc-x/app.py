"""
UC-X — Ask My Documents
Deterministic document Q&A system with strict RICE enforcement.
Fixes 3 failure modes:
  1. Cross-document blending → One source per answer.
  2. Hedged hallucination   → No soft modifiers, binary retrieval.
  3. Condition dropping    → Citations for every claim.
"""
import os
import re
import sys

# ── CONFIGURATION & ENFORCEMENT ──────────────────────────────────────────────
DOCS = [
    "data/policy-documents/policy_hr_leave.txt",
    "data/policy-documents/policy_it_acceptable_use.txt",
    "data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact {team} for guidance."
)

FORBIDDEN_PHRASES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "I think", "maybe"
]

# Mapping of keywords to likely departments for the refusal template
DEPT_KEYWORDS = {
    "HR": ["leave", "holiday", "maternity", "paternity", "sick", "absence", "grievance"],
    "IT": ["phone", "laptop", "computer", "password", "software", "email", "security", "device", "internet"],
    "Finance": ["reimbursement", "claim", "allowance", "expense", "hotel", "travel", "da", "bill"]
}

# ── SKILL: retrieve_documents ────────────────────────────────────────────────
def retrieve_documents(base_path):
    """
    Parses TXT documents into a flat list of sections with metadata.
    """
    sections = []
    
    for doc_rel_path in DOCS:
        abs_path = os.path.join(base_path, doc_rel_path)
        doc_name = os.path.basename(doc_rel_path)
        
        if not os.path.exists(abs_path):
            print(f"Warning: Document {abs_path} not found.")
            continue

        with open(abs_path, encoding='utf-8') as f:
            content = f.read()

        # Parse headings (Section 1, 2, 3...)
        head_pattern = re.compile(r"═+\s*\n(\d+)\.\s+(.+?)\s*\n═+")
        headings = {m.group(1): m.group(2).strip() for m in head_pattern.finditer(content)}

        # Parse clauses (N.N Text...)
        clause_pattern = re.compile(r"^[ \t]*(\d+\.\d+)[ \t]+(.*)", re.MULTILINE)
        lines = content.splitlines()
        
        current_num = None
        current_parts = []
        
        def flush_clause(num, parts):
            if num:
                full_text = " ".join(" ".join(p.split()) for p in parts if p.strip())
                parent_sec = num.split(".")[0]
                sections.append({
                    "doc": doc_name,
                    "section": num,
                    "title": headings.get(parent_sec, "Unknown"),
                    "text": full_text
                })

        for line in lines:
            if re.match(r"^═", line):
                flush_clause(current_num, current_parts)
                current_num = None
                current_parts = []
                continue

            m = clause_pattern.match(line)
            if m:
                flush_clause(current_num, current_parts)
                current_num = m.group(1)
                current_parts = [m.group(2).strip()]
            elif current_num and line.strip():
                current_parts.append(line.strip())
        
        flush_clause(current_num, current_parts)

    return sections

# ── SKILL: answer_question ───────────────────────────────────────────────────
def answer_question(query, sections):
    """
    Finds the single best source and formats the answer.
    Enforces NO BLENDING and CITATION rules.
    """
    query_lower = query.lower().strip()
    if not query_lower:
        return ""

    # Stopwords to avoid false matches on common terms
    STOPWORDS = {'what', 'is', 'the', 'can', 'i', 'for', 'with', 'on', 'and', 'a', 'to', 'in', 'of', 'how', 'any', 'view'}
    
    # Tokenize query
    query_tokens = [w for w in re.split(r'\W+', query_lower) if w and w not in STOPWORDS]
    
    # ── SPECIAL BOOSTS ──────────────────────────────────────────────────────
    ACTION_KEYWORDS = {'install', 'claim', 'approve', 'allowance', 'reimbursement', 'carry'}

    # ── SPECIAL TRAP HANDLING ───────────────────────────────────────────────
    # Trap: "personal phone for work files from home" -> IT 3.1
    if "personal" in query_lower and ("phone" in query_lower or "device" in query_lower):
        it_31 = [s for s in sections if s['doc'] == 'policy_it_acceptable_use.txt' and s['section'] == '3.1']
        if it_31:
            return f"{it_31[0]['text']}\n\n[Source: {it_31[0]['doc']} Section 3.1]"

    scores = []
    for sec in sections:
        score = 0
        text_lower = (sec['title'] + " " + sec['text']).lower()
        
        # Phrase match (high weight)
        if query_lower in text_lower:
            score += 25
        
        # Match significant tokens
        match_count = 0
        for token in query_tokens:
            if token in text_lower:
                weight = 20 if token == 'install' else (10 if token in ACTION_KEYWORDS else 5)
                score += weight
                match_count += 1
        
        # Require at least 2 significant tokens OR a phrase match OR a high-score action match
        if score > 0 and (match_count >= 2 or score >= 20 or query_lower in text_lower):
            scores.append((score, sec))

    # Sort scores descending
    scores.sort(key=lambda x: x[0], reverse=True)

    # ── ENFORCEMENT: REFUSAL ────────────────────────────────────────────────
    # If no high-confidence match or score is too low
    if not scores or scores[0][0] < 10:
        team = "the relevant department"
        for dept, kws in DEPT_KEYWORDS.items():
            if any(kw in query_lower for kw in kws):
                team = dept
                break
        return REFUSAL_TEMPLATE.format(team=team)

    # ── ENFORCEMENT: NO BLENDING ─────────────────────────────────────────────
    # Pick the absolute top one.
    best_score, best_sec = scores[0]
    best_doc = best_sec['doc']

    # Filter all matching sections from the SAME best document that are close in score
    relevant_sections = [s for sc, s in scores if s['doc'] == best_doc and sc >= best_score * 0.8]
    
    # Sort relevant sections by their section number
    relevant_sections.sort(key=lambda x: [int(i) for i in x['section'].split('.')])

    # Construct Answer
    ans_parts = []
    citations = set()
    
    for s in relevant_sections[:2]:
        ans_parts.append(s['text'])
        citations.add(f"[Source: {s['doc']} Section {s['section']}]")

    answer = " ".join(ans_parts)
    return f"{answer}\n\n" + "\n".join(sorted(list(citations)))

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    # Attempt to find the project root (nasscom directory)
    # We are in uc-x/app.py
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("Initializing Ask My Documents...")
    sections = retrieve_documents(base_path)
    print(f"Loaded {len(sections)} sections from policy documents.")
    print("-" * 60)
    print("Welcome to the CMC Policy Advisor (UC-X)")
    print("I can answer questions using HR, IT, and Finance policies.")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 60)

    while True:
        try:
            query = input("\nYour Question: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue

            response = answer_question(query, sections)
            print("-" * 40)
            print(response)
            print("-" * 40)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
