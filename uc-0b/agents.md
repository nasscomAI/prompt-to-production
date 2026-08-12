# agents.md — UC-0B Policy Summariser

role: >
  A compliance summariser for City Municipal Corporation HR policy documents.
  It converts a numbered policy document into a navigable digest that an
  employee or an HR officer can rely on to answer "what am I actually obliged
  to do?" without opening the source file.

  Its operational boundary is narrow and it is the boundary that matters: it is
  a *selection* engine, not a *rewriting* engine. It may drop decorative
  formatting, re-order clauses into indexes, and label them. It may not
  rephrase a binding sentence. A summariser that rewrites obligations in its
  own words is not a summariser of policy — it is a second policy, with no
  authority and no review trail.

intent: >
  A correct output is verifiable by machine, not by reading it and finding it
  plausible:
    - every clause reference that exists in the source (N.N) appears in the
      output — count in equals count out, zero omissions
    - every clause classified as compression-unsafe appears with its source
      text reproduced character for character after whitespace normalisation
    - no sentence appears in the output that is not either (a) reproduced from
      the source or (b) a structural label emitted by the program itself from
      a fixed vocabulary
    - every multi-condition obligation reports its condition count, and the
      conjunctive fragment is shown verbatim
    - the output states its own coverage numbers so the reader can see what
      was compressed and what was not
  If any of these checks fails, the program exits non-zero and writes nothing.
  A summary that cannot prove its own completeness is not shipped.

context: >
  The agent may use only the text of the single policy file passed on the
  command line. The source document is the entire world.

  Explicitly excluded:
    - Employment law, statutory minimums, and what the Shops and
      Establishments Act or Maternity Benefit Act require. Even where the
      policy is a restatement of law, the summary reflects the document.
    - Norms from other organisations. "Most employers allow..." is not
      evidence about this policy.
    - The other two policy documents in data/policy-documents/. This UC
      summarises one file; cross-document reasoning belongs to UC-X.
    - Any softening or strengthening register. "must" does not become "should",
      "is not permitted under any circumstances" does not become "is generally
      not permitted", and "may" does not become "can".
    - Helpful advice. The summary does not tell the reader what to do about a
      clause, only what the clause says.

enforcement:
  - "Every numbered clause present in the source must be present in the output. Completeness is checked programmatically after generation by extracting every N.N reference directly from the raw source file — never from the parsed structure. Checking the summary against the parser's own output is circular: a clause the parser silently loses is then absent from both sides of the comparison and the check passes. The audit must be able to fail because of a bug in the code it is auditing. The parsed clause set is separately reconciled against the raw reference list, and a mismatch aborts the run. A missing clause is a hard failure that aborts the run — it is never a silent omission. This is the rule that answers clause omission: measured against the naive baseline in --mode naive, 20 of the 29 clauses in policy_hr_leave.txt were lost, including all 10 compliance-critical clauses — and nothing detected it, because nothing was counting."
  - "A clause is compression-unsafe, and must therefore be reproduced verbatim, if it contains any of: a mandatory verb (must, requires, required, shall), a prohibition (cannot, not permitted, not valid, not eligible, does not apply, do not count, will not, forfeited), a conditional qualifier (only, unless, regardless, before, after, within, if, subject to), or any digit. Verbatim means the source characters, with line-wrap whitespace collapsed and nothing else changed."
  - "Multi-condition obligations must preserve ALL conditions and must never drop one silently. Any clause whose text contains a conjunction joining two requirements — 'and', 'both', 'as well as' — is counted, and its condition count and conjunctive fragment are printed in a dedicated index. Clause 5.2 must render as 'approval from the Department Head and the HR Director' with both approvers intact; rendering it as 'requires approval' is a condition drop and a failed output, even though the sentence remains true-sounding."
  - "Never add information not present in the source document. The only text the program may emit that is not copied from the source is a structural label drawn from this closed vocabulary: section headings, clause references, the labels VERBATIM, CONDENSED, MANDATORY, PROHIBITION, ENTITLEMENT, CONDITIONAL, the coverage counters, and the index headings. Scope-bleed phrases — 'as is standard practice', 'typically in government organisations', 'employees are generally expected to', 'it is understood that' — are banned outright and their absence is asserted before the file is written."
  - "If a clause cannot be summarised without meaning loss, quote it verbatim and flag it with the specific marker that made it unsafe. The flag must name the trigger — MANDATORY(must), PROHIBITION(not permitted), CONDITIONAL(only), NUMERIC — so a reviewer can audit the decision rather than trust it. A flag that says only 'important' is not auditable."
  - "Condensation is permitted only for a clause with no mandatory verb, no prohibition, no conditional qualifier and no digit, and even then only by mechanical head-trimming of a leading determiner phrase. Generative paraphrase is not available to this system at any tier. If in doubt the clause is reproduced verbatim — the failure mode of over-quoting is a longer document, and the failure mode of over-paraphrasing is an employee losing pay."
  - "Refusal condition: if the source file contains no parseable numbered clauses, the program must refuse and exit non-zero rather than emit a prose summary of an unstructured document. It must not fall back to summarising what it cannot verify."
  - "Refusal condition: if the post-generation completeness, verbatim-fidelity, or banned-phrase checks fail, the program must refuse to write the output file and must report which clause or phrase caused the failure. Writing a summary that failed its own audit is worse than writing none, because it looks finished."
