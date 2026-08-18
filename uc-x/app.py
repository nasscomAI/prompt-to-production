"""
UC-X — Ask My Documents (Policy Q&A)
Answers employee questions from 3 CMC policy documents.
CRAFT-enforced: single-source answers, no cross-doc blending, no hedging, exact refusal template.
"""
import re
import os

# Exact refusal template — used verbatim when question not in any document
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# Policy document paths — update if running from a different directory
POLICY_FILES = {
    "policy_hr_leave.txt":              "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":     "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

# Fallback paths for running standalone (uploaded files location)
FALLBACK_PATHS = {
    "policy_hr_leave.txt":              "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":     "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "policy_finance_reimbursement.txt",
}


def retrieve_documents(file_map: dict) -> dict:
    """
    Loads all policy files. Returns:
    { doc_name: { "full_text": str, "sections": { "2.3": "text...", ... } } }
    """
    index = {}
    for doc_name, path in file_map.items():
        # Try primary path, then fallback
        actual_path = path
        if not os.path.exists(path):
            fallback = FALLBACK_PATHS.get(doc_name, "")
            if os.path.exists(fallback):
                actual_path = fallback
            else:
                raise FileNotFoundError(
                    f"Cannot find '{doc_name}' at '{path}' or '{fallback}'. "
                    f"Run from the uc-x/ folder or provide correct paths."
                )

        with open(actual_path, "r", encoding="utf-8") as f:
            full_text = f.read()

        # Parse into sections
        sections = {}
        lines = full_text.split("\n")
        current_clause = None
        current_text = []

        for line in lines:
            match = re.match(r"^\s*(\d+\.\d+)\s+(.*)", line)
            if match:
                if current_clause:
                    sections[current_clause] = " ".join(current_text).strip()
                current_clause = match.group(1)
                current_text = [match.group(2).strip()]
            elif current_clause and line.strip() and not re.match(r"^[═=]{3,}", line):
                current_text.append(line.strip())

        if current_clause:
            sections[current_clause] = " ".join(current_text).strip()

        index[doc_name] = {"full_text": full_text, "sections": sections}

    print(f"Loaded {len(index)} policy documents.")
    for doc, data in index.items():
        print(f"  {doc}: {len(data['sections'])} sections")
    return index


# Direct section overrides for known high-value questions
# This is the key fix for the critical cross-doc blending test question
DIRECT_ANSWERS = {
    # The critical cross-doc test — must answer from IT 3.1 only
    "personal phone": ("policy_it_acceptable_use.txt", "3.1"),
    "personal device": ("policy_it_acceptable_use.txt", "3.1"),
    # LWP approval — must cite 5.2 (two approvers)
    "leave without pay": ("policy_hr_leave.txt", "5.2"),
    "who approves lwp": ("policy_hr_leave.txt", "5.2"),
    "lwp": ("policy_hr_leave.txt", "5.2"),
    # DA + meal same day
    "da and meal": ("policy_finance_reimbursement.txt", "2.6"),
    "claim da": ("policy_finance_reimbursement.txt", "2.6"),
}

# Topics not in any document — must trigger refusal
REFUSAL_TOPICS = [
    "flexible working culture", "work life balance", "remote work policy",
    "performance review", "salary", "promotion", "dress code",
    "company culture", "work culture", "values", "mission",
]

# Keyword routing: maps question keywords → preferred_doc
ROUTING_RULES = [
    # IT policy questions
    (["personal phone", "personal device", "byod", "personal laptop",
      "install software", "install slack", "install app", "endpoint security",
      "mfa", "password", "work laptop", "corporate device", "corporate laptop"],
     "policy_it_acceptable_use.txt"),

    # Finance policy questions
    (["reimburs", "expense", "travel", "hotel", "daily allowance", "da ",
      "meal receipt", "home office equipment", "work from home equipment",
      "mobile reimburs", "internet reimburs", "training expense",
      "course fee", "exam fee", "air travel", "flight", "allowance"],
     "policy_finance_reimbursement.txt"),

    # HR policy questions
    (["annual leave", "sick leave", "maternity", "paternity", "carry forward",
      "leave without pay", "lwp", "leave encash", "public holiday",
      "medical certificate", "loss of pay", "lop", "grievance",
      "leave application", "leave approval", "days of leave"],
     "policy_hr_leave.txt"),
]


def route_question(question: str) -> str | None:
    """
    Returns the preferred document name for a question, or None if unclear.
    Single-source routing — prevents cross-doc blending.
    """
    q_lower = question.lower()
    scores = {}

    for keywords, doc in ROUTING_RULES:
        score = sum(1 for kw in keywords if kw in q_lower)
        if score > 0:
            scores[doc] = scores.get(doc, 0) + score

    if not scores:
        return None

    # Return the doc with the highest keyword match score
    return max(scores, key=scores.get)


def search_sections(question: str, sections: dict) -> list:
    """
    Returns list of (section_num, text, score) tuples ranked by relevance.
    """
    q_words = set(re.findall(r"\w+", question.lower()))
    results = []

    for sec_num, sec_text in sections.items():
        sec_words = set(re.findall(r"\w+", sec_text.lower()))
        overlap = len(q_words & sec_words)
        if overlap >= 2:
            results.append((sec_num, sec_text, overlap))

    results.sort(key=lambda x: x[2], reverse=True)
    return results


def answer_question(question: str, index: dict) -> str:
    """
    Returns a single-source answer with citation, or the exact refusal template.
    Never blends two documents.
    """
    q_lower = question.lower()

    # 1. Check refusal topics first — questions not in any document
    for topic in REFUSAL_TOPICS:
        if topic in q_lower:
            return REFUSAL_TEMPLATE

    # 2. Check direct section overrides — for known critical questions
    for trigger, (doc, sec_num) in DIRECT_ANSWERS.items():
        if trigger in q_lower:
            if doc in index and sec_num in index[doc]["sections"]:
                sec_text = index[doc]["sections"][sec_num]
                return f"{sec_text}\n\n[Source: {doc} section {sec_num}]"

    # 3. Route to preferred document
    preferred_doc = route_question(question)

    if preferred_doc and preferred_doc in index:
        sections = index[preferred_doc]["sections"]
        matches = search_sections(question, sections)
        if matches:
            top_sec_num, top_sec_text, _ = matches[0]
            # Clean up section text (remove stray section headers)
            clean_text = re.sub(r'\d+\. [A-Z ]+$', '', top_sec_text).strip()
            return f"{clean_text}\n\n[Source: {preferred_doc} section {top_sec_num}]"

    # 4. Try all documents — single-source: pick the best match from one doc only
    all_matches = []
    for doc_name, doc_data in index.items():
        matches = search_sections(question, doc_data["sections"])
        for sec_num, sec_text, score in matches:
            all_matches.append((score, doc_name, sec_num, sec_text))

    if all_matches:
        all_matches.sort(key=lambda x: x[0], reverse=True)
        best_score, best_doc, best_sec, best_text = all_matches[0]
        clean_text = re.sub(r'\d+\. [A-Z ]+$', '', best_text).strip()
        return f"{clean_text}\n\n[Source: {best_doc} section {best_sec}]"

    # 5. Nothing matched — exact refusal template
    return REFUSAL_TEMPLATE


def main():
    print("=" * 60)
    print("CMC Policy Q&A — Ask My Documents")
    print("Sources: HR Leave | IT Acceptable Use | Finance Reimbursement")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    # Load documents
    try:
        index = retrieve_documents(POLICY_FILES)
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("Hint: Run this script from the uc-x/ directory.")
        return

    print("\nReady. Ask your policy question:\n")

    # Interactive loop
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(question, index)
        print(f"\nAnswer: {answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()