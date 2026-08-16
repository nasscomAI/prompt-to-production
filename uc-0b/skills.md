skills:

&#x20; - name: retrieve\_policy

&#x20;   description: Loads the supplied HR leave policy text and returns its numbered sections for summarization.

&#x20;   input: Path to the policy .txt file.

&#x20;   output: Structured numbered policy sections containing clause references and source text.

&#x20;   error\_handling: If the file does not exist, cannot be read, or contains no usable numbered sections, return an explicit error and do not invent content.



&#x20; - name: summarize\_policy

&#x20;   description: Produces a concise summary of the structured HR leave policy while preserving every required clause and condition.

&#x20;   input: Structured numbered policy sections from retrieve\_policy.

&#x20;   output: A clause-preserving policy summary containing all required clause references and preserving obligations, conditions, approval requirements, deadlines, limits, exceptions, and prohibitions.

&#x20;   error\_handling: If input is missing, incomplete, ambiguous, or a clause cannot be summarized without meaning loss, do not guess; preserve the source wording and flag the affected clause.

