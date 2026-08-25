skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return its content as structured numbered sections.
    input: A file path to a .txt policy document.
    output: A list of dictionaries, each with keys: section_number, heading, content.
    error_handling: If the file does not exist or cannot be read, return an error message and do not proceed to summarization.

  - name: summarize_policy
    description: Take structured numbered sections and produce a compliant summary that preserves every clause and condition.
    input: A list of structured sections (output of retrieve_policy), plus a reference to the enforcement rules from agents.md.
    output: A plain-text summary string that includes every numbered clause, preserves multi-condition obligations, avoids external content, and flags verbatim quotes with [VERBATIM].
    error_handling: If input sections are empty or malformed, return an error message. If a clause cannot be summarised without meaning loss, quote it verbatim and flag with [VERBATIM] rather than omitting or altering it.
