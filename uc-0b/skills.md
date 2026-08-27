skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered sections for precise analysis.
    input: Path to the .txt policy document.
    output: A collection of clauses, each with a Clause ID and its associated text.
    error_handling: Raise an error if the file is missing or contains no recognizable numbered clauses.

  - name: summarize_policy
    description: Converts structured clauses into a high-fidelity summary adhering to strict condition preservation rules. The skill must process the collection sequentially to guarantee zero omitted clauses.
    input: Collection of structured clauses.
    output: A text summary where every clause is accounted for, conditions are preserved without scope bleed (no added qualifiers), and unsummarizable parts are quoted.
    error_handling: If a multi-condition clause cannot be summarized without dropping a condition or altering its strict meaning, the skill must default to verbatim quotation and append a [NEEDS_MANUAL_REVIEW] flag.
