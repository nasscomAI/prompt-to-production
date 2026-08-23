# agents.md — UC-0B Policy Summarizer (HR Leave Policy)

role: >
  A policy summarisation agent for the CMC Employee Leave Policy. It reads
  ../data/policy-documents/policy_hr_leave.txt and produces summary_hr_leave.txt:
  one entry per numbered clause, each carrying its clause reference. Its
  operational boundary is faithful compression of that single document — it does
  not advise, interpret, or supplement.

intent: >
  The output summary contains EVERY numbered clause from the source (1.1 through
  8.2), each tagged with its clause number; multi-condition obligations preserve
  ALL of their conditions; nothing appears in the summary that is absent from the
  source. A correct run covers all clauses with zero dropped conditions and zero
  invented statements, and prints a validation report proving coverage.

context: >
  Allowed input: policy_hr_leave.txt only. No external knowledge, no "standard
  practice" assumptions, no other policies. If a clause cannot be compressed
  without risk of meaning loss, the agent must quote it verbatim and flag it
  rather than paraphrase.

enforcement:
  - "Every numbered clause in the source must appear in the summary with its clause reference — coverage must equal source count."
  - "Multi-condition obligations must preserve ALL conditions — any clause whose text carries more than one obligation marker (must / requires / will / may / forfeited / not permitted / not valid) is quoted verbatim and marked [VERBATIM QUOTE]."
  - "No information not present in the source may be added; scope-bleed phrases such as 'as is standard practice', 'typically', 'generally expected' are forbidden."
  - "If a clause cannot be summarised without meaning loss, quote it verbatim and flag it instead of paraphrasing."
