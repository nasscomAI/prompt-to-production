\# skills.md — UC-0B



skills:



&#x20; - name: retrieve\_policy

&#x20;   description: Load the supplied HR leave policy text and identify its numbered clauses and sections.

&#x20;   input: A UTF-8 text policy file containing numbered policy clauses.

&#x20;   output: Structured policy sections containing clause numbers and their original text.

&#x20;   error\_handling: If the file is missing, unreadable, or contains an unparseable clause, report the problem rather than inventing policy content.



&#x20; - name: summarize\_policy

&#x20;   description: Produce a policy summary that preserves every required clause and all of its conditions.

&#x20;   input: Structured numbered policy sections from retrieve\_policy.

&#x20;   output: A plain-text summary containing clause references and faithful summaries of each required clause.

&#x20;   error\_handling: If a clause cannot be summarized without losing meaning, preserve its wording and mark it for review; never omit or invent a condition.

