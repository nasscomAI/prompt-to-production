"""
UC-X — Ask My Documents
Built using RICE → agents.md → skills.md → CRAFT workflow.

ChromaDB semantic retrieval — no LLM, no API key.
Replaces hand-crafted regex rules with vector similarity search.

Dependencies:
    pip install chromadb

Run:
    python app.py
Interactive CLI — type a question, press Enter. Type 'quit' to exit.
"""
import re
import os

import chromadb

# ---------------------------------------------------------------------------
# Policy file paths
# ---------------------------------------------------------------------------

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

# Cross-document blending guard: refuse if second-best doc appears in >= this
# fraction of the top-N results (count-based, more robust than score ratio).
COUNT_BLEND_THRESHOLD = 0.50

# Minimum similarity for the best-matching section (filters out-of-scope queries)
MIN_SIMILARITY = 0.35

# Number of nearest sections to retrieve per query
N_RESULTS = 10

# Unambiguous keywords that force the ChromaDB search into a single document.
# Used only when the term makes domain attribution certain (e.g. Slack = IT software).
KEYWORD_FORCE_DOC = [
    (r"\b(slack|teams|zoom)\b",              "policy_it_acceptable_use.txt"),
    (r"\b(receipt[s]?|reimburse|expense[s]?)\b", "policy_finance_reimbursement.txt"),
]


# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents() -> chromadb.Collection:
    """
    Parse all 3 CMC policy files into sections and load them into an
    in-memory ChromaDB collection using the default embedding function.

    Output: ChromaDB Collection indexed by (doc_name, section_num)
    """
    client = chromadb.EphemeralClient()
    collection = client.create_collection("policy_docs")

    section_pattern = re.compile(
        r"(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+\s|\n[═]+|\Z)",
        re.DOTALL,
    )

    documents, metadatas, ids = [], [], []
    doc_counts = {}

    for path in POLICY_FILES:
        doc_name = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as f:
                raw = f.read()
        except (FileNotFoundError, IOError) as e:
            raise RuntimeError(
                f"retrieve_documents: cannot read '{path}' — {e}\n"
                "All 3 policy files are required. Do not proceed with partial data."
            ) from e

        count = 0
        seen_ids: dict[str, int] = {}
        for match in section_pattern.finditer(raw):
            section_num = match.group(1).strip()
            text = re.sub(r"\s+", " ", match.group(2)).strip()
            base_id = f"{doc_name}__{section_num}"
            if base_id in seen_ids:
                seen_ids[base_id] += 1
                uid = f"{base_id}__dup{seen_ids[base_id]}"
            else:
                seen_ids[base_id] = 0
                uid = base_id
            documents.append(text)
            metadatas.append({"doc_name": doc_name, "section_num": section_num})
            ids.append(uid)
            count += 1

        doc_counts[doc_name] = count

    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    for doc, count in doc_counts.items():
        print(f"  Loaded {doc} ({count} sections)")

    return collection


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------

def answer_question(question: str, collection: chromadb.Collection) -> str:
    """
    Query ChromaDB for the most relevant policy section and return a cited
    answer, or the exact refusal template if:
      - no section clears the minimum similarity threshold, OR
      - a second document claims >= 50% of the top-N results (cross-doc blending risk).

    Enforcement rules applied:
    1. Never combine claims from two documents — count-based cross-doc guard
    2. Refusal template is a constant string — no hedging possible
    3. Every answer includes (Source: doc, section X.Y)
    4. Not found in any document → exact refusal template
    """
    q_lower = question.lower()

    # Keyword pre-filter: if the question contains an unambiguous domain term,
    # restrict ChromaDB search to that document only.
    force_doc = None
    for pattern, doc in KEYWORD_FORCE_DOC:
        if re.search(pattern, q_lower):
            force_doc = doc
            break

    query_kwargs = dict(
        query_texts=[question],
        n_results=min(N_RESULTS, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    if force_doc:
        query_kwargs["where"] = {"doc_name": force_doc}

    results = collection.query(**query_kwargs)

    if not results["ids"][0]:
        return REFUSAL_TEMPLATE

    # Build per-document stats over the top-N results:
    #   doc_best:  doc_name → (best_similarity, section_num, text)
    #   doc_count: doc_name → number of sections in top-N
    doc_best: dict[str, tuple[float, str, str]] = {}
    doc_count: dict[str, int] = {}
    for dist, meta, text in zip(
        results["distances"][0],
        results["metadatas"][0],
        results["documents"][0],
    ):
        sim = 1.0 / (1.0 + dist)
        doc_name = meta["doc_name"]
        section_num = meta["section_num"]
        doc_count[doc_name] = doc_count.get(doc_name, 0) + 1
        if doc_name not in doc_best or sim > doc_best[doc_name][0]:
            doc_best[doc_name] = (sim, section_num, text)

    # Rank by count descending, then by best similarity as tiebreaker
    ranked = sorted(
        doc_best.keys(),
        key=lambda d: (doc_count[d], doc_best[d][0]),
        reverse=True,
    )

    top_doc = ranked[0]
    top_sim = doc_best[top_doc][0]

    # Minimum similarity guard — question is genuinely out of scope
    if top_sim < MIN_SIMILARITY:
        return REFUSAL_TEMPLATE

    # Count-based cross-document guard (agents.md enforcement rule 1):
    # refuse if the second document holds ≥ 50% as many top-N hits as the first
    if len(ranked) > 1:
        top_cnt    = doc_count[ranked[0]]
        second_cnt = doc_count[ranked[1]]
        if second_cnt >= top_cnt * COUNT_BLEND_THRESHOLD:
            return REFUSAL_TEMPLATE

    best_sim, best_section, best_text = doc_best[top_doc]
    return f"{best_text}\n\n(Source: {top_doc}, section {best_section})"


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("Loading policy documents into ChromaDB...")
    try:
        collection = retrieve_documents()
    except RuntimeError as e:
        print(f"ERROR: {e}")
        raise SystemExit(1)

    print(f"\n  Total sections indexed: {collection.count()}")
    print("\nReady. Type a question and press Enter. Type 'quit' to exit.\n")
    print("=" * 60)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(question, collection)
        print(f"\nAnswer:\n{answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
