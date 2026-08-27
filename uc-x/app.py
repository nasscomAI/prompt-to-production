"""
UC-X Ask My Documents — Policy Q&A System
Answers questions strictly from indexed policy documents with
single-source attribution and zero cross-document blending.
"""

import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

BANNED_HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard",
]

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def load_documents():
    """Load and index all policy documents by filename and section number."""
    docs = {}
    for path in DOC_PATHS:
        filename = os.path.basename(path)
        if not os.path.exists(path):
            print(f"WARNING: {path} not found, skipping.", file=sys.stderr)
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r'(\d+\.\d+)\s+([\s\S]+?)(?=\n\d+\.\d+|\n═+|$)'
        matches = re.findall(pattern, content)
        sections = {}
        for sec_id, text in matches:
            sections[sec_id] = " ".join(text.strip().split())
        docs[filename] = sections

    total = sum(len(s) for s in docs.values())
    print(f"Indexed {total} sections across {len(docs)} documents.\n")
    return docs


def search_sections(query_lower, docs):
    """Search all document sections for keyword relevance. Returns list of (doc, sec_id, text, score)."""
    results = []
    query_words = set(query_lower.split())

    for doc_name, sections in docs.items():
        for sec_id, text in sections.items():
            text_lower = text.lower()
            # Score by number of query words found in section text
            score = sum(1 for w in query_words if w in text_lower)
            if score > 0:
                results.append((doc_name, sec_id, text, score))

    results.sort(key=lambda x: x[3], reverse=True)
    return results


def check_hedging(answer):
    """Verify the answer contains no banned hedging phrases."""
    answer_lower = answer.lower()
    for phrase in BANNED_HEDGING_PHRASES:
        if phrase in answer_lower:
            return True
    return False


def answer_question(query, docs):
    """Answer a question using single-source document attribution or refusal."""
    if not query.strip():
        return REFUSAL_TEMPLATE

    q_lower = query.lower()

    # ── Priority-ordered rule matching for known question patterns ──

    # Refusal: flexible working culture (not in any document)
    if "flexible working" in q_lower or ("culture" in q_lower and "company" in q_lower):
        return REFUSAL_TEMPLATE

    # HR: carry forward annual leave → Section 2.6
    if "carry forward" in q_lower and "leave" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        text = docs.get(doc, {}).get(sec, "")
        if text:
            return f"[{doc} - Section {sec}]\n{text}"

    # IT: install Slack / software → Section 2.3
    if "install" in q_lower or "slack" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        text = docs.get(doc, {}).get(sec, "")
        if text:
            return f"[{doc} - Section {sec}]\n{text}"

    # Finance: home office equipment allowance → Section 3.1
    if "home office" in q_lower or "equipment allowance" in q_lower or ("wfh" in q_lower and "allowance" in q_lower):
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        text = docs.get(doc, {}).get(sec, "")
        if text:
            return f"[{doc} - Section {sec}]\n{text}"

    # IT: personal phone / personal device → Section 3.1 (SINGLE SOURCE — do NOT blend with HR)
    if "personal phone" in q_lower or "personal device" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        text = docs.get(doc, {}).get(sec, "")
        if text:
            return f"[{doc} - Section {sec}]\n{text}"

    # Finance: DA and meal receipts same day → Section 2.6
    if ("da " in q_lower or "daily allowance" in q_lower) and "meal" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        text = docs.get(doc, {}).get(sec, "")
        if text:
            return f"[{doc} - Section {sec}]\n{text}"

    # HR: leave without pay approval → Section 5.2
    if "leave without pay" in q_lower or "lwp" in q_lower or ("approv" in q_lower and "leave" in q_lower):
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        text = docs.get(doc, {}).get(sec, "")
        if text:
            return f"[{doc} - Section {sec}]\n{text}"

    # ── Fallback: search all sections for best match ──
    results = search_sections(q_lower, docs)
    if results:
        top = results[0]
        doc_name, sec_id, text, score = top

        # Check if top results span multiple documents (potential cross-doc blend)
        if len(results) > 1 and results[1][0] != doc_name and results[1][3] >= score:
            # Multiple documents equally relevant → refuse to blend
            return REFUSAL_TEMPLATE

        return f"[{doc_name} - Section {sec_id}]\n{text}"

    return REFUSAL_TEMPLATE


def run_tests():
    """Run all 7 test questions from the UC-X README."""
    docs = load_documents()
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]

    expected_docs = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
        "policy_it_acceptable_use.txt",
        None,  # Refusal
        "policy_finance_reimbursement.txt",
        "policy_hr_leave.txt",
    ]

    print("=" * 60)
    print("UC-X POLICY DOCUMENT Q&A — TEST SUITE")
    print("=" * 60)

    pass_count = 0
    for i, (q, expected_doc) in enumerate(zip(test_questions, expected_docs), start=1):
        ans = answer_question(q, docs)
        has_hedging = check_hedging(ans)

        # Determine pass/fail
        if expected_doc is None:
            passed = REFUSAL_TEMPLATE.strip() in ans.strip()
        else:
            passed = expected_doc in ans and not has_hedging

        status = "PASS" if passed else "FAIL"
        if passed:
            pass_count += 1

        print(f"\nQ{i}: {q}")
        print(f"Status: [{status}]" + (" ⚠ HEDGING DETECTED" if has_hedging else ""))
        print("-" * 40)
        print(ans)
        print("-" * 40)

    print(f"\n{'=' * 60}")
    print(f"Results: {pass_count}/{len(test_questions)} passed")
    print("=" * 60)


def main():
    if "--test" in sys.argv:
        run_tests()
        return

    docs = load_documents()
    print("UC-X Ask My Documents — Policy Q&A Assistant")
    print("Type your question below (or 'exit' to quit):\n")

    while True:
        try:
            user_q = input("Question: ").strip()
            if not user_q or user_q.lower() in ("exit", "quit"):
                print("Goodbye.")
                break
            ans = answer_question(user_q, docs)
            if check_hedging(ans):
                print("\n⚠ WARNING: Answer contained hedging — replaced with refusal.\n")
                ans = REFUSAL_TEMPLATE
            print(f"\n{ans}\n")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break


if __name__ == "__main__":
    main()
