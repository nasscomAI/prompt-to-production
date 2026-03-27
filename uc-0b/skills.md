skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content parsed into structured, numbered clauses.
    input: File path to the .txt policy document.
    output: A structured text or JSON representation of the clauses by their specific numbers.
    error_handling: Throws an error if the file cannot be read or if it cannot detect clear numbered sections.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant, lossless summary ensuring no clauses or multi-condition obligations are dropped.
    input: The structured output from retrieve_policy and the target output file path.
    output: A written summary string saved to the target text file.
    error_handling: Quotes text verbatim and flags it in the output if summarizing would risk losing condition precision or meaning. If the output path is inaccessible, raise an exception.
