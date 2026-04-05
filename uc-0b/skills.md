# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a raw text policy file and extracts the contents directly into structured, numbered sections.
    input: The file path to the `.txt` policy document.
    output: A structured object (e.g., dictionary) mapping exact clause numbers to their raw text paragraphs.
    error_handling: Halts and raises an error if the file cannot be found, and securely dumps unnumbered/unparsable chunks verbatim rather than silently dropping content.

  - name: summarize_policy
    description: Ingests the structured sections to generate a concise summary that preserves all core obligations and multi-condition rules.
    input: The structured sections returned by the retrieval skill.
    output: A simplified but complete summary text where every original numbered clause is explicitly referenced.
    error_handling: If a specific clause is overly complex and summarizing it equates to risking meaning-loss or omission of critical multi-approver conditions, it simply quotes the clause verbatim and visually flags it.
