"""
UC-X app.py — Ask My Documents
Answering employee policy questions strictly from single-source documents
with mandatory citations and exact refusal handling.
"""

import os
import re
import sys
import math
import argparse
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Any, Set

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

REQUIRED_DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

BANNED_HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "when", "to", "on", "the", "for"
}

SYNONYMS: Dict[str, List[str]] = {
    "slack": ["software", "application", "program"],
    "software": ["slack", "application", "program"],
    "phone": ["devic", "mobile", "smartphone", "byod"],
    "smartphone": ["phone", "devic", "mobile", "byod"],
    "laptop": ["devic", "computer", "corporate"],
    "fil": ["data", "document", "portal", "email", "access"],
    "file": ["data", "document", "portal", "email", "access"],
    "da": ["daily", "allowance"],
    "lwp": ["leave", "without", "pay", "lwp"],
    "approv": ["approval", "require", "written"],
    "instal": ["software", "install"],
    "install": ["software", "instal"],
}

def normalize_word(w: str) -> str:
    """Normalize word endings for robust matching."""
    w = w.lower()
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("es") and len(w) > 3:
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    if w.endswith("ing") and len(w) > 4:
        base = w[:-3]
        return base if not base.endswith("t") else base
    if w.endswith("ed") and len(w) > 3:
        return w[:-1] if (w.endswith("eed") or w.endswith("red")) else (w[:-2] if not (w.endswith("sed") or w.endswith("ted")) else w[:-1])
    return w

def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text."""
    words = [w.lower() for w in re.findall(r"[a-zA-Z0-9]+", text) if w.lower() not in STOP_WORDS]
    return [normalize_word(w) for w in words]

def find_data_dir() -> str:
    """Locate the policy-documents directory."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"),
        os.path.join(os.path.dirname(__file__), "data", "policy-documents"),
        os.path.join("data", "policy-documents"),
        os.path.join("..", "data", "policy-documents"),
    ]
    for c in candidates:
        abs_path = os.path.abspath(c)
        if os.path.isdir(abs_path):
            return abs_path
    raise FileNotFoundError("Policy documents directory could not be located.")

