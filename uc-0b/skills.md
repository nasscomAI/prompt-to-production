skills:

&#x20; - name: retrieve\_policy

&#x20;   description: Loads the HR leave policy from a text file and returns its content as structured numbered sections.

&#x20;   input: A .txt policy file containing numbered policy sections.

&#x20;   output: Structured policy sections with their clause numbers and content.

&#x20;   error\_handling: If the file is missing, unreadable, or does not contain usable policy content, report the error and do not guess or create missing information.



&#x20; - name: summarize\_policy

&#x20;   description: Produces an accurate summary of the structured policy while preserving all clause requirements and conditions.

&#x20;   input: Structured numbered policy sections from retrieve\_policy.

&#x20;   output: A concise policy summary with references to the original clause numbers.

&#x20;   error\_handling: If the input is incomplete, ambiguous, or a clause cannot be summarized without changing its meaning, flag the issue and quote the original clause instead of guessing.

