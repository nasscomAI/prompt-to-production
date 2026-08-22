\# skills.md — UC-0B



skills:

&#x20; - name: retrieve\_policy

&#x20;   description: >

&#x20;     Loads the supplied plain-text policy file and extracts its numbered

&#x20;     clauses while preserving the original clause text.

&#x20;   input: >

&#x20;     Path to a UTF-8 or compatible plain-text policy document.

&#x20;   output: >

&#x20;     Structured collection of numbered policy clauses containing clause

&#x20;     number and original text.

&#x20;   error\_handling: >

&#x20;     If the file is missing, unreadable, or numbered clauses cannot be

&#x20;     identified reliably, return an explicit error and do not invent

&#x20;     missing policy content.



&#x20; - name: summarize\_policy

&#x20;   description: >

&#x20;     Produces a clause-referenced summary that preserves every obligation,

&#x20;     condition, threshold, deadline, exception, and approval requirement.

&#x20;   input: >

&#x20;     Structured numbered policy clauses produced by retrieve\_policy.

&#x20;   output: >

&#x20;     Plain-text policy summary containing every source clause number and

&#x20;     a faithful summary of its requirements.

&#x20;   error\_handling: >

&#x20;     If summarization would risk changing a clause's meaning, preserve the

&#x20;     clause text verbatim and flag it for review. Never fill gaps using

&#x20;     outside knowledge or assumptions.

