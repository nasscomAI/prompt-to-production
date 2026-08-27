skills:
  - name: retrieve_policy
    description: Load the .txt policy file and return its content as structured, numbered sections.
    input: File path to the policy document (String, e.g., '../data/policy-documents/policy_hr_leave.txt').
    output: A structured text or JSON object where keys are clause numbers and values are the exact text of those clauses.
    error_handling: Return a clear error message if the file is not found, cannot be read, or does not contain numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that safely condenses text while referencing every original clause number and preserving all multi-condition obligations.
    input: Structured, numbered policy clauses (output from retrieve_policy).
    output: A compiled summary document (text format) with explicit references to each original clause number, ensuring no conditions are dropped or meanings changed.
    error_handling: Raise a validation error and refuse to output if the drafted summary drops any clause numbers from the input or adds external information not in the structured content.
