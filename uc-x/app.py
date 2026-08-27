"""
UC-X — Policy Q&A Assistant

Answers questions exclusively from three CMC policy documents.
Never blends sources. Returns refusal template when not covered.
"""

import argparse
import os
import re
import sys

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Each entry: (keyword_lower, doc_name, section_num)
# Keywords map question terms to the SINGLE most relevant section.
KEYWORD_INDEX = [
    # HR — LEAVE
    ("carry forward annual leave", "policy_hr_leave.txt", "2.6"),
    ("carry forward unused annual leave", "policy_hr_leave.txt", "2.6"),
    ("carry forward leave", "policy_hr_leave.txt", "2.6"),
    ("unused annual leave", "policy_hr_leave.txt", "2.6"),
    ("annual leave carry forward", "policy_hr_leave.txt", "2.6"),
    ("forfeited annual leave", "policy_hr_leave.txt", "2.6"),
    ("leave encashment", "policy_hr_leave.txt", "7.1"),
    ("encash leave", "policy_hr_leave.txt", "7.1"),
    ("sick leave medical certificate", "policy_hr_leave.txt", "3.2"),
    ("sick leave", "policy_hr_leave.txt", "3.1"),
    ("maternity leave", "policy_hr_leave.txt", "4.1"),
    ("paternity leave", "policy_hr_leave.txt", "4.3"),
    ("leave without pay", "policy_hr_leave.txt", "5.2"),
    ("lwp approval", "policy_hr_leave.txt", "5.2"),
    ("approves leave without pay", "policy_hr_leave.txt", "5.2"),
    ("approve leave without pay", "policy_hr_leave.txt", "5.2"),
    ("approve lwp", "policy_hr_leave.txt", "5.2"),
    ("public holiday", "policy_hr_leave.txt", "6.1"),
    ("compensatory off", "policy_hr_leave.txt", "6.2"),
    ("leave grievance", "policy_hr_leave.txt", "8.1"),
    ("leave application", "policy_hr_leave.txt", "2.3"),
    ("approval manager leave", "policy_hr_leave.txt", "2.4"),
    ("loss of pay", "policy_hr_leave.txt", "2.5"),
    ("lop", "policy_hr_leave.txt", "2.5"),

    # IT — ACCEPTABLE USE
    ("install software", "policy_it_acceptable_use.txt", "2.3"),
    ("install slack", "policy_it_acceptable_use.txt", "2.3"),
    ("install on work laptop", "policy_it_acceptable_use.txt", "2.3"),
    ("install on corporate device", "policy_it_acceptable_use.txt", "2.3"),
    ("software installation approval", "policy_it_acceptable_use.txt", "2.3"),
    ("software installation", "policy_it_acceptable_use.txt", "2.3"),
    ("personal device access email", "policy_it_acceptable_use.txt", "3.1"),
    ("personal device", "policy_it_acceptable_use.txt", "3.1"),
    ("personal phone work files", "policy_it_acceptable_use.txt", "3.1"),
    ("personal phone access work", "policy_it_acceptable_use.txt", "3.1"),
    ("personal phone email", "policy_it_acceptable_use.txt", "3.1"),
    ("byod", "policy_it_acceptable_use.txt", "3.1"),
    ("bring your own device", "policy_it_acceptable_use.txt", "3.1"),
    ("share password", "policy_it_acceptable_use.txt", "4.1"),
    ("password change", "policy_it_acceptable_use.txt", "4.3"),
    ("multi factor authentication", "policy_it_acceptable_use.txt", "4.4"),
    ("mfa", "policy_it_acceptable_use.txt", "4.4"),
    ("corporate device personal use", "policy_it_acceptable_use.txt", "2.2"),
    ("corporate device", "policy_it_acceptable_use.txt", "2.1"),
    ("acceptable use policy", "policy_it_acceptable_use.txt", "1.1"),
    ("cmc email personal account", "policy_it_acceptable_use.txt", "5.2"),
    ("endpoint security", "policy_it_acceptable_use.txt", "2.6"),
    ("lost device report", "policy_it_acceptable_use.txt", "3.5"),
    ("confidential data", "policy_it_acceptable_use.txt", "5.1"),
    ("internet monitoring", "policy_it_acceptable_use.txt", "6.1"),
    ("policy violation", "policy_it_acceptable_use.txt", "7.1"),
    ("password sharing", "policy_it_acceptable_use.txt", "4.1"),
    ("remote access mfa", "policy_it_acceptable_use.txt", "4.4"),
    ("guest wifi", "policy_it_acceptable_use.txt", "3.3"),
    ("cmc guest wifi", "policy_it_acceptable_use.txt", "3.3"),
    ("device pin lock", "policy_it_acceptable_use.txt", "3.4"),
    ("biometric lock", "policy_it_acceptable_use.txt", "3.4"),
    ("cmc email personal device", "policy_it_acceptable_use.txt", "3.1"),
    ("access cmc email", "policy_it_acceptable_use.txt", "3.1"),
    ("employee self service portal", "policy_it_acceptable_use.txt", "3.1"),

    # FINANCE — REIMBURSEMENT
    ("home office equipment allowance", "policy_finance_reimbursement.txt", "3.1"),
    ("home office allowance", "policy_finance_reimbursement.txt", "3.1"),
    ("equipment allowance", "policy_finance_reimbursement.txt", "3.1"),
    ("wfh allowance", "policy_finance_reimbursement.txt", "3.1"),
    ("work from home allowance", "policy_finance_reimbursement.txt", "3.1"),
    ("work from home equipment", "policy_finance_reimbursement.txt", "3.1"),
    ("da and meal receipts", "policy_finance_reimbursement.txt", "2.6"),
    ("daily allowance and meal", "policy_finance_reimbursement.txt", "2.6"),
    ("claim da and meal", "policy_finance_reimbursement.txt", "2.6"),
    ("da meal same day", "policy_finance_reimbursement.txt", "2.6"),
    ("daily allowance meal", "policy_finance_reimbursement.txt", "2.6"),
    ("meal receipt da", "policy_finance_reimbursement.txt", "2.6"),
    ("travel reimbursement", "policy_finance_reimbursement.txt", "2.1"),
    ("outstation travel", "policy_finance_reimbursement.txt", "2.2"),
    ("air travel reimbursement", "policy_finance_reimbursement.txt", "2.3"),
    ("hotel reimbursement", "policy_finance_reimbursement.txt", "2.4"),
    ("daily allowance", "policy_finance_reimbursement.txt", "2.5"),
    ("da outstation", "policy_finance_reimbursement.txt", "2.5"),
    ("local travel reimbursement", "policy_finance_reimbursement.txt", "2.1"),
    ("training reimbursement", "policy_finance_reimbursement.txt", "4.1"),
    ("course fee reimbursement", "policy_finance_reimbursement.txt", "4.2"),
    ("exam fee reimbursement", "policy_finance_reimbursement.txt", "4.3"),
    ("mobile phone reimbursement", "policy_finance_reimbursement.txt", "5.1"),
    ("internet reimbursement", "policy_finance_reimbursement.txt", "5.2"),
    ("mobile reimbursement grade", "policy_finance_reimbursement.txt", "5.1"),
    ("internet reimbursement wfh", "policy_finance_reimbursement.txt", "5.2"),
    ("claim submission", "policy_finance_reimbursement.txt", "6.1"),
    ("reimbursement claim form", "policy_finance_reimbursement.txt", "6.1"),
    ("original receipt", "policy_finance_reimbursement.txt", "6.2"),
    ("claim processing time", "policy_finance_reimbursement.txt", "6.3"),
    ("disputed claim", "policy_finance_reimbursement.txt", "6.4"),
    ("personal expense reimbursable", "policy_finance_reimbursement.txt", "1.2"),
    ("30 day claim", "policy_finance_reimbursement.txt", "1.3"),
    ("claim within 30 days", "policy_finance_reimbursement.txt", "1.3"),
]

