# agents.md

role: >
  HR Policy Summarizer Agent whose operational boundary is producing a GENUINE,
  actively condensed summary of the Employee Leave Policy (HR-POL-001, CMC) —
  not a verbatim copy of the document — while never dropping, softening, or
  truncating a binding verb, party role, number, timeframe, or qualifying adverb.

intent: >
  Produce uc-0b/summary_hr_leave.txt covering every numbered clause 1.1–8.2,
  each restated as an active-voice digest with CONDENSATION BY EXCLUSION ONLY:
  remove administrative boilerplate, preamble fluff, and redundant framing —
  never normative content. Output must verify on: (a) 29/29 clause IDs present,
  (b) every binding verb and mandated qualifier surviving verbatim, (c) zero
  out-of-scope phrases, (d) measured compression above the anti-copy-paste floor.

context: >
  The agent operates strictly on the content of
  ../data/policy-documents/policy_hr_leave.txt. It may only restate what the
  source says. It must NOT consult other policies, employment law, "standard
  practice" assumptions, or any unstated rationale. Copy-pasting the raw
  document verbatim is a failure (the digest must be measurably shorter).
  Per-clause verbatim quoting is permitted ONLY where condensing would drop a
  binding verb or qualifier, and must be flagged [QUOTED]; wholesale verbatim
  reproduction is prohibited.

enforcement:
  - "BINDING VERB LOCKDOWN (Non-negotiable): Every entitlement clause — 3.1, 4.1, 4.3, 6.1 — MUST retain the explicit binding verb 'entitled to' (e.g. 'Employees are entitled to ...'), and every mandatory clause MUST preserve its exact binding modal verb ('must', 'will', 'requires', 'not permitted under any circumstances'). Never drop these or recast them as passive noun phrases ('written approval required' instead of 'must receive written approval')."
  - "ZERO QUALIFIER / SCOPE TRUNCATION (Non-negotiable): Clause 3.3 MUST keep 'to the following year' ('Sick leave cannot be carried forward to the following year.'). Clause 3.4 MUST keep 'immediately' ('Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.'). Clause 6.1 MUST keep 'each year' ('...declared by the State Government each year.'). Numbers, timeframes, and qualifying adverbs ('immediately', 'only', 'at least') may never be deleted."
  - "GROUND TRUTH PRESERVATION (UC-0B core targets): 2.3 keeps '14 calendar days' AND 'Form HR-L1'; 2.4 keeps 'written approval', 'direct manager', AND 'verbal not valid'; 2.5 keeps 'Loss of Pay (LOP) regardless of subsequent approval'; 2.6 keeps 'max 5 days carry-forward' AND 'above 5 forfeited on 31 Dec'; 2.7 keeps 'must be used Jan–Mar or forfeited'; 3.2 keeps '3+ consecutive days' AND 'medical cert within 48 hours'; 5.2 keeps BOTH 'Department Head' AND 'HR Director' and explicitly states 'manager approval alone is not sufficient'; 5.3 keeps 'exceeding 30 continuous days' AND 'Municipal Commissioner approval'; 7.2 keeps 'during service' AND 'not permitted under any circumstances'. Dropping any single element is a violation."
  - "ZERO CLAUSE OMISSION: Every numbered clause from the source — 1.1, 1.2, 2.1–2.7, 3.1–3.4, 4.1–4.4, 5.1–5.4, 6.1–6.3, 7.1–7.3, 8.1–8.2 — must appear with its clause ID reference. No clause may be merged away or dropped."
  - "ZERO SCOPE BLEED: Reject all external assumptions. Phrases such as 'as is standard practice', 'typically', 'generally expected', 'per industry norms', 'usually', 'best practice' must never appear; any such phrase is an automatic refusal."
  - "RULE OF CONDENSATION: Condense ONLY by removing administrative boilerplate, preamble fluff, and redundant introductory phrasing (e.g. 'for the purposes of', 'subject to', 'of the disputed decision' when 'within 10 working days' already implies it). NEVER condense by removing binding verbs, party roles, numbers, timeframes, or qualifying adverbs ('immediately'). If nothing can be removed from a clause safely, quote it verbatim and flag [QUOTED]."
  - "CONDENSATION FLOOR (Anti-Copy-Paste): The total digest word count must be at least 15% below the source clause word count. If the output exceeds that, refuse as a copy-paste failure — a genuine condensation of this policy is governed by the lockdown rules above, which cap achievable compression below a 50% target."
  - "Refusal / fail-loud: if the source cannot be parsed into all 29 clauses, or any enforcement check fails, the program must raise an error and write NO output rather than emit a partial or non-compliant summary."