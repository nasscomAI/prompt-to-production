# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy document from a text file and parses its contents into structured, numbered sections.
    input: "String: relative or absolute path to the .txt policy document (e.g., '../data/policy-documents/policy_hr_leave.txt')."
    output: "JSON Object: key-value pairs mapping section or clause numbers (as string keys) to their corresponding raw text content (as string values)."
    error_handling: "Raises a FileNotFoundError if the file does not exist, or a ValueError if the document is empty or does not contain identifiable numbered sections."

  - name: summarize_policy
    description: Summarizes structured policy sections into a compliant text summary with explicit clause references, preserving all core obligations and conditions.
    input: "JSON Object: key-value pairs representing structured, numbered policy sections and their corresponding text."
    output: "String: a compliant, structured text summary referencing each of the 10 target clauses with their obligations intact."
    error_handling: "Raises a ValidationError if any target clause is omitted, if multi-condition obligations drop conditions, or if external scope bleed is detected. If a clause cannot be summarized without loss of meaning, it is quoted verbatim and flagged."
