\# UC-0B Skills



skills:

&#x20; - name: retrieve\_policy

&#x20;   description: Loads the HR leave policy and returns its content as structured numbered sections.

&#x20;   input: A path to a .txt HR policy document.

&#x20;   output: Structured policy sections containing section numbers and source text.

&#x20;   error\_handling: If the file is missing, unreadable, or not a text policy file, report the error and do not invent policy content.



&#x20; - name: summarize\_policy

&#x20;   description: Produces a clause-complete HR policy summary while preserving every binding obligation and condition.

&#x20;   input: Structured numbered sections returned by retrieve\_policy.

&#x20;   output: A text summary containing the required policy clauses with clause references.

&#x20;   error\_handling: If a clause cannot be summarized without meaning loss, preserve it verbatim and flag it; never guess or add external information.

