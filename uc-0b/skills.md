skills:
  - name: retrieve_policy
    description: Reads a plain text policy document (.txt) from disk and parses the content into structured numbered sections and individual numbered clauses.
    input: file_path (str: path to policy text document, e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: A structured object/dictionary containing document metadata (title, reference, version, effective date) and an ordered list of sections with their section numbers, titles, and individual clause records (clause_number, clause_text).
    error_handling: Raises FileNotFoundError if the file does not exist; raises ValueError if file is empty or unreadable; employs resilient regex parsing to capture all numbered clauses without omitting unstructured paragraphs.

  - name: summarize_policy
    description: Takes structured policy sections and clauses and generates a faithful, clause-by-clause summary preserving all binding obligations, multi-condition requirements, dual-approver rules, and source clause references.
    input: Structured policy sections (list/dict produced by retrieve_policy) and optional output formatting parameters.
    output: A formatted plain text string (written to summary_hr_leave.txt) containing section headings, concise summaries for each numbered clause retaining exact binding verbs, and explicit clause numbers (e.g., Clause 2.3).
    error_handling: Validates output against the clause inventory; if any multi-condition rule (e.g., Clause 5.2 dual approval) or obligation cannot be safely condensed without meaning loss, outputs the exact verbatim clause text annotated with '[VERBATIM_PRESERVED: Clause X.Y]' to prevent compliance failure.
