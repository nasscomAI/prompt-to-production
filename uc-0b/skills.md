skills:

&#x20; - name: retrieve\_policy

&#x20;   description: Load the policy text file and return its numbered clauses as structured sections.

&#x20;   input: Path to a UTF-8 text policy file.

&#x20;   output: A list of structured sections containing clause numbers and source text.

&#x20;   error\_handling: If the file cannot be read or a clause cannot be identified, report the error instead of inventing content.



&#x20; - name: summarize\_policy

&#x20;   description: Produce a compliant summary from structured policy sections while preserving clause meaning.

&#x20;   input: A list of numbered policy sections containing clause numbers and source text.

&#x20;   output: A text summary containing every numbered clause reference and all material conditions from the source.

&#x20;   error\_handling: If a clause cannot be summarized without meaning loss, include its source text verbatim and flag it for review.



