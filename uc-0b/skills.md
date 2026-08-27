skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and returns its contents as structured numbered sections for downstream clause-preserving summarization.
    input:
      type: file_path
      format: Plain-text path to a .txt policy document, expected here as ../data/policy-documents/policy_hr_leave.txt
    output:
      type: structured_sections
      format: YAML object or list keyed by numbered clause identifiers, preserving original clause text and section order
    error_handling: >
      If the file path is missing, unreadable, not a .txt file, or the document cannot be reliably segmented into numbered clauses, return a structured error and do not infer missing content. If numbering is ambiguous or incomplete, flag the ambiguous clauses explicitly. Do not add outside context, and do not rewrite or summarize the source during retrieval.
  - name: summarize_policy
    description: Takes structured numbered policy sections and produces a compliant summary with clause references that preserves obligations and conditions without adding new meaning.
    input:
      type: structured_sections
      format: Structured numbered clauses from the source policy, including clause identifiers and original text
    output:
      type: summary_document
      format: Plain-text summary with clause references, covering every numbered clause and preserving binding meaning; if needed, verbatim quotations are included and flagged
    error_handling: >
      If input sections are missing, malformed, out of order, or incomplete, return a structured error rather than guessing. If any clause would be omitted, softened, broadened, or lose a condition during summarization, block the rewrite for that clause and quote it verbatim with a flag. Detect and reject scope bleed, including unsupported phrases such as "as is standard practice", "typically in government organisations", or "employees are generally expected to". Preserve all multi-condition requirements exactly, including clause 5.2 requiring approval from both Department Head and HR Director.