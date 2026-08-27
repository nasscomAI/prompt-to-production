# skills.md — UC-X Policy Document Assistant Skills

skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy files (HR, IT, Finance) and partitions them into 
      indexed sections by document name and clause number for accurate retrieval.
    input: None (uses hardcoded paths to the 3 policy files).
    output: A dictionary mapping (Document Name, Section ID) to clause text.
    error_handling: >
      If any file is missing from ../data/policy-documents/, the system raises 
      a FileNotFoundError and exits.

  - name: answer_question
    description: >
      Searches the indexed policy repository for the most relevant single-source
      clause and returns it with mandatory citations.
    input: Question (string) from the interactive CLI.
    output: >
      A structured answer string including the core obligation and citation, 
      or the verbatim refusal template.
    error_handling: >
      If no single section provides a high-confidence match (determined by keyword density),
      or if multiple documents contradict each other, the system returns the refusal template.
