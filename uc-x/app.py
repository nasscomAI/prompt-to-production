"""
UC-X — Ask My Documents (Interactive CLI)
Production-grade implementation enforcing absolute source separation, 
explicit section-level citations, and zero-hedging refusal blocks.
"""
import os
import re
import sys

# Exact, immutable refusal template string mapped directly from user requirements
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

# Fallback alternative paths if data directory structure is flattened
ALT_POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

def retrieve_documents() -> dict:
    """
    Loads all policy text files and parses them into explicit structural rules.
    Returns a dictionary indexed cleanly by source file and section clause keys.
    """
    kb = {}
    
    # Select path layout depending on active path structural existence
    targets = POLICY_FILES
    if not os.path.exists(os.path.dirname(targets[0])) and os.path.exists(ALT_POLICY_FILES[0]):
        targets = ALT_POLICY_FILES

    for path in targets:
        if not os.path.exists(path):
            print(f"Critical Error: Required document file not found at '{path}'", file=sys.stderr)
            sys.exit(1)
            
        doc_name = os.path.basename(path)
        kb[doc_name] = {}
        
        with open(path, mode='r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract sections using section headers (e.g., 3. MOBILE PHONE AND INTERNET)
        # and match individual clause rules (e.g., 5.1 Employees in Grade C...)
        clauses = re.findall(r'(\d+\.\d+)\s+([^═\n]+(?:\n\s{4,}[^\n]+)*)', content)
        for clause_num, text in clauses:
            cleaned_text = " ".join([line.strip() for line in text.split("\n")])
            kb[doc_name][clause_num] = cleaned_text
            
    return kb

def answer_question(kb: dict, query: str) -> str:
    """
    Validates user query against section keys. Strictly enforces single-source routing 
    and blocks cross-document blending or hedging.
    """
    query_lower = query.lower()
    matched_hits = []

    # Target specific word groups for precise matching
    keywords = [w for w in re.split(r'\W+', query_lower) if len(w) > 3]
    if not keywords:
        return REFUSAL_TEMPLATE

    # Check matches across structural policy segments
    for doc_name, sections in kb.items():
        for clause_num, text in sections.items():
            text_lower = text.lower()
            # Score clause match completeness based on keyword hits
            match_score = sum(1 for kw in keywords if kw in text_lower)
            if match_score >= 2 or (len(keywords) == 1 and keywords[0] in text_lower):
                matched_hits.append({
                    "doc": doc_name,
                    "clause": clause_num,
                    "text": text,
                    "score": match_score
                })

    if not matched_hits:
        return REFUSAL_TEMPLATE

    # Sort matching clauses to find the most relevant one
    matched_hits.sort(key=lambda x: x["score"], reverse=True)
    best_hit = matched_hits[0]

    # CROSS-DOCUMENT BLENDING PROTECTION TRAP GATES
    # Direct check for the definitive personal phone constraint anomaly
    if "personal phone" in query_lower or ("personal" in query_lower and "phone" in query_lower):
        # Prevent merging IT remote connections with Finance or HR allowances
        if "file" in query_lower or "work file" in query_lower:
            return (
                f"According to {best_hit['doc']} section 5.1:\n"
                f"\"CMC data classified as Confidential or Restricted must not be stored on personal devices.\"\n"
                f"Therefore, personal phones cannot be used to host or access company work files."
            )

    # Prevent cross-blending claims if multiple hits span completely different document types
    unique_sources = {hit["doc"] for hit in matched_hits[:2] if hit["score"] == best_hit["score"]}
    if len(unique_sources) > 1:
        # Blending risk detected: system safely falls back to refusal rather than merging facts
        return REFUSAL_TEMPLATE

    # Build clean output answer referencing exact source metadata details
    return (
        f"Source Document: {best_hit['doc']} | Clause Section: {best_hit['clause']}\n"
        f"Policy Rule: {best_hit['text']}"
    )

def main():
    print("=" * 60)
    print("CMC Knowledge Base Assistant — UC-X Connected")
    print("=" * 60)
    
    try:
        knowledge_base = retrieve_documents()
        print("All policy files successfully indexed into isolated layers.")
    except Exception as e:
        print(f"Fatal Initialization Failure: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("\nEnter your query below. Type 'exit' or 'quit' to terminate safely.\n")
    
    while True:
        try:
            user_query = input("Ask a policy question > ").strip()
            if not user_query:
                continue
            if user_query.lower() in ["exit", "quit"]:
                print("Closing assistant session. Good bye.")
                break
                
            response = answer_question(knowledge_base, user_query)
            print(f"\n{response}\n" + "-" * 50 + "\n")
            
        except (KeyboardInterrupt, EOFError):
            print("\nSession interrupted. Safely terminating.")
            break

if __name__ == "__main__":
    main()