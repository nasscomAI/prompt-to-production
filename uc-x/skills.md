    output: Answer text with `source: <filename>` and `section: <n.m>` or the
      refusal template exactly as specified.
    processing: Tokenise question, search for presence of tokens in section
      texts; if exactly one section across all docs matches, return it; if
      multiple docs match and the answer would need combining, return refusal.
    validation: For each returned factual snippet include a citation with the
      originating filename and section number.
