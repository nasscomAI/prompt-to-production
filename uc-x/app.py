"""
UC-X app.py — Policy Assistant CLI.
Implements RICE + agents.md + skills.md workflow.
"""

import argparse
import pathlib
import re
import sys
from typing import Dict, List, Tuple

# Refusal template (must match exactly as defined)
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents() -> Dict[str, List[Dict[str, str]]]:
    """Load the three policy text files, parse sections, and build an index.
    Returns a dict mapping document name to a list of sections with keys:
        'section' (e.g., '3.1') and 'content' (full text of that section).
    """
    base_path = pathlib.Path(__file__).parent.parent / "data" / "policy-documents"
    doc_files = {
        "policy_hr_leave.txt": base_path / "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": base_path / "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": base_path / "policy_finance_reimbursement.txt",
    }
    index: Dict[str, List[Dict[str, str]]] = {}
    section_regex = re.compile(r"(?i)section\s+([\d\.]+)")
    for name, path in doc_files.items():
        if not path.is_file():
            print(f"Error: missing policy file {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        sections: List[Dict[str, str]] = []
        current_section = None
        current_content = []
        for line in raw.splitlines():
            match = section_regex.search(line)
            if match:
                # store previous section
                if current_section:
                    sections.append({"section": current_section, "content": "\n".join(current_content).strip()})
                current_section = match.group(1).strip()
                current_content = [line]
            else:
                if current_section:
                    current_content.append(line)
        # add last section
        if current_section:
            sections.append({"section": current_section, "content": "\n".join(current_content).strip()})
        index[name] = sections
    return index

def find_answer(query: str, index: Dict[str, List[Dict[str, str]]]) -> str:
    """Search each document for a single‑source answer.
    Returns either the answer with citation or the REFUSAL_TEMPLATE.
    """
    # First attempt exact substring match (case‑insensitive)
    query_lc = query.lower()
    matches: List[Tuple[str, str, str]] = []  # (doc, section, snippet)
    for doc, sections in index.items():
        for sec in sections:
            content_lc = sec["content"].lower()
            if query_lc in content_lc:
                # extract a snippet (first sentence containing the query)
                sentences = re.split(r"(?<=[.!?])\s+", sec["content"])  # keep punctuation
                snippet = None
                for s in sentences:
                    if query_lc in s.lower():
                        snippet = s.strip()
                        break
                if not snippet:
                    snippet = sec["content"].splitlines()[0].strip()
                matches.append((doc, sec["section"], snippet))
    # If exactly one exact match, return it
    if len(matches) == 1:
        doc, section, snippet = matches[0]
        return f"{snippet} ({doc}, section {section})"
    # No exact match or ambiguous – try token‑based fuzzy match
    # Tokenise query (remove punctuation) and filter stopwords
    import string
    stopwords = {"can", "i", "the", "a", "to", "for", "of", "and", "in", "is", "are", "does", "do", "does", "does", "it", "that", "this", "any", "all"}
    tokens = [t for t in query_lc.translate(str.maketrans('', '', string.punctuation)).split() if t and t not in stopwords]
    # If after filtering no tokens remain, fallback to original token list to avoid empty
    if not tokens:
        tokens = [t for t in query_lc.translate(str.maketrans('', '', string.punctuation)).split() if t]
    fuzzy_matches: List[Tuple[str, str, str]] = []
    for doc, sections in index.items():
        for sec in sections:
            content_lc = sec["content"].lower()
            if all(tok in content_lc for tok in tokens):
                # Find a sentence that contains any token
                sentences = re.split(r"(?<=\.|!|\?)\s+", sec["content"])  # keep punctuation
                snippet = None
                for s in sentences:
                    if any(tok in s.lower() for tok in tokens):
                        snippet = s.strip()
                        break
                if not snippet:
                    snippet = sec["content"].splitlines()[0].strip()
                fuzzy_matches.append((doc, sec["section"], snippet))
                break  # take first matching section per doc
    if len(fuzzy_matches) == 1:
        doc, section, snippet = fuzzy_matches[0]
        return f"{snippet} ({doc}, section {section})"
    # If still ambiguous or no matches, refuse
    return REFUSAL_TEMPLATE

def answer_question(query: str, index: Dict[str, List[Dict[str, str]]]) -> str:
    """Public wrapper for CLI usage."""
    query = query.strip()
    if not query:
        return ""
    return find_answer(query, index)

def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X Policy Assistant")
    # No CLI arguments required for now
    args = parser.parse_args()
    index = retrieve_documents()
    print("UC-X Policy Assistant – ask a question (empty line to quit).")
    while True:
        try:
            user_input = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not user_input:
            print("Goodbye!")
            break
        answer = answer_question(user_input, index)
        print("\nAnswer:")
        print(answer)

if __name__ == "__main__":
    main()
