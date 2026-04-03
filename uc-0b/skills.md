# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) to the policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A list or dictionary containing the policy's structured numbered sections (e.g., {"2.3": "...", "2.4": "..."}).
    error_handling: Return an error if the file is missing, empty, or cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured sections, produces a compliant summary with clause references, without modifying obligations or conditions.
    input: Structured sections (dict or list) from `retrieve_policy`.
    output: A string containing the finalized summary, ensuring every clause is referenced.
    error_handling: If any section is excessively ambiguous, output it verbatim with a flagged warning rather than guessing its meaning.
