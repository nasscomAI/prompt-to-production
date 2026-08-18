skills:

&#x20; - name: retrieve\_policy

&#x20;   description: Loads the supplied HR leave policy and returns its numbered clauses as structured sections.

&#x20;   input: Policy document as a .txt file.

&#x20;   output: Structured list of numbered policy clauses with their clause references and text.

&#x20;   error\_handling: If the file is missing or unreadable, report the error; do not invent or infer missing clauses.



&#x20; - name: summarize\_policy

&#x20;   description: Produces a concise policy summary while preserving every required clause, obligation, condition, approval, deadline, limit, and prohibition.

&#x20;   input: Structured numbered policy clauses.

&#x20;   output: Summary containing all required clause references and their original meaning.

&#x20;   error\_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it; never guess, weaken, or add information.



