# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Reads the raw .txt policy file and breaks it down into structured numbered sections for the summarizer.
    input: File path to a plain-text policy document.
    output: A list of structured dictionaries, each containing the section title, clause numbers, and the raw text for that clause.
    error_handling: If the file cannot be read or parsed into sections, throw an error indicating the file format is invalid.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant, comprehensive summary retaining all obligations.
    input: A list of structured clause dictionaries.
    output: A single string containing the generated summary, with references to clause numbers and preserving all multi-condition obligations.
    error_handling: If any clause is missing from the output, or if conditions are dropped during generation, the summary must be regenerated or the clause quoted verbatim.
