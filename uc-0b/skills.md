skills:



&#x20; - name: retrieve\_policy

&#x20;   description: Loads the HR leave policy text file and returns its contents as structured numbered sections.

&#x20;   input: Path to the policy\_hr\_leave.txt policy file.

&#x20;   output: Structured policy sections containing section numbers, clause numbers, and source text.

&#x20;   error\_handling: If the file cannot be read, report the input error; do not invent or reconstruct missing policy content.



&#x20; - name: summarize\_policy

&#x20;   description: Produces a compliant summary from structured policy sections while preserving every numbered clause and all conditions that affect meaning.

&#x20;   input: Structured numbered sections from the HR leave policy.

&#x20;   output: A text summary containing clause references and the requirements, conditions, thresholds, approvers, exceptions, prohibitions, and consequences stated in the source.

&#x20;   error\_handling: If a clause cannot be summarized without meaning loss, quote that clause verbatim and flag it for review; never omit conditions or add unsupported information.

