skills:



&#x20; - name: retrieve\_policy

&#x20;   description: >

&#x20;     Loads the supplied UTF-8 HR leave policy and returns its numbered

&#x20;     sections as structured source content.

&#x20;   input: >

&#x20;     Path to policy\_hr\_leave.txt.

&#x20;   output: >

&#x20;     Structured numbered policy sections containing clause number and source text.

&#x20;   error\_handling: >

&#x20;     If the file cannot be read or numbered clauses cannot be found, report

&#x20;     the error and do not invent policy content.



&#x20; - name: summarize\_policy

&#x20;   description: >

&#x20;     Produces a concise clause-referenced summary while preserving every

&#x20;     required obligation, condition, threshold, deadline, approver, exception,

&#x20;     and consequence from the source.

&#x20;   input: >

&#x20;     Structured numbered policy sections returned by retrieve\_policy.

&#x20;   output: >

&#x20;     Plain-text summary containing clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2,

&#x20;     3.4, 5.2, 5.3, and 7.2 with their original meaning preserved.

&#x20;   error\_handling: >

&#x20;     If a clause cannot be summarized without meaning loss, quote the relevant

&#x20;     source text and flag it for review. Never omit, weaken, or invent

&#x20;     policy requirements.

