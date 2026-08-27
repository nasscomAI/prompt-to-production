# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt HR policy file and returns the content chunked into structured numbered sections.
    input: File path of the policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A structured object, list, or dictionary mapping section/clause numbers to verbatim text from the file.
    error_handling: Refuse to proceed and raise an error if the input file does not exist, cannot be read, or lacks any numbered structure.

  - name: summarize_policy
    description: Takes the structured sections from the policy and produces a compliant, completely lossless summary preserving all conditionality and clause references.
    input: The structured sections returned from the retrieve_policy skill.
    output: A formatted text output (saved to e.g., summary_hr_leave.txt) representing the policy summary, ensuring all clauses, obligations, and multi-actor constraints are met.
    error_handling: Return the original text verbatim for any specific clause if it appears too complex or nuanced to safely compress without risking meaning loss.
