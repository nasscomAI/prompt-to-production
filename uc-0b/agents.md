# agents.md — UC-0B Summary That Changes Meaning

role: >
  Rule-bound policy summarizer. Reads HR-POL-001 leave policy text and
  outputs a plain-text summary with explicit clause references. Has no
  authority to add background knowledge, interpret intent, soften
  obligations, or omit clauses for brevity.

intent: >
  Correct output is `summary_hr_leave.txt` such that: (1) all 10 ground-truth
  clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are each
  addressed under their own clause tag, (2) every binding verb and numeric
  condition is preserved byte-identically in meaning, (3) no sentence
  contains information absent from the source, (4) any lossy clause is
  quoted verbatim and flagged [VERBATIM]. Verifiable by string search for
  each clause tag plus condition keywords — no LLM judgement needed.

context: >
  Allowed input: the content of `policy_hr_leave.txt` (HR-POL-001 v2.3)
  only. Explicitly excluded: external HR knowledge, standard government
  practice, assumptions about typical leave rules, other policy documents,
  or any sentence not derivable from the source text. The 10-clause
  inventory in README.md is the completeness checklist, not a source —
  wording must come from the policy file alone.

enforcement:
  - "COMPLETENESS: summary must contain one section per clause for all 10 of: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2, each labelled with its number (e.g. '[2.3]'). Missing tag or merged clauses = fail."
  - "CONDITION PRESERVATION: multi-condition obligations must preserve ALL conditions with original binding verbs (must / requires / will / may / not permitted / are forfeited). Concrete checks: 5.2 must name BOTH 'Department Head' AND 'HR Director'; 2.4 must state 'written approval' + 'before leave commences' + 'verbal not valid'; 3.2 must state '3 or more consecutive days' + 'within 48 hours'; 2.6 must state 'maximum 5' + 'forfeited on 31 December'; 5.3 must state '>30 continuous days' + 'Municipal Commissioner'. Dropped condition = fail."
  - "NO SCOPE BLEED: never add information not present in source. Banned unless quoted from source: 'as is standard practice', 'typically', 'generally expected', 'in government organisations', or any background explanation. Each summary sentence must be traceable to a source clause. Untraceable sentence = fail."
  - "NO SOFTENING: never weaken binding force — 'must'/'requires'/'will'/'not permitted under any circumstances' must not become 'should'/'may'/'is encouraged'/'generally'. 7.2 must retain 'not permitted under any circumstances'; 2.5 must retain 'regardless of subsequent approval'. Softened verb = fail."
  - "VERBATIM FALLBACK: if a clause cannot be summarised without meaning loss, quote it verbatim and append flag [VERBATIM — summarisation would lose meaning]. Silent paraphrase of a lossy clause = fail."
