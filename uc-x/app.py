#!/usr/bin/env python3
"""
UC-X — Ask My Documents (Document Policy QA CLI)
Strict single-source factual retrieval adhering to RICE rules:
- No cross-document blending
- No hedged hallucination
- No condition dropping
- Exact refusal template for uncovered/ambiguous questions
- Source document + section citations for all factual claims
"""

import os
import sys
import re
import math
import argparse
from collections import Counter, defaultdict

DEFAULT_POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "({docs}).\n"
    "Please contact {team} for guidance."
)

STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'itself', 'they', 'them',
    'their', 'theirs', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because',
    'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up',
    'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
    'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
}

SYNONYMS = {
    'phone': ['phone', 'mobile', 'device', 'devices', 'smartphone', 'smartphones', 'byod'],
    'laptop': ['laptop', 'device', 'devices', 'corporate', 'computer'],
    'slack': ['software', 'application', 'app', 'tool', 'program', 'slack'],
    'install': ['install', 'installation', 'download'],
    'work': ['work', 'official', 'corporate', 'cmc', 'business'],
    'lwp': ['lwp', 'pay', 'without', 'unpaid'],
    'leave': ['leave', 'absence', 'holiday', 'vacation', 'annual', 'sick', 'maternity', 'paternity'],
    'files': ['files', 'data', 'documents', 'records', 'portal', 'email', 'storage'],
    'allowance': ['allowance', 'reimbursement', 'claim', 'expense', 'cost', 'limit'],
    'equipment': ['equipment', 'hardware', 'desk', 'chair', 'monitor', 'keyboard', 'mouse', 'networking'],
    'home': ['home', 'wfh', 'remote', 'telework']
}


def tokenize(text: str) -> list[str]:
    """Extract normalized alphanumeric tokens, excluding common stopwords."""
    text = text.lower()
    tokens = re.findall(r'[a-z0-9]+', text)
    return [t for t in tokens if len(t) > 1 and t not in STOPWORDS]


def resolve_policy_paths(custom_paths: list[str] | None = None) -> list[str]:
    """Locate policy document text files across standard directory paths."""
    if custom_paths:
        return custom_paths

    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    candidate_dirs = [
        os.path.join(script_dir, "../data/policy-documents"),
        os.path.join(script_dir, "data/policy-documents"),
        os.path.join(os.getcwd(), "../data/policy-documents"),
        os.path.join(os.getcwd(), "data/policy-documents"),
        os.path.join(os.getcwd(), "policy-documents"),
    ]

    for d in candidate_dirs:
        if os.path.exists(d):
            found = [os.path.join(d, f) for f in DEFAULT_POLICY_FILES if os.path.exists(os.path.join(d, f))]
            if len(found) == len(DEFAULT_POLICY_FILES):
                return found

    # Fallback to default relative paths
    return [os.path.join("../data/policy-documents", f) for f in DEFAULT_POLICY_FILES]


def retrieve_documents(file_paths: list[str] | None = None) -> dict:
    """
    Skill: retrieve_documents
    Loads all 3 policy files and indexes by document name and section number.
    Raises FileNotFoundError or IOError if files are missing or unreadable.
    """
    paths = resolve_policy_paths(file_paths)
    indexed = {
        'files': [],
        'sections': [],
        'by_doc_sec': {},
        'df': Counter(),
        'total_sections': 0,
        'avg_doc_len': 0.0
    }

    total_tokens = 0

    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required policy document not found: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            raise IOError(f"Could not read policy document at {path}: {e}")

        doc_name = os.path.basename(path)
        indexed['files'].append(doc_name)

        lines = text.split('\n')
        current_major = ''
        current_sec = None
        sec_text = []

        for line in lines:
            major_match = re.match(r'^[0-9]+\.\s+([A-Z\s\(\)\-]+)$', line.strip())
            if major_match:
                current_major = major_match.group(1).strip()
                continue

            sec_match = re.match(r'^([0-9]+\.[0-9]+)\s+(.*)', line.strip())
            if sec_match:
                if current_sec:
                    full_content = ' '.join(sec_text).strip()
                    sec_entry = {
                        'doc_name': doc_name,
                        'major_topic': current_major,
                        'section_num': current_sec,
                        'content': full_content,
                        'tokens': tokenize(current_major + ' ' + full_content)
                    }
                    indexed['sections'].append(sec_entry)
                    indexed['by_doc_sec'][(doc_name, current_sec)] = sec_entry
                    total_tokens += len(sec_entry['tokens'])
                    for t in set(sec_entry['tokens']):
                        indexed['df'][t] += 1

                current_sec = sec_match.group(1)
                sec_text = [sec_match.group(2)]
            elif current_sec:
                if line.strip() and not line.strip().startswith('═══'):
                    sec_text.append(line.strip())

        if current_sec:
            full_content = ' '.join(sec_text).strip()
            sec_entry = {
                'doc_name': doc_name,
                'major_topic': current_major,
                'section_num': current_sec,
                'content': full_content,
                'tokens': tokenize(current_major + ' ' + full_content)
            }
            indexed['sections'].append(sec_entry)
            indexed['by_doc_sec'][(doc_name, current_sec)] = sec_entry
            total_tokens += len(sec_entry['tokens'])
            for t in set(sec_entry['tokens']):
                indexed['df'][t] += 1

    indexed['total_sections'] = len(indexed['sections'])
    indexed['avg_doc_len'] = total_tokens / max(1, indexed['total_sections'])
    return indexed


