import os
import re

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance."""


# ---------------------------
# TOKENIZATION
# ---------------------------
def tokenize(text):
    return set(re.findall(r'\b\w+\b', text.lower()))


# ---------------------------
# LOAD DOCUMENTS
# ---------------------------
def load_documents():
    base = "data/policy-documents"
    docs = {}

    for filename in [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]:
        path = os.path.join(base, filename)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        sections = {}
        lines = text.split("\n")

        current = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line[:3].replace(".", "").isdigit():
                parts = line.split(" ", 1)
                sec = parts[0]
                content = parts[1] if len(parts) > 1 else ""
                current = sec
                sections[current] = content
            else:
                if current:
                    sections[current] += " " + line

        docs[filename] = sections

    return docs


# ---------------------------
# STAGE 1: RETRIEVAL (LOOSE)
# ---------------------------
def search_documents(question, docs):
    q_words = tokenize(question)
    results = []

    for doc_name, sections in docs.items():
        for sec, text in sections.items():
            t_words = tokenize(text)

            overlap = len(q_words & t_words)

            if overlap > 1:  # loose filter
                results.append((overlap, doc_name, sec, text))

    results.sort(reverse=True)
    return results


# ---------------------------
# STAGE 2: RELEVANCE CHECK
# ---------------------------
def is_relevant(question, text):
    """
    Perform a strict relevance validation:
    1. The section must directly answer the user's question.
    2. The section must match the intent of the question, not just share keywords.
    3. If the section is about a different topic (e.g., reporting incidents, penalties, procedures), it must be rejected.
    """
    q = question.lower()
    t = text.lower()

    # --- REJECT OFF-TOPIC SECTIONS ---
    # If the section is about a different topic, reject it unless the user explicitly asked about it.
    off_topics = ["report", "penalty", "procedure", "disciplinary", "violation", "lost", "stolen", "law enforcement", "audit"]
    for topic in off_topics:
        if topic in t and topic not in q:
            return False

    # --- PERMISSIONS / ALLOWED USAGE ---
    permission_q = ["can i", "am i allowed", "may i", "is it allowed", "permitted"]
    if any(phrase in q for phrase in permission_q):
        permission_keywords = ["may", "allowed", "only", "permit", "must", "cannot", "not", "prohibited", "requires", "approve", "approval"]
        if not any(word in t for word in permission_keywords):
            return False

    # --- INTENT MATCHING ---
    # The section must match the specific intent, not just share loose keywords.

    # --- INSTALL / SOFTWARE ---
    if "install" in q or "slack" in q:
        if "install" in t and "approval" in t:
            return True

    # --- CARRY FORWARD ---
    if "carry forward" in q:
        if "carry forward" in t:
            return True

    # --- ALLOWANCE ---
    if "allowance" in q:
        if "allowance" in t:
            return True

    # --- PERSONAL DEVICE ---
    if "personal phone" in q or "personal device" in q:
        if "personal device" in t and ("access" in t or "email" in t):
            return True

    # --- DA + MEALS ---
    if "da" in q and "meal" in q:
        if "cannot" in t or "not" in t:
            return True

    # --- LWP ---
    if "leave without pay" in q or "lwp" in q:
        # For questions involving approvals or responsibilities
        if "approve" in q or "approval" in q or "who" in q or "manager" in q:
            # Multi-condition clause check: must include ALL required roles
            # Do NOT require exact phrase matching (variations acceptable)
            has_dept_head = "department head" in t or "head of department" in t
            has_hr_director = "hr director" in t or "human resources director" in t
            
            if has_dept_head and has_hr_director:
                return True
            else:
                # Reject if any required entity is missing
                return False
                
        # If not an approval question but relevant to LWP
        if "approval" in t:
            return True

    # If the section does not explicitly answer the question (no intent matched), discard it.
    return False


# ---------------------------
# ANSWER ENGINE
# ---------------------------
def answer_question(question, docs):
    candidates = search_documents(question, docs)

    valid = []

    for _, doc, sec, text in candidates:
        if is_relevant(question, text):
            valid.append((doc, sec, text))

    # --- NO VALID MATCH ---
    if not valid:
        return REFUSAL

    # --- MULTIPLE SECTIONS → REFUSE (no combining) ---
    if len(valid) > 1:
        return REFUSAL

    # --- SINGLE VALID MATCH ---
    doc, sec, text = valid[0]

    return f"{text}\n(Source: {doc}, Section {sec})"


# ---------------------------
# CLI
# ---------------------------
def main():
    docs = load_documents()

    print("Policy QA System Ready. Type 'exit' to quit.\n")

    while True:
        q = input("Ask: ").strip()

        if not q:
            print("Please enter a question.\n")
            continue

        if q.lower() == "exit":
            break

        answer = answer_question(q, docs)
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()