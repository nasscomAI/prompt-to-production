# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Load a policy text file and parse it into structured numbered sections with section headers and clause text.
    input: File path to .txt policy document.
    output: Dict with keys: document_name, sections list. Each section contains section_number, section_title, clauses list. Each clause contains clause_number, full_text.
    error_handling: If file not found, raise FileNotFoundError. If file is empty or malformed, log warning and return empty sections list.

  - name: summarize_policy
    description: Generate a summary of a policy document that preserves all numbered clauses and their conditions, with references to source clause numbers.
    input: Structured policy dict from retrieve_policy (document_name, sections, clauses).
    output: Text summary with all numbered clauses preserved, each with clause reference (e.g., "[Clause 2.3]"), full obligation text, and no external additions. If clause requires verbatim quote to preserve meaning, flag it [VERBATIM].
    error_handling: If a clause cannot be extracted clearly, quote it verbatim and flag [VERBATIM]. Never skip a clause. If summary would lose meaning through paraphrasing, default to verbatim + flag.
