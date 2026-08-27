# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them securely by document name and section number.
    input: List of document file paths (strings).
    output: Indexed dictionary mapping document names and section numbers to the explicit text.
    error_handling: Return error if any of the three documents fails to load or parse cleanly.

  - name: answer_question
    description: Searches the indexed documents and returns a clean, single-source answer with immediate citation OR returns the definitive refusal template.
    input: Extracted queries from user (string) and the indexed dictionary.
    output: The compliant single-source string answer or exact Refusal Template (string).
    error_handling: Output explicitly the Refusal Template if search encounters contradictory documents or if evidence is missing.
