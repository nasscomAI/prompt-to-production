skills:
  - name: retrieve_policy
    description: Extracts policy content from a text file and returns it as a collection of structured numbered sections for precise clause tracking.
    input: Absolute file path string.
    output: Structured numbered sections formatted as a mapping of clause IDs to their corresponding text content.
    error_handling: Reports an error if the source document is missing or if the parser cannot unambiguously identify all numbered clauses, preventing clause omission at the source level.

  - name: summarize_policy
    description: Transforms structured policy sections into a summary that preserves all binding conditions and references without introducing external scope bleed.
    input: Object containing structured policy sections and a reference list of required clause numbers.
    output: A text summary with clearly referenced clauses and verbatim quotes for any text where summarization would risk meaning loss.
    error_handling: Rejects the output and triggers a failure flag if any multi-condition obligation is softened, a clause is omitted, or external phrases like "standard practice" are introduced.
