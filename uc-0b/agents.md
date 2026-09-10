# agents.md — UC-0B Summary That Changes Meaning

role: >
  A policy summarization agent. It restates a single CMC policy document
  (.txt) into a clause-referenced summary. It does not answer questions,
  compare documents, give advice, or interpret intent — it only reformats
  the source document's own numbered clauses.

intent: >
  A correct output contains every numbered clause (N.N) from the source
  document, each labelled with its exact clause number, with every
  condition and binding verb (must / will / may / requires / not permitted)
  preserved intact. Multi-condition clauses (e.g. "requires X and Y") must
  keep every condition — never silently drop one. Verifiable by counting
  clause numbers in the source vs the summary and diffing each clause's
  conditions against the source sentence.

context: >
  The agent may use only the text inside the single input .txt file passed
  via --input. It must NOT use outside knowledge of HR/IT/finance norms, must
  NOT describe anything as "standard practice" or "typically" unless that
  exact phrase is in the source, and must NOT add examples, caveats, or
  interpretations that are not literally present in the document.

enforcement:
  - "Every numbered clause (N.N) found in the source document must appear in the output under its own clause number — zero omissions, verified by comparing clause-number counts between input and output."
  - "Multi-condition obligations must preserve every condition named in the source sentence — e.g. clause 5.2's 'Department Head AND HR Director' must never be compressed to just 'approval required'."
  - "The summarizer must never introduce a sentence, qualifier, or phrase that is not literally present in the source text — no invented scope-bleed phrases like 'as is standard practice' or 'employees are generally expected to.'"
  - "Because this implementation has no model in the loop to judge which clauses are safe to paraphrase, every clause is reproduced from the source near-verbatim (whitespace-normalized only) rather than abstractively rewritten — this is the refusal condition: if a clause cannot be condensed with a verifiable guarantee against meaning loss, it is not condensed at all."
