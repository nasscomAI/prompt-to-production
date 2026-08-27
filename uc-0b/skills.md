skills:
  - name: retrieve_policy
    description: Parses a plain text HR policy document and structures it into identifiable, numbered clauses to ensure completeness.
    input: File path to a plaintext policy document (e.g., policy_hr_leave.txt).
    output: A structured map consisting of each extracted numbered clause strictly matched to its verbatim text without omissions.
    error_handling: Notifies the user and halts if the document is unreadable, completely malformed, or unexpectedly lacks any section numbering.

  - name: summarize_policy
    description: Generates a comprehensively accurate summary where every single numbered clause from the input is referenced while perfectly preserving all specific constraints and multi-condition obligations.
    input: Structured policy sections data retrieved by the retrieve_policy skill.
    output: A precise textual summary strictly abiding by the source document constraints, featuring verbatim quotes where necessary to avoid condition dropping or meaning loss.
    error_handling: Immediately refuses execution if instructed to provide opinions or standard market generalizations; strictly quotes verbatim and flags any clause that cannot be accurately summarized without softening its meaning.
