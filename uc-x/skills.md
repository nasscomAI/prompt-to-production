skills:
  - name: retrieve_documents
    description: Loads the three required policy .txt files and indexes their content by document name and section number.
    input: file_paths (list of str paths to the policy documents)
    output: A dictionary where keys are document names and values are dicts mapping section numbers to section text.
    error_handling: Refuses to start if any of the three required documents is missing.

  - name: answer_question
    description: Searches the indexed documents for keywords from the question to find the best single-source section explicitly answering the question, and returns the answer with citation. If no clear single-source match exists, returns the exact refusal template.
    input: question (str), indexed_docs (dict)
    output: A string containing the answer with citation, or the refusal template.
    error_handling: Output the exact refusal template if keyword matching yields ambiguous results, multiple contradictory documents, or zero matches. No hedging is allowed.
