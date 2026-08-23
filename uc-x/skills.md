# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files and indexes them by document name and
      section number, keeping every clause tagged with the file it came from so
      that a later step cannot lose track of provenance.
    input: >
      paths (list[str]) — the three policy .txt files. Section numbering is
      "N. TITLE" for sections and "N.N " for clauses, with indented
      continuation lines.
    output: >
      A dict: {"clauses": [{document, section, section_title, number, text,
      tokens}], "documents": [filenames], "idf": {token: weight}}.
      Every clause carries its document filename — provenance is a property of
      the clause, not of the search result, so it cannot be dropped downstream.
    error_handling: >
      A missing file → FileNotFoundError naming the path; the agent does not
      start with two of three documents, because the refusal template promises
      the user that all three were searched.
      A file that yields zero clauses → ValueError; an unparseable policy is not
      silently indexed as empty, which would make every question about it
      return a confident refusal.
      Tokens shorter than two characters are dropped except for known
      abbreviations (DA, IT, HR) so that "Can I claim DA?" still retrieves.

  - name: answer_question
    description: >
      Searches the indexed clauses and returns either a single-source answer
      with citations or the refusal template. Never returns anything else.
    input: >
      index (dict from retrieve_documents), question (str as typed by the user).
    output: >
      A dict: {"kind": "answer" | "refusal", "document": filename or None,
      "citations": [{document, section, text}], "excluded": [filenames that
      matched but were not used], "coverage": float, "text": the printable
      response}. When kind is "refusal", "text" is the refusal template with
      only the bracketed team slot filled.
    error_handling: >
      Coverage below the confidence floor → refusal template, not a best guess.
      Top two documents within the ambiguity margin → refusal template, because
      no single document decides the question and combining them is forbidden.
      A hedging phrase detected anywhere in the assembled response → the whole
      response is discarded and replaced with the refusal template; a softened
      answer is never printed.
      Quoted text that does not match the indexed clause character-for-character
      → assertion failure rather than a printed paraphrase.
      Empty or whitespace-only question → prompts again; it is not treated as a
      question with no matches, which would produce a misleading refusal.
