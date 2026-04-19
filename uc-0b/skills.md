skills:
  - name: retrieve_policy
    description: Reads a policy text file and returns the document as ordered section headings and numbered clauses.
    input:
      type: file
      format: Plain-text `.txt` policy document path containing numbered clauses such as `2.3` and section headings.
    output:
      type: object
      format: >
        Structured document with document title, ordered section headings, and an
        ordered list of clause objects containing `clause_number`, `section_heading`,
        and `text`.
    error_handling: >
      If the file path is missing, unreadable, or not a text policy document,
      abort with a clear error. If numbered clauses cannot be extracted, abort
      rather than guessing structure. Preserve original clause wording exactly;
      never infer missing text from broken formatting.

  - name: summarize_policy
    description: Produces a clause-preserving summary from the structured policy while retaining clause references and all binding conditions.
    input:
      type: object
      format: >
        Structured policy output from `retrieve_policy`, including ordered clause
        objects with clause numbers and source text.
    output:
      type: file_content
      format: >
        Plain-text summary in source order where every numbered clause appears,
        each line is traceable by clause number, and clauses that risk meaning
        loss are quoted verbatim.
    error_handling: >
      If any numbered clause is missing, duplicated, or structurally ambiguous,
      abort instead of producing an incomplete summary. If a clause contains
      multi-condition obligations, approvals, deadlines, exceptions, or
      forfeiture rules, keep the full requirement intact and use verbatim wording
      when compression would drop meaning. Never add explanatory language,
      standard-practice statements, or content absent from the source.
