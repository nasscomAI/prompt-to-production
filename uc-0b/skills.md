# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a policy document (.txt file) and returns its content structured as numbered sections.
    input: File path (string) to a policy document (e.g., policy_hr_leave.txt).
    output: Dictionary or structured object containing: document title, numbered clauses (2.3, 2.4, 2.5, etc.), and their raw text content.
    error_handling: If file is not found, return error message. If file is empty or malformed, flag it and refuse to proceed. Only process plain text files.

  - name: summarize_policy
    description: Extracts all numbered clauses from a structured policy document and produces a legally compliant summary with all conditions and obligations preserved.
    input: Structured policy data (from retrieve_policy) containing numbered clauses and their full text.
    output: Plain text summary containing all 10 core clauses with: clause number, core obligation, binding verb, and complete conditions. Format: "Clause X.X: [Binding Verb] [Complete Obligation with all conditions]". Flag any clauses quoted verbatim as [QUOTED].
    error_handling: If any of the 10 core clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is missing, refuse to finalize and return error. If a clause contains multi-part conditions, preserve all parts or quote verbatim. Never paraphrase high-stakes legal obligations.