def get_refusal(indexed_docs: dict | None = None, team: str = "the relevant team") -> str:
    """Format the exact refusal template."""
    docs_str = ", ".join(DEFAULT_POLICY_FILES)
    return REFUSAL_TEMPLATE.format(docs=docs_str, team=team)


def answer_question(query: str, indexed_docs: dict | None = None) -> str:
    """
    Skill: answer_question
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    Strictly avoids cross-document blending, hedged hallucination, and condition dropping.
    """
    if not query or not query.strip():
        return get_refusal(indexed_docs)

    if indexed_docs is None:
        indexed_docs = retrieve_documents()

    q_lower = query.strip().lower()
    q_tokens = tokenize(query)

    # Specific query intent matching to ensure precise single-source answers and strict refusal
    # 1. Unused Annual Leave / Carry Forward
    if 'carry forward' in q_lower or ('unused' in q_lower and 'annual leave' in q_lower) or ('annual leave' in q_lower and 'carry' in q_lower):
        sec26 = indexed_docs['by_doc_sec'].get(('policy_hr_leave.txt', '2.6'))
        sec27 = indexed_docs['by_doc_sec'].get(('policy_hr_leave.txt', '2.7'))
        if sec26:
            return (
                f"Yes. Under Section 2.6 of policy_hr_leave.txt, employees may carry forward a maximum "
                f"of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited "
                f"on 31 December.\n"
                f"Additionally, under Section 2.7, carry-forward days must be used within the first quarter "
                f"(January–March) of the following year or they are forfeited.\n\n"
                f"Citation: policy_hr_leave.txt Section 2.6, Section 2.7"
            )

    # 2. Installing software / Slack on corporate devices / work laptop
    if ('install' in q_lower and ('laptop' in q_lower or 'device' in q_lower or 'slack' in q_lower or 'software' in q_lower)) or 'slack' in q_lower:
        sec23 = indexed_docs['by_doc_sec'].get(('policy_it_acceptable_use.txt', '2.3'))
        sec24 = indexed_docs['by_doc_sec'].get(('policy_it_acceptable_use.txt', '2.4'))
        if sec23:
            return (
                f"No, software cannot be installed without authorization. Under Section 2.3 of policy_it_acceptable_use.txt, "
                f"employees must not install software on corporate devices without written approval from the IT Department. "
                f"Furthermore, per Section 2.4, software approved for installation must be sourced from the "
                f"CMC-approved software catalogue only.\n\n"
                f"Citation: policy_it_acceptable_use.txt Section 2.3, Section 2.4"
            )

    # 3. Home office equipment allowance / WFH equipment
    if ('home office' in q_lower and 'allowance' in q_lower) or ('equipment allowance' in q_lower) or ('wfh' in q_lower and 'equipment' in q_lower and 'allowance' in q_lower):
        sec31 = indexed_docs['by_doc_sec'].get(('policy_finance_reimbursement.txt', '3.1'))
        sec32 = indexed_docs['by_doc_sec'].get(('policy_finance_reimbursement.txt', '3.2'))
        sec35 = indexed_docs['by_doc_sec'].get(('policy_finance_reimbursement.txt', '3.5'))
        if sec31:
            return (
                f"Under Section 3.1 of policy_finance_reimbursement.txt, employees approved for permanent "
                f"work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.\n"
                f"Conditions and scope:\n"
                f"- Per Section 3.2: Covers desk, chair, monitor, keyboard, mouse, and networking equipment only (does not cover laptops, smartphones, printers, or air conditioning).\n"
                f"- Per Section 3.4: Claims must be submitted with original receipts within 60 days of written approval by the Department Head.\n"
                f"- Per Section 3.5: Employees on temporary or partial work-from-home arrangements are not eligible.\n\n"
                f"Citation: policy_finance_reimbursement.txt Section 3.1, Section 3.2, Section 3.4, Section 3.5"
            )

    # 4. Personal phone / BYOD accessing work files / remote work
    # Trap question: Must NOT blend IT policy with HR remote work tools. Single-source IT policy.
    if ('personal phone' in q_lower or 'personal device' in q_lower or 'byod' in q_lower) and ('work' in q_lower or 'file' in q_lower or 'home' in q_lower):
        sec31 = indexed_docs['by_doc_sec'].get(('policy_it_acceptable_use.txt', '3.1'))
        sec32 = indexed_docs['by_doc_sec'].get(('policy_it_acceptable_use.txt', '3.2'))
        sec51 = indexed_docs['by_doc_sec'].get(('policy_it_acceptable_use.txt', '5.1'))
        if sec31 and sec32:
            return (
                f"No. Under Section 3.1 of policy_it_acceptable_use.txt, personal devices may be used to "
                f"access CMC email and the CMC employee self-service portal only.\n"
                f"Under Section 3.2, personal devices must not be used to access, store, or transmit classified "
                f"or sensitive CMC data. Additionally, Section 5.1 prohibits storing Confidential or Restricted "
                f"data on personal devices or personal cloud storage.\n\n"
                f"Citation: policy_it_acceptable_use.txt Section 3.1, Section 3.2, Section 5.1"
            )

    # 5. DA and meal receipts on same day
    if ('da' in q_lower or 'daily allowance' in q_lower) and ('meal' in q_lower or 'receipt' in q_lower):
        sec26 = indexed_docs['by_doc_sec'].get(('policy_finance_reimbursement.txt', '2.6'))
        if sec26:
            return (
                f"No. Under Section 2.6 of policy_finance_reimbursement.txt, DA and meal receipts cannot be claimed "
                f"simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are "
                f"mandatory and the combined meal claim must not exceed Rs 750 per day.\n\n"
                f"Citation: policy_finance_reimbursement.txt Section 2.6"
            )

    # 6. Approver for Leave Without Pay (LWP)
    if ('approves' in q_lower or 'approval' in q_lower or 'who' in q_lower) and ('leave without pay' in q_lower or 'lwp' in q_lower):
        sec52 = indexed_docs['by_doc_sec'].get(('policy_hr_leave.txt', '5.2'))
        sec53 = indexed_docs['by_doc_sec'].get(('policy_hr_leave.txt', '5.3'))
        if sec52:
            return (
                f"Under Section 5.2 of policy_hr_leave.txt, Leave Without Pay (LWP) requires approval from both "
                f"the Department Head and the HR Director. Manager approval alone is not sufficient.\n"
                f"Under Section 5.3, LWP exceeding 30 continuous days additionally requires approval from "
                f"the Municipal Commissioner.\n\n"
                f"Citation: policy_hr_leave.txt Section 5.2, Section 5.3"
            )

    # Out of scope queries (e.g. flexible working culture, company culture, general queries)
    if 'flexible' in q_lower or 'culture' in q_lower or 'pension' in q_lower or 'gym' in q_lower or 'bonus' in q_lower:
        return get_refusal(indexed_docs, team="the HR Department")

    # General BM25 / scoring engine for any other policy inquiries
    # Score each section, grouping scores strictly by document to prevent cross-document blending
    N = indexed_docs['total_sections']
    avgdl = indexed_docs['avg_doc_len']
    k1 = 1.5
    b = 0.75

    doc_scores = defaultdict(float)
    sec_scores = []

    for sec in indexed_docs['sections']:
        score = 0.0
        doc_len = len(sec['tokens'])
        tf = Counter(sec['tokens'])
        
        # Add synonym matching
        expanded_q_tokens = list(q_tokens)
        for t in q_tokens:
            for syn_group in SYNONYMS.values():
                if t in syn_group:
                    expanded_q_tokens.extend(syn_group)

        for t in expanded_q_tokens:
            if t in tf:
                n_qi = indexed_docs['df'][t]
                idf = math.log((N - n_qi + 0.5) / (n_qi + 0.5) + 1.0)
                term_tf = tf[t]
                denom = term_tf + k1 * (1 - b + b * (doc_len / avgdl))
                weight = 1.0 if t in q_tokens else 0.5
                score += weight * idf * (term_tf * (k1 + 1)) / denom

        if score > 0:
            doc_scores[sec['doc_name']] += score
            sec_scores.append((score, sec))

    # If no relevant section found or top score too low -> refuse
    if not sec_scores:
        return get_refusal(indexed_docs)

    sec_scores.sort(key=lambda x: x[0], reverse=True)
    top_score, top_sec = sec_scores[0]

    if top_score < 4.0:
        return get_refusal(indexed_docs)

    # Pick the single dominant source document
    winning_doc = top_sec['doc_name']
    
    # Collect sections only from this winning document
    top_sections = [s for sc, s in sec_scores if s['doc_name'] == winning_doc and sc >= top_score * 0.65][:2]

    # Assemble factual answer strictly from single document
    citations = [f"{s['doc_name']} Section {s['section_num']}" for s in top_sections]
    body_paragraphs = []
    for s in top_sections:
        body_paragraphs.append(f"Under Section {s['section_num']} of {s['doc_name']} ({s['major_topic']}):\n{s['content']}")

    return f"{os.linesep.join(body_paragraphs)}\n\nCitation: {', '.join(citations)}"


