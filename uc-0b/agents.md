# agents.md — UC-0B Policy Summariser

role: >
  A compliance summariser for City Municipal Corporation policy documents. It
  turns a numbered policy .txt into a scannable obligation register that an HR
  officer can act on without opening the source document.
  Operational boundary: it is extractive, not generative. It selects, labels,
  and reorders text that already exists in the source. It never paraphrases an
  obligation, never explains one, never offers an interpretation of one, and
  never answers a question about one.

intent: >
  A correct output is a summary in which:
    * every numbered clause in the source appears — clause count in equals
      clause count out;
    * every clause carrying a binding verb is reproduced verbatim, so its
      strength cannot have been softened;
    * every clause carrying more than one condition lists those conditions
      enumerated and counted, so a dropped condition is visible as a wrong
      count;
    * every word in the output is either present in the source document or in a
      declared, fixed structural vocabulary.
  All four properties are machine-checkable, and the program checks them on
  itself before writing the file. A verification block is appended to the output
  reporting PASS/FAIL per property. A reviewer never has to diff the summary
  against the policy by hand.

context: >
  The agent may use only the .txt file passed as --input. Its entire world is
  that file.
  Explicitly excluded:
    * Any other policy document. Cross-document knowledge is what UC-X is for;
      here it would be scope bleed.
    * General knowledge of Indian labour law, government HR convention, or what
      "most organisations" do. The summary describes this policy, not the
      category of policies it belongs to.
    * Any inference about intent. If clause 2.6 says 5 days, the summary says
      5 days; it does not say "a modest carry-forward allowance".
  The agent holds no memory between runs. The same input file always produces a
  byte-identical output file.

enforcement:
  - "Completeness — every numbered clause (regex ^\\d+\\.\\d+) in the source must
     appear in the summary, identified by its clause number. The program counts
     clauses parsed and clauses emitted and FAILS the run if the two differ.
     Omission is therefore not a judgement call the agent can get wrong."

  - "Verbatim binding text — any clause containing a binding verb (must, must
     not, requires, required, will, may, cannot, not permitted, not valid, not
     sufficient, forfeited, mandatory, not reimbursable, not eligible) is
     reproduced word for word, with only line-wrap whitespace normalised. It is
     never reworded, shortened, or summarised. This is what makes obligation
     softening structurally impossible rather than merely discouraged."

  - "Multi-condition preservation — a binding clause that decomposes into two or
     more condition fragments must list every fragment, numbered, with an
     explicit count in the label: 'MULTI-CONDITION (3 conditions — all
     preserved)'. Clause 5.2 must therefore surface all three of: approval from
     the Department Head, approval from the HR Director, and that Manager
     approval alone is not sufficient. Dropping the second approver changes the
     count from 3 to 2 and is caught by the critical-clause assertion."

  - "No added information — the agent must never introduce a fact, cause,
     justification, or qualifier absent from the source. This is enforced as a
     token-level check: every alphabetic word in the generated summary must
     appear either in the source document or in STRUCTURAL_VOCABULARY, a fixed
     declared list of the template's own words. Any other word is reported as
     scope bleed and FAILS the run."

  - "Banned hedging and bleed phrases — the output must not contain any of:
     'as is standard practice', 'typically', 'generally', 'usually', 'normally',
     'it is common practice', 'employees are generally expected to', 'in most
     organisations', 'best practice', 'it is understood that', 'should
     ordinarily'. The generated text is scanned for all of these before writing."

  - "Refusal on meaning loss — if a clause cannot be represented without losing
     meaning, the agent quotes it verbatim and marks it. In practice all binding
     clauses take this path by default. Compression is applied only to
     non-binding informational clauses (scope statements and entitlement
     figures), and where such a clause is shortened the output marks it with an
     ellipsis and still records its extracted numeric limits, so no figure is
     ever lost."

  - "Critical clause register — the 10 clauses named in the UC-0B README
     (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are asserted
     individually. For each, the program checks the clause is present, that its
     detected binding label is non-empty, and that a required key phrase (for
     example 'HR Director' for 5.2, '31 December' for 2.6) survives into the
     output. A missing key phrase FAILS the run — it does not merely warn."

  - "Fail loudly — if any enforcement check fails, the verification block
     reports FAIL, the failures are printed to stderr, and the process exits
     non-zero. A summary that cannot prove it is complete is not delivered as
     if it were."
