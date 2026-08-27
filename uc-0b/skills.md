skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and extracts its content into structured, numbered sections for precise processing.
    input: File path to the policy text document (String format, e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: A structured object mapping clause numbers to their corresponding verbatim text (Dictionary or JSON).
    error_handling: Return an explicit error message if the file cannot be found, read, or if the text format lacks clear numbered sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with explicit clause references, ensuring no multi-condition obligations are dropped.
    input: Structured representation of the numbered policy sections (Dictionary or JSON).
    output: A compliant summary text explicitly referencing clause numbers and preserving all core obligations and conditions (String).
    error_handling: If any clause cannot be summarized without risking meaning loss or softening, quote the clause verbatim and explicitly flag it in the summary output.
