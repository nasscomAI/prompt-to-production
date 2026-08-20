# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content split into structured
      numbered sections for reliable clause-level processing.
    input: >
      str — file path to a policy document (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: >
      dict or list of sections — each section keyed by clause number (e.g. "2.3") with
      the clause text, plus the document metadata (title, reference, version).
    error_handling: >
      Raises a clear error if the file is missing or unreadable; preserves clause numbers
      exactly as they appear in the source so no clause can be silently dropped.

  - name: summarize_policy
    description: >
      Takes the structured sections and produces a compliant summary with clause
      references, preserving every clause and all conditions.
    input: >
      Structured sections from retrieve_policy — list of {clause_number, text}.
    output: >
      str — summary text where every clause appears, every condition is preserved,
      and each entry is linked to its clause number.
    error_handling: >
      If a clause cannot be summarised without losing meaning, quotes the clause
      verbatim and flags it; refuses to add any sentence not traceable to a clause.