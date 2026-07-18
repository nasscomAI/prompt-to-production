"""
UC-X — Ask My Documents
Interactive policy Q&A agent. Answers from 3 CMC policy documents only.
Strategy: LLM-first (Groq or Gemini) with keyword-search fallback.
"""
import os
import re

# ---------------------------------------------------------------------------
# Policy document paths
# ---------------------------------------------------------------------------

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = {
    "policy_hr_leave.txt": "HR-POL-001 (Employee Leave Policy)",
    "policy_it_acceptable_use.txt": "IT-POL-003 (IT Acceptable Use Policy)",
    "policy_finance_reimbursement.txt": "FIN-POL-007 (Expense Reimbursement Policy)",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

# ---------------------------------------------------------------------------
# System prompt (derived from agents.md enforcement rules)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a policy question-answering agent for the City Municipal Corporation (CMC).
You answer employee questions using ONLY the policy documents provided below.

RULES — you must follow every one:
1. SINGLE-SOURCE ONLY: Never combine claims from two different documents into a single answer. Each answer must come from one document only.
2. NO HEDGING: Never use phrases like "while not explicitly covered", "typically", "generally understood", "it is common practice", "it is likely that". These are PROHIBITED.
3. REFUSAL: If the question is not covered in any document, respond with EXACTLY this template:
   "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the relevant team for guidance."
4. CITE SOURCES: Every factual claim must include the document name and section number. Format: [Document: section]. Example: [IT-POL-003: 3.1].
5. PRESERVE CONDITIONS: Multi-condition rules must retain ALL conditions. Never drop approvers, time limits, or exceptions.
6. NO EXTERNAL KNOWLEDGE: Do not add any information not present in the documents.

POLICY DOCUMENTS:
"""

# ---------------------------------------------------------------------------
# retrieve_documents — loads and indexes all policy files
# ---------------------------------------------------------------------------

def retrieve_documents() -> dict:
    """Load all 3 policy files. Returns dict mapping filename to content."""
    documents = {}
    for filename, label in POLICY_FILES.items():
        filepath = os.path.join(POLICY_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                documents[filename] = {
                    "label": label,
                    "content": f.read(),
                }
        except FileNotFoundError:
            print(f"  Warning: {filename} not found at {filepath}")
    return documents


# ---------------------------------------------------------------------------
# LLM client initialization
# ---------------------------------------------------------------------------

def _get_llm_client():
    """Try to initialize an LLM client. Priority: Groq > Gemini."""
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            return Groq(api_key=api_key), "groq"
    except ImportError:
        pass

    try:
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            return genai.Client(api_key=api_key), "gemini"
    except ImportError:
        pass

    return None, None


# ---------------------------------------------------------------------------
# answer_question — LLM-based
# ---------------------------------------------------------------------------

def answer_question_llm(question: str, documents: dict, client, provider: str) -> str:
    """Answer a question using LLM with policy documents as context."""
    # Build full context with all documents
    context = SYSTEM_PROMPT
    for filename, doc in documents.items():
        context += f"\n--- {filename} ({doc['label']}) ---\n{doc['content']}\n"

    try:
        if provider == "groq":
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": question},
                ],
                temperature=0,
            )
            return response.choices[0].message.content.strip()
        else:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                config={"system_instruction": context},
                contents=question,
            )
            return response.text.strip()
    except Exception as e:
        print(f"  LLM error: {e}")
        return None


# ---------------------------------------------------------------------------
# answer_question — keyword-search fallback
# ---------------------------------------------------------------------------

def answer_question_fallback(question: str, documents: dict) -> str:
    """Keyword-based search fallback when LLM is unavailable."""
    q_lower = question.lower()
    matches = []

    for filename, doc in documents.items():
        content = doc["content"]
        lines = content.splitlines()

        current_section = None
        current_text = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("═"):
                continue

            clause_match = re.match(r"^(\d+\.\d+)\s+(.*)", stripped)
            if clause_match:
                # Save previous section
                if current_section and current_text:
                    full_text = " ".join(current_text).lower()
                    # Check if question keywords appear in this section
                    q_words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3]
                    hit_count = sum(1 for w in q_words if w in full_text)
                    if hit_count >= 2:
                        matches.append({
                            "file": filename,
                            "label": doc["label"],
                            "section": current_section,
                            "text": " ".join(current_text),
                            "hits": hit_count,
                        })

                current_section = clause_match.group(1)
                current_text = [clause_match.group(2)]
            elif current_section and stripped:
                current_text.append(stripped)

        # Save last section
        if current_section and current_text:
            full_text = " ".join(current_text).lower()
            q_words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3]
            hit_count = sum(1 for w in q_words if w in full_text)
            if hit_count >= 2:
                matches.append({
                    "file": filename,
                    "label": doc["label"],
                    "section": current_section,
                    "text": " ".join(current_text),
                    "hits": hit_count,
                })

    if not matches:
        return REFUSAL_TEMPLATE

    # Sort by hit count, take top matches from a single document only
    matches.sort(key=lambda m: m["hits"], reverse=True)
    best_doc = matches[0]["file"]
    doc_matches = [m for m in matches if m["file"] == best_doc][:3]

    answer_parts = [f"Based on {doc_matches[0]['label']}:\n"]
    for m in doc_matches:
        answer_parts.append(f"  [{m['label'].split(' ')[0]}: {m['section']}] {m['text']}")

    return "\n".join(answer_parts)


# ---------------------------------------------------------------------------
# Main — interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A Agent (CMC)")
    print("=" * 60)

    # Load documents
    print("\nLoading policy documents...")
    documents = retrieve_documents()
    print(f"Loaded {len(documents)} documents:")
    for filename, doc in documents.items():
        print(f"  - {filename} ({doc['label']})")

    # Initialize LLM
    client, provider = _get_llm_client()
    if client:
        print(f"\nUsing {provider.upper()} (LLM) for answering.")
    else:
        print("\nNo LLM available. Using keyword-search fallback.")
        print("Tip: set GROQ_API_KEY (or GEMINI_API_KEY) for better answers.")

    print("\nType your question (or 'quit' to exit):\n")

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        # Answer the question
        answer = None
        if client:
            answer = answer_question_llm(question, documents, client, provider)

        if not answer:
            if client:
                print("  (LLM failed, using fallback)")
            answer = answer_question_fallback(question, documents)

        print(f"\nA: {answer}\n")


if __name__ == "__main__":
    main()