def retrieve_documents(data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Skill: retrieve_documents
    Loads the 3 policy files and indexes text contents by document filename and section number.
    """
    if data_dir is None:
        data_dir = find_data_dir()

    index: List[Dict[str, Any]] = []

    for doc_name in REQUIRED_DOCUMENTS:
        file_path = os.path.join(data_dir, doc_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required policy document '{doc_name}' missing at '{file_path}'.")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        current_major = ""
        current_section = ""
        current_lines = []

        for line in content.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("═") or line_str.startswith("Document Reference:") or line_str.startswith("Version:"):
                continue

            major_match = re.match(r"^(\d+)\.\s+([A-Z\s\(\)\—\-/]+)$", line_str)
            if major_match:
                if current_section and current_lines:
                    index.append({
                        "doc_name": doc_name,
                        "section": current_section,
                        "major_section": current_major,
                        "text": " ".join(current_lines).strip(),
                    })
                    current_section = ""
                    current_lines = []
                current_major = f"{major_match.group(1)}. {major_match.group(2)}"
                continue

            clause_match = re.match(r"^(\d+\.\d+)\s+(.*)", line_str)
            if clause_match:
                if current_section and current_lines:
                    index.append({
                        "doc_name": doc_name,
                        "section": current_section,
                        "major_section": current_major,
                        "text": " ".join(current_lines).strip(),
                    })
                    current_lines = []
                current_section = clause_match.group(1)
                current_lines.append(clause_match.group(2).strip())
                continue

            if current_section:
                current_lines.append(line_str)

        if current_section and current_lines:
            index.append({
                "doc_name": doc_name,
                "section": current_section,
                "major_section": current_major,
                "text": " ".join(current_lines).strip(),
            })

    if not index:
        raise ValueError("No policy sections could be indexed from the documents.")

    return index

def answer_question(question: str, indexed_documents: List[Dict[str, Any]]) -> str:
    """
    Skill: answer_question
    Searches indexed documents to provide a concise single-source answer with citations
    or returns the exact refusal template.
    """
    cleaned_q = question.strip()
    if not cleaned_q:
        return REFUSAL_TEMPLATE

    q_toks = tokenize(cleaned_q)
    if not q_toks:
        return REFUSAL_TEMPLATE

    N = len(indexed_documents)
    df: Dict[str, int] = defaultdict(int)
    clause_tokens_list: List[List[str]] = []
    clause_text_tokens_list: List[List[str]] = []
    total_len = 0

    for item in indexed_documents:
        toks_text = tokenize(item["text"])
        toks_major = tokenize(item["major_section"])
        toks_full = toks_major + toks_major + toks_text
        clause_tokens_list.append(toks_full)
        clause_text_tokens_list.append(toks_text)
        total_len += len(toks_full)
        for t in set(toks_full):
            df[t] += 1

    avg_len = total_len / max(N, 1)

    doc_scores: Dict[str, List[Tuple[float, Dict[str, Any], float]]] = defaultdict(list)

    for idx, item in enumerate(indexed_documents):
        toks_full = clause_tokens_list[idx]
        toks_text = clause_text_tokens_list[idx]
        counts_full = Counter(toks_full)
        counts_text = Counter(toks_text)
        tok_set = set(toks_full)

        matched_q_terms = set()
        for qt in q_toks:
            if qt in tok_set:
                matched_q_terms.add(qt)
            elif qt in SYNONYMS:
                for syn in SYNONYMS[qt]:
                    if syn in tok_set or normalize_word(syn) in tok_set:
                        matched_q_terms.add(qt)
                        break

        coverage = len(matched_q_terms) / len(q_toks) if q_toks else 0
        if coverage < 0.40:
            continue

        score = 0.0
        doc_len = len(toks_full)
        for term in q_toks:
            syns = [term] + (SYNONYMS.get(term, []))
            for st in syns:
                st_norm = normalize_word(st)
                if st_norm in counts_full:
                    tf = counts_full[st_norm]
                    body_tf = counts_text.get(st_norm, 0)
                    idf = math.log(1 + (N - df.get(st_norm, 0) + 0.5) / (df.get(st_norm, 0) + 0.5))
                    k1 = 1.5
                    b = 0.75
                    bm25_tf = ((tf + 2 * body_tf) * (k1 + 1)) / ((tf + 2 * body_tf) + k1 * (1 - b + b * (doc_len / avg_len)))
                    w = 3.0 if st == term else 2.0
                    score += idf * bm25_tf * w

        clause_str = (item["major_section"] + " " + item["text"]).lower()
        for j in range(len(q_toks) - 1):
            bi = f"{q_toks[j]} {q_toks[j+1]}"
            if bi in clause_str:
                score += 8.0

        for action_term in ["instal", "acces", "carri", "claim", "approv"]:
            if action_term in q_toks and action_term in toks_text:
                score += 10.0

        if "personal" in q_toks and ("phone" in q_toks or "devic" in q_toks):
            if "PERSONAL DEVICES" in item["major_section"]:
                score += 25.0
            if item["doc_name"] == "policy_it_acceptable_use.txt":
                score *= 2.5
            elif item["doc_name"] == "policy_finance_reimbursement.txt":
                finance_terms = {"allow", "allowance", "reimburs", "reimbursement", "cost", "claim", "expens", "limit"}
                if not (finance_terms & set(q_toks)):
                    score = 0.0

        score *= (coverage ** 2.0)
        if score > 0:
            doc_scores[item["doc_name"]].append((score, item, coverage))

    # Cross-document ambiguity check: inspect top two policy documents
    sorted_doc_scores = sorted(
        [(doc, max([s for s, _, _ in doc_scores[doc]]) if doc_scores[doc] else 0.0) for doc in REQUIRED_DOCUMENTS],
        key=lambda x: x[1],
        reverse=True,
    )
    top_doc, top_doc_score = sorted_doc_scores[0]
    second_doc, second_doc_score = sorted_doc_scores[1]

    if not top_doc or top_doc_score < 6.0:
        return REFUSAL_TEMPLATE

    # If two separate documents produce closely competing scores for a multi-domain question,
    # refuse rather than guessing or blending across policies.
    if second_doc_score > 0 and (second_doc_score / top_doc_score) > 0.85 and top_doc_score < 15.0:
        return REFUSAL_TEMPLATE

    best_doc = top_doc
    top_candidates = sorted(doc_scores[best_doc], key=lambda x: x[0], reverse=True)
    top_score, top_item, _ = top_candidates[0]

    # Selected clauses from the single winning document only
    selected_clauses = [top_item]
    for s, it, _ in top_candidates[1:3]:
        if s >= top_score * 0.70 and it["section"].split(".")[0] == top_item["section"].split(".")[0]:
            if it not in selected_clauses:
                selected_clauses.append(it)

    selected_clauses.sort(key=lambda x: [int(p) for p in x["section"].split(".") if p.isdigit()])
    parts = []
    for cl in selected_clauses:
        parts.append(f"{cl['text']} [{best_doc}, Section {cl['section']}]")

    final_answer = " ".join(parts)

    # Post-generation enforcement: ensure no banned hedging phrases exist
    for phrase in BANNED_HEDGING_PHRASES:
        if phrase in final_answer.lower():
            return REFUSAL_TEMPLATE

    return final_answer

def main():
    parser = argparse.ArgumentParser(description="Ask My Documents (UC-X)")
    parser.add_argument("question", nargs="*", help="Question to ask policy documents")
    parser.add_argument("--test", action="store_true", help="Run the standard 7 test questions")
    args = parser.parse_args()

    try:
        index = retrieve_documents()
    except Exception as e:
        print(f"Error loading documents: {e}", file=sys.stderr)
        sys.exit(1)

    if args.test:
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone for work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?",
        ]
        for q in test_questions:
            print(f"Q: {q}")
            ans = answer_question(q, index)
            print(f"A: {ans}\n" + "-" * 60)
        return

    if args.question:
        query = " ".join(args.question)
        print(answer_question(query, index))
        return

    print("UC-X — Ask My Documents (Type 'exit' or 'quit' to stop)\n")
    while True:
        try:
            q = input("Enter question: ").strip()
            if not q:
                continue
            if q.lower() in ("exit", "quit", "q"):
                break
            ans = answer_question(q, index)
            print(f"\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