def _stop_words():
    return {
        "the", "and", "for", "are", "not", "but", "all", "can", "any",
        "has", "had", "may", "per", "use", "must", "each", "from",
        "this", "that", "with", "their", "will", "than", "been",
        "also", "more", "into", "other", "such", "only", "who", "what",
        "when", "where", "why", "how", "which", "whose", "have", "does",
        "used", "using", "being", "done", "about", "after", "before",
        "between", "through", "during", "without", "within", "upon",
        "under", "over", "above", "below", "whether", "while", "although",
        "because", "therefore", "however", "otherwise", "regarding",
    }


def _parse_sections(content):
    sections = {}
    current_section = ""
    current_sub = ""
    current_lines = []

    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped or re.match(r'^═+$', stripped):
            continue

        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            if current_sub and current_lines:
                sections[current_sub] = current_section + "\n" + '\n'.join(current_lines)
            current_section = stripped
            current_sub = ""
            current_lines = []
            continue

        m = re.match(r'^(\d+\.\d+)\s+(.*)', stripped)
        if m:
            if current_sub and current_lines:
                sections[current_sub] = current_section + "\n" + '\n'.join(current_lines)
            current_sub = m.group(1)
            current_lines = [stripped]
            continue

        if current_sub:
            current_lines.append(stripped)

    if current_sub and current_lines:
        sections[current_sub] = current_section + "\n" + '\n'.join(current_lines)

    return sections


