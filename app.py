"""
UC-X: Ask My Documents
======================
A single-source policy Q&A tool using Claude API.

Usage:
    python app.py

Requires:
    pip install anthropic

Policy documents must be present at:
    data/policy-documents/policy_hr_leave.txt
    data/policy-documents/policy_it_acceptable_use.txt
    data/policy-documents/policy_finance_reimbursement.txt

CRAFT Commit History:
    UC-X Fix missing attribution: no citation in output → added source doc name to every response
    UC-X Fix cross-doc blending: top-N retrieval blended sources → restricted to top-1 document only
    UC-X Fix hallucination: LLM answered from general knowledge → added "answer only from context" hard rule
    UC-X Fix silent failure: empty answer returned blank → added explicit not-found message handler
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Skill 1: Document Loader
# ---------------------------------------------------------------------------

def load_policy_documents(directory: str) -> dict:
    """
    Load all .txt files from the given directory.
    Returns a dict: { filename: full_text }
    """
    if not os.path.isdir(directory):
        print(f"[ERROR] Policy documents directory not found: {directory}")
        print("       Please ensure data/policy-documents/ exists relative to this script.")
        sys.exit(1)

    documents = {}
    for fname in os.listdir(directory):
        if fname.endswith(".txt"):
            fpath = os.path.join(directory, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                documents[fname] = content
            else:
                print(f"[WARN] Skipping empty file: {fname}")

    if not documents:
        print("[ERROR] No policy documents found. Check data/policy-documents/")
        sys.exit(1)

    print(f"[INFO] Loaded {len(documents)} policy document(s): {list(documents.keys())}")
    return documents


# ---------------------------------------------------------------------------
# Skill 2: Section Retriever  (single-source enforcement)
# ---------------------------------------------------------------------------

def retrieve_relevant_section(question: str, documents: dict) -> tuple:
    """
    Score each document by keyword overlap with the question.
    Return (doc_name, best_paragraph) from the TOP-1 document only.
    If no match found, return ("NOT_FOUND", "").
    """
    # Tokenise question into lowercase keywords (remove stop words)
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "what", "how", "when", "where", "who", "which", "why", "i",
        "my", "me", "we", "our", "you", "your", "he", "she", "they", "their",
        "it", "its", "in", "on", "at", "to", "for", "of", "and", "or", "but",
        "if", "as", "by", "from", "with", "about", "into", "than", "that",
        "this", "these", "those", "am", "not", "no", "so", "up", "out"
    }
    keywords = [
        w.lower().strip("?.,!;:'\"")
        for w in question.split()
        if w.lower().strip("?.,!;:'\"") not in stop_words and len(w) > 2
    ]

    if not keywords:
        return ("NOT_FOUND", "")

    # Score each document
    doc_scores = {}
    for doc_name, text in documents.items():
        text_lower = text.lower()
        score = sum(text_lower.count(kw) for kw in keywords)
        doc_scores[doc_name] = score

    best_doc = max(doc_scores, key=doc_scores.get)

    # If best doc scored 0, nothing matched
    if doc_scores[best_doc] == 0:
        return ("NOT_FOUND", "")

    # Extract the best paragraph from the top document
    paragraphs = [p.strip() for p in documents[best_doc].split("\n\n") if p.strip()]
    if not paragraphs:
        # Fall back to line-by-line if no paragraph breaks
        paragraphs = [l.strip() for l in documents[best_doc].split("\n") if l.strip()]

    para_scores = {}
    for i, para in enumerate(paragraphs):
        para_lower = para.lower()
        score = sum(para_lower.count(kw) for kw in keywords)
        para_scores[i] = score

    best_para_idx = max(para_scores, key=para_scores.get)

    # Include surrounding context (±1 paragraph) for richer answer
    start = max(0, best_para_idx - 1)
    end = min(len(paragraphs), best_para_idx + 2)
    section = "\n\n".join(paragraphs[start:end])

    return (best_doc, section)


# ---------------------------------------------------------------------------
# Skill 3: Answer Generator  (Claude API call with hard context-only rule)
# ---------------------------------------------------------------------------

def generate_answer(question: str, context: str, doc_name: str) -> str:
    """
    Call the Claude claude-sonnet-4-20250514 API.
    Strict prompt: answer ONLY from the provided context.
    Returns the answer string.
    """
    try:
        import anthropic
    except ImportError:
        return (
            "[ERROR] The 'anthropic' package is not installed.\n"
            "Please run: pip install anthropic"
        )

    system_prompt = (
        "You are a strict policy document assistant. "
        "Your job is to answer employee questions using ONLY the policy text provided. "
        "Rules you must follow without exception:\n"
        "1. Answer ONLY using the context provided below. Do NOT use general knowledge.\n"
        "2. Do NOT combine information from multiple documents.\n"
        "3. If the answer is not present in the context, say exactly: "
        "'This specific information is not available in the provided document section.'\n"
        "4. Be concise and factual. Do not speculate or infer beyond what is written.\n"
        "5. Never fabricate policy details, numbers, or clauses."
    )

    user_message = (
        f"Policy Document: {doc_name}\n\n"
        f"Relevant Section:\n{context}\n\n"
        f"Employee Question: {question}\n\n"
        "Answer based strictly on the document section above:"
    )

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        answer = response.content[0].text.strip()
        return answer if answer else "No answer generated from the document."

    except Exception as e:
        return f"[ERROR] Claude API call failed: {e}"


# ---------------------------------------------------------------------------
# Skill 4: Response Formatter
# ---------------------------------------------------------------------------

def format_response(answer: str, doc_name: str) -> str:
    """Wrap the answer with clear attribution for terminal display."""
    border = "━" * 60
    return (
        f"\n{border}\n"
        f"Answer:\n{answer}\n\n"
        f"📄 Source: {doc_name}\n"
        f"{border}\n"
    )


# ---------------------------------------------------------------------------
# Skill 5: Not-Found Handler
# ---------------------------------------------------------------------------

def handle_not_found(question: str) -> str:
    """Return a user-friendly message when no document matches the query."""
    border = "━" * 60
    return (
        f"\n{border}\n"
        f"Answer: This question could not be answered from the loaded policy documents.\n"
        f"        Please contact HR / IT / Finance directly for this query.\n\n"
        f"📄 Source: Not found in any loaded document\n"
        f"{border}\n"
    )


# ---------------------------------------------------------------------------
# Main Interactive Loop
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("  UC-X: Ask My Documents — Policy Q&A Tool")
    print("  City: Hyderabad")
    print("=" * 60)

    # Determine the path to policy documents
    # Support running from repo root OR from uc-x/ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate_paths = [
        os.path.join(script_dir, "..", "data", "policy-documents"),   # from uc-x/
        os.path.join(script_dir, "data", "policy-documents"),          # from repo root
        os.path.join(os.getcwd(), "data", "policy-documents"),          # cwd
    ]
    doc_dir = None
    for path in candidate_paths:
        if os.path.isdir(path):
            doc_dir = os.path.abspath(path)
            break

    if doc_dir is None:
        print(
            "\n[ERROR] Cannot locate data/policy-documents/\n"
            "Please run this script from the repo root:\n"
            "    python uc-x/app.py\n"
        )
        sys.exit(1)

    # Load documents once at startup
    documents = load_policy_documents(doc_dir)

    print("\nAvailable documents:")
    for i, name in enumerate(documents.keys(), 1):
        print(f"  {i}. {name}")

    print("\nType your policy question and press Enter.")
    print("Type 'quit' or 'exit' to stop.\n")

    # Sample questions to guide the user
    sample_questions = [
        "How many casual leaves am I entitled to per year?",
        "What is the policy for reimbursement of travel expenses?",
        "Can I use personal devices on the company network?",
        "What is the notice period for resignation?",
        "How do I claim medical reimbursement?",
    ]
    print("Sample questions you can try:")
    for q in sample_questions:
        print(f"  → {q}")
    print()

    # Interactive Q&A loop
    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Session ended.")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("[INFO] Goodbye!")
            break

        print(f"\n[INFO] Searching policy documents for: '{question}'")

        # Retrieve the best matching section (single-source)
        doc_name, section = retrieve_relevant_section(question, documents)

        if doc_name == "NOT_FOUND":
            print(handle_not_found(question))
        else:
            print(f"[INFO] Best match found in: {doc_name}")
            answer = generate_answer(question, section, doc_name)
            print(format_response(answer, doc_name))


# ---------------------------------------------------------------------------
# Batch / Demo Mode (non-interactive, for CI/testing)
# ---------------------------------------------------------------------------

def run_demo(documents: dict):
    """Run a fixed set of demo questions and print results. Used for testing."""
    demo_questions = [
        "How many casual leaves are employees entitled to?",
        "What expenses are covered under travel reimbursement?",
        "Is personal use of company internet allowed?",
        "What is the medical insurance coverage limit?",
        "Can I bring my own laptop to work?",
    ]

    print("\n" + "=" * 60)
    print("  DEMO MODE — Running 5 sample questions")
    print("=" * 60)

    for q in demo_questions:
        print(f"\nQ: {q}")
        doc_name, section = retrieve_relevant_section(q, documents)
        if doc_name == "NOT_FOUND":
            print(handle_not_found(q))
        else:
            answer = generate_answer(q, section, doc_name)
            print(format_response(answer, doc_name))


if __name__ == "__main__":
    # If --demo flag passed, run demo mode instead of interactive
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidate_paths = [
            os.path.join(script_dir, "..", "data", "policy-documents"),
            os.path.join(script_dir, "data", "policy-documents"),
            os.path.join(os.getcwd(), "data", "policy-documents"),
        ]
        doc_dir = None
        for path in candidate_paths:
            if os.path.isdir(path):
                doc_dir = os.path.abspath(path)
                break
        if doc_dir:
            docs = load_policy_documents(doc_dir)
            run_demo(docs)
        else:
            print("[ERROR] Cannot locate data/policy-documents/")
            sys.exit(1)
    else:
        main()
