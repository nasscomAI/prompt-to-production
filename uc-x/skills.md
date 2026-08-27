# skills.md
skills:
  - name: retrieve_documents
    description: Parses the three target policy text files and builds an indexed mapping of sections by document and clause number.
    input: None entirely; hardcoded to look for the three required policy .txt files.
    output: A flattened dictionary or search space representing isolated clauses with their respective source filenames.
    error_handling: System halt if any of the three required `.txt` files drop offline.

  - name: answer_question
    description: Rigorously matches user queries to a single specific clause across the documents, refusing matches that span multiple domains or lack explicit cover.
    input: User's typed question string.
    output: A formulated answer string citing the single sourced document and section, or the verbatim refusal template.
    error_handling: If a question matches overlapping policies (e.g. IT and HR conflict), throws the explicit refusal template string immediately without guessing.