def _section_text(doc_name, section_num, doc_index):
    return doc_index[doc_name].get(section_num, "")


def retrieve_documents():
    index = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(POLICY_DIR, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Policy file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        sections = _parse_sections(content)
        index[filename] = sections
    return index


# Build secondary word-level index
def _build_word_index():
    word_index = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(POLICY_DIR, filename)
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        sections = _parse_sections(content)
        for sec_num, sec_text in sections.items():
            words = set(w.lower() for w in re.findall(r'[a-z]\w{2,}', sec_text.lower())
                        if w.lower() not in _stop_words() and len(w) >= 4)
            for w in words:
                word_index.setdefault(w, []).append((filename, sec_num))
    return word_index

WORD_INDEX = _build_word_index()


def answer_question(question, doc_index):
    if not question.strip():
        return REFUSAL_TEMPLATE

    q = question.lower().strip()

    # Step 1: Try PRIMARY keyword index (phrase matching)
    matches = {}  # (doc_name, section_num) -> count
    for keyword, doc_name, section_num in KEYWORD_INDEX:
        if keyword in q:
            key = (doc_name, section_num)
            matches[key] = matches.get(key, 0) + 1

    if matches:
        best_key = max(matches, key=matches.get)
        best_doc, best_sec = best_key
        text = _section_text(best_doc, best_sec, doc_index)
        if text:
            return text + "\n\nSource: " + best_doc + ", Section " + best_sec

    # Step 2: Try SECONDARY word-level fallback
    q_words = set()
    for w in re.findall(r'[a-z]\w{2,}', q):
        if w not in _stop_words() and len(w) >= 4:
            q_words.add(w)

    if not q_words:
        return REFUSAL_TEMPLATE

    word_matches = {}  # (doc_name, section_num) -> count
    doc_match_count = {}  # doc_name -> set of matched section nums

    for qw in q_words:
        for doc_name, section_num in WORD_INDEX.get(qw, []):
            key = (doc_name, section_num)
            word_matches[key] = word_matches.get(key, 0) + 1
            doc_match_count.setdefault(doc_name, set()).add(section_num)

    if not word_matches:
        return REFUSAL_TEMPLATE

    # Score at the DOCUMENT level first
    doc_scores = {}
    for doc_name, sec_set in doc_match_count.items():
        doc_scores[doc_name] = len(sec_set)
    ranked_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    best_doc, best_doc_score = ranked_docs[0]

    # Check for cross-document blend
    for doc, score in ranked_docs[1:]:
        if score > 0 and score >= best_doc_score * 0.7:
            return REFUSAL_TEMPLATE

    # Within best doc, pick the section with most question-word hits
    best_sec = None
    best_sec_score = 0
    for (doc_name, section_num), count in word_matches.items():
        if doc_name == best_doc:
            if count > best_sec_score:
                best_sec_score = count
                best_sec = section_num

    if best_sec is None:
        return REFUSAL_TEMPLATE

    text = _section_text(best_doc, best_sec, doc_index)
    return text + "\n\nSource: " + best_doc + ", Section " + best_sec


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Q&A Assistant")
    parser.add_argument("--question", "-q", help="Answer a single question and exit")
    args = parser.parse_args()

    try:
        doc_index = retrieve_documents()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.question:
        print(answer_question(args.question, doc_index))
        return

    print("UC-X Policy Q&A Assistant")
    print("Type your questions or 'quit' to exit.\n")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in ("quit", "exit", ""):
            break
        print()
        print(answer_question(question, doc_index))
        print()


if __name__ == "__main__":
    main()
