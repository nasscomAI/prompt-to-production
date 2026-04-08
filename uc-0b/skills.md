# skills.md

skills:
  - name: retrieve_policy
    description: "Load a .txt file and parse it into structured dictionary of numbered sections (e.g., '2.3', '5.2')."
    input: "Absolute file path (string)."
    output: "Dictionary/Object: { 'clause_number': 'clause_text' }."
    error_handling: "Fail if file is empty, missing clause numbering, or unreadable."

  - name: summarize_policy
    description: "Convert structured sections into a summary that preserves all conditions and adds clause references."
    input: "Structured policy sections (Dictionary)."
    output: "Markdown summary formatted with clause numbers in brackets."
    error_handling: "If a clause is non-summarizable without loss of meaning, quote it verbatim and flag it."
