# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections.
    input: File path (string) to policy document in .txt format with numbered clause structure (e.g., "../data/policy-documents/policy_hr_leave.txt")
    output: Structured data containing numbered sections with clause identifiers (e.g., 2.3, 2.4, 3.2) and their full text content, preserving all formatting and binding language
    error_handling: If file does not exist, return error "Policy file not found at specified path". If file exists but lacks numbered clause structure (no clauses matching pattern X.Y), refuse processing and return "Input file does not contain numbered clause structure required for policy summarization"

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references that preserves all binding obligations and conditions.
    input: Structured numbered sections (dict/object) with clause identifiers as keys and clause text as values, plus list of required clause numbers to verify (e.g., [2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2])
    output: Summary text where each statement includes source clause reference in format "[Clause X.Y]", preserves all binding verbs (must/requires/not permitted), maintains all conditions in multi-part obligations, and flags any verbatim quotes with [VERBATIM: cannot simplify without meaning loss]
    error_handling: If any required clause number is missing from input sections, return error listing missing clauses. If summary generation would require dropping conditions from multi-part obligations, quote the clause verbatim and flag it. If input contains scope bleed phrases ("typically", "generally", "as is standard practice"), reject and return "Summary contains prohibited scope bleed language not present in source document"
