skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content parsed into structured, numbered sections.
    input: File path string pointing to a plain-text policy document (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: Ordered list of numbered sections, each containing the section identifier and its raw text, preserving original clause numbering.
    error_handling: If the file path does not exist or is unreadable, return an error object with the path and reason; do not proceed to summarisation.

  - name: summarize_policy
    description: Takes the structured numbered sections produced by retrieve_policy and produces a compliant summary with explicit clause references.
    input: Ordered list of numbered sections (output of retrieve_policy).
    output: a structured summary with explicit clause references.Plain-text summary where each paragraph or bullet is prefixed with its source clause reference (e.g. "[2.4]"), covering all 10 mapped clauses and preserving every condition of multi-condition obligations.
    error_handling: If any of the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is absent from the input, halt and return a missing-clause error listing the absent clause identifiers.