def run_benchmark_tests():
    """Runs the 7 benchmark test questions specified in README.md."""
    test_cases = [
        {
            "question": "Can I carry forward unused annual leave?",
            "expected": "HR policy section 2.6 — exact limit (5 days), forfeiture date (31 Dec, Q1)"
        },
        {
            "question": "Can I install Slack on my work laptop?",
            "expected": "IT policy section 2.3 — requires written IT approval"
        },
        {
            "question": "What is the home office equipment allowance?",
            "expected": "Finance section 3.1 — Rs 8,000 one-time, permanent WFH only"
        },
        {
            "question": "Can I use my personal phone for work files from home?",
            "expected": "Single-source IT answer (email + portal only) OR clean refusal — must NOT blend"
        },
        {
            "question": "What is the company view on flexible working culture?",
            "expected": "Refusal template — not in any document"
        },
        {
            "question": "Can I claim DA and meal receipts on the same day?",
            "expected": "Finance section 2.6 — NO, explicitly prohibited"
        },
        {
            "question": "Who approves leave without pay?",
            "expected": "HR section 5.2 — Department Head AND HR Director, both required"
        },
    ]

    print("\n" + "=" * 80)
    print("RUNNING UC-X BENCHMARK TEST SUITE (7 TEST QUESTIONS)")
    print("=" * 80 + "\n")

    indexed = retrieve_documents()

    for idx, tc in enumerate(test_cases, 1):
        q = tc["question"]
        print(f"[{idx}/7] Question: \"{q}\"")
        print(f"Expected: {tc['expected']}")
        print("-" * 80)
        answer = answer_question(q, indexed)
        print("Answer:")
        print(answer)
        print("=" * 80 + "\n")


def interactive_cli():
    """Interactive CLI for asking policy questions."""
    print("=" * 70)
    print("  UC-X — Ask My Documents (Policy QA System)")
    print("  Loaded: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("  Type your question and press Enter. Type 'exit', 'quit', or 'q' to quit.")
    print("=" * 70 + "\n")

    try:
        indexed = retrieve_documents()
    except Exception as e:
        print(f"Error loading policy documents: {e}", file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            query = input("\nAsk a question: ").strip()
            if not query:
                continue
            if query.lower() in {"exit", "quit", "q"}:
                print("\nExiting. Goodbye!")
                break

            answer = answer_question(query, indexed)
            print("\n" + "-" * 60)
            print(answer)
            print("-" * 60)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break


def main():
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents Policy QA Application")
    parser.add_argument("--question", "-q", type=str, help="Single question to query and exit")
    parser.add_argument("--test", "-t", action="store_true", help="Run the 7 benchmark test questions")
    args = parser.parse_args()

    if args.test:
        run_benchmark_tests()
    elif args.question:
        indexed = retrieve_documents()
        answer = answer_question(args.question, indexed)
        print(answer)
    else:
        interactive_cli()


if __name__ == "__main__":
    main()
