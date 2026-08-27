# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured, numbered sections to ensure precise mapping.
    input: Absolute or relative path to a policy .txt file.
    output: A collection of structured sections containing section numbers and their corresponding text.
    error_handling: Returns an empty list and logs an error if the file path is invalid or the document structure is unreadable.

  - name: summarize_policy
    description: Condenses structured policy sections into a compliant summary, preserving every obligation and multi-part condition.
    input: A collection of structured, numbered policy sections.
    output: A bulleted summary string where every point is mapped back to its original clause number.
    error_handling: If a section is too complex to summarize without meaning loss, it quotes the section verbatim and flags it for review.
