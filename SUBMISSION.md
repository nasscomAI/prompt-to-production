# Vibe Coding Workshop — Submission PR

**Name:** Shoib Ahmad
**City / Group:** Lucknow
**Date:** 12 August 2026
**AI tool(s) used:** Claude Code (Opus 5)

> **Note on input data:** the repo ships city test files for Pune, Hyderabad,
> Kolkata and Ahmedabad only, so UC-0A uses `test_pune.csv` and produces
> `results_pune.csv`. The classifier is city-agnostic and was additionally run
> against all three other city files as a generalisation check.
>
> **Note on method:** all four builds are deterministic Python (stdlib only, no
> model call at runtime). That was a deliberate choice: it makes every
> enforcement rule in `agents.md` an executable, testable check rather than a
> hope, and it means a reviewer can re-run any result and get the same output.

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_[city].csv` without crash
- [x] `results_pune.csv` present in `uc-0a/`
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**

> **False confidence on ambiguity.** My first working build flagged
> `NEEDS_REVIEW` only when two categories tied exactly on keyword count.
> Row `PM-202408` — *"Bus stand flooded. Passengers standing in water. Drain
> blocked."* — matched Flooding on two terms and Drain Blockage on one, so a
> 2:1 lead passed as certainty and the row shipped unflagged. The citizen
> explicitly names a blocked drain as the cause; that is a real
> Flooding/Drain-Blockage judgement call, and my rule had quietly decided it.
> The lesson was that keyword count measures vocabulary overlap, not
> diagnostic confidence.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Refusal condition — when a rival category matches the description on
> comparable evidence (within one keyword hit of the leading category), emit
> the leading category and set flag to NEEDS_REVIEW rather than presenting the
> choice as settled. Comparable, not merely equal: keyword count measures
> vocabulary overlap, not diagnostic certainty, so a 2-to-1 lead is still a
> judgement call a human must confirm. When no category keyword matches at
> all, emit category Other with flag NEEDS_REVIEW. The agent must never express
> confidence it cannot justify from matched words."

**How many rows in your results CSV match the answer key?**

> The answer key has not been released yet, so I cannot report a figure against
> it honestly. What I can report is verified independently of the key:
> 15 rows in / 15 rows out; every `category` value is one of the ten permitted
> strings; every row carries a non-empty `reason` quoting at least one literal
> word from that row's own description; 4 Urgent, 10 Standard, 1 Low,
> 3 flagged `NEEDS_REVIEW` (`PM-202408`, `PM-202420`, `PM-202430`).

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> **Yes** — audited mechanically rather than by eye. I re-scanned
> `test_pune.csv` for the nine README severity keywords and cross-checked every
> hit against the output:
>
> | Row | Trigger | Priority |
> |---|---|---|
> | PM-202402 | "School", "children" | Urgent |
> | PM-202411 | "hazard" | Urgent |
> | PM-202420 | "injury" | Urgent |
> | PM-202446 | "fell" | Urgent |
>
> 4 of 4. The severity check runs before and independently of the category
> check, so a complaint that cannot be categorised at all is still Urgent — I
> verified this with a malformed row whose `complaint_id` was missing and whose
> description mentioned a school: it came out `UNKNOWN_ID / Waste / Urgent /
> NEEDS_REVIEW`.

**Your git commit message for UC-0A:**

> `UC-0A Fix false confidence on ambiguity: exact-tie test missed rival categories with real evidence -> flag NEEDS_REVIEW when a rival scores within one keyword hit`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**

> All three, from a single control run. I implemented the naive strategy as a
> real code path (`--mode naive`, output committed as
> `naive_summary_baseline.txt`) rather than assuming what it would do —
> take the first clause of each section and smooth the language.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> The naive run produced 8 lines for 29 clauses. **All 10 critical clauses were
> missing** — 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3 and 7.2 — because
> every one of them is the second or later clause in its section, and the naive
> strategy only ever reaches the first. Clause 8.1 survived but was weakened:
> source *"grievances **must** be raised"* became *"grievances **should** be
> raised"*.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> **Yes.** The audit reports `clauses in source: 29 / clauses in summary: 29`,
> `missing clauses: none`, `missing critical clauses: none`. Completeness is not
> asserted by me — the run recomputes it from the source on every execution and
> exits non-zero if it fails.
>
> Clause 5.2, the designated trap, is emitted verbatim with both approvers
> intact: *"LWP requires approval from the Department Head and the HR Director.
> Manager approval alone is not sufficient."*

**Did the naive prompt add any information not in the source document (scope bleed)?**

> **Yes** — four phrases, none of which appear anywhere in `policy_hr_leave.txt`:
> "as is standard practice", "generally", "in most cases", and "employees are
> generally expected to". The vocabulary check also caught "should", "expected",
> "follow", "these", "rules" as words the renderer had introduced.
>
> The enforced build scores 0 banned phrases and 0 scope-bleed words. Getting
> there required fixing my own audit twice — it initially reported the
> document's own heading words ("purpose", "scope") as invented, because I had
> built the vocabulary baseline from clause text and omitted section headings.

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission and condition drop: naive summary kept 8 of 29 clauses and lost every multi-approver condition -> made compression conditional on material-token survival, with a self-audit that fails the run`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> To be precise about evidence: I did not run a free-text prompt for this UC. I
> reasoned about what "calculate growth from the data" must produce against a
> 300-row file with no scope argument — a single percentage covering 5 wards
> and 5 categories, computed over whatever rows parse cleanly — and built the
> enforcement rules against exactly that shape of answer.
>
> The point that made the rule concrete: such a number is not wrong
> arithmetically. It is wrong *operationally*, because no ward officer and no
> category owner can act on it. That is why the refusal message names the
> available scope rather than just declining.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> That is the failure the design assumes and forecloses. In my build,
> aggregation is not blocked by a check — it is **absent as a code path**.
> `compute_growth()` takes exactly one ward and one category and has no
> parameter through which it could be asked to span either dimension.
> `--aggregate`, `--ward ALL`, and supplying `--ward` without `--category` are
> each refused with the available scope listed. Verified: **0 rows** in
> `growth_output.csv` lack a single ward+category scope.
>
> Nulls are reported *before* any computation runs, with the verbatim `notes`
> text for each.

**After your fix — does your system refuse all-ward aggregation?**

> **Yes.** Observed output:
>
> ```
> REFUSED: cross-ward or cross-category aggregation is not permitted by this agent
>   A single blended figure across 5 wards and 5 categories belongs to no ward
>   officer and no category owner, so no one can act on it.
>   Available scope — one ward AND one category per series: ...
> ```
>
> `--growth-type` is also refused when omitted, rather than defaulting to MoM:
> MoM and YoY answer different questions and would return different numbers
> from the same rows. And because this dataset is a single calendar year, a YoY
> request returns 12/12 rows as `NOT_COMPUTED_NO_PRIOR_YEAR` stating the
> coverage — it never silently falls back to MoM or reports 0% growth.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> **Yes — and it flags 10 rows, not 5.** That was the subtler find. The row
> *after* a null has a perfectly good `actual_spend`, and computing its MoM
> growth against a null prior would either crash or fabricate a number.
>
> | Period | Ward | Category | Status |
> |---|---|---|---|
> | 2024-03 | Ward 2 – Shivajinagar | Drainage & Flooding | NOT_COMPUTED_NULL_CURRENT |
> | 2024-05 | Ward 5 – Hadapsar | Streetlight Maintenance | NOT_COMPUTED_NULL_CURRENT |
> | 2024-07 | Ward 4 – Warje | Roads & Pothole Repair | NOT_COMPUTED_NULL_CURRENT |
> | 2024-08 | Ward 3 – Kothrud | Parks & Greening | NOT_COMPUTED_NULL_CURRENT |
> | 2024-11 | Ward 1 – Kasba | Waste Management | NOT_COMPUTED_NULL_CURRENT |
>
> plus 5 matching `NOT_COMPUTED_PRIOR_NULL` rows. Example — Ward 4 Warje
> 2024-08 has `actual_spend` 16.0 and is still refused:
> *"prior period 2024-07 has null actual_spend — source note: Audit freeze —
> figures under review."* One null invalidates two rows and both say why.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> **Yes, both exactly.**
>
> | Period | actual_spend | Formula as printed | Result |
> |---|---|---|---|
> | 2024-07 | 19.7 | `(19.7 - 14.8) / 14.8 * 100` | **+33.1%** |
> | 2024-10 | 13.1 | `(13.1 - 20.1) / 20.1 * 100` | **−34.8%** |
>
> Every row carries the substituted arithmetic, not the symbolic form, so a
> reader can verify any figure without opening the source file.

**Your git commit message for UC-0C:**

> `UC-0C Fix silent aggregation and null skipping: a growth figure with no ward/category scope belongs to no one and nulls vanished into the arithmetic -> removed every cross-scope code path and made one null invalidate two rows explicitly`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**

> My first working build answered it — confidently, from the **wrong document**:
>
> ```
> Source: policy_finance_reimbursement.txt (single-source answer)
>   [section 3.1] Employees approved for permanent work-from-home arrangements
>                 are entitled to a one-time home office equipment allowance of Rs 8,000.
>   [section 3.3] The allowance does not cover: personal computers, laptops,
>                 smartphones, printers, or air conditioning equipment.
>   [section 5.2] Employees in Grade B and above are entitled to a monthly
>                 internet reimbursement of Rs 800 ...
> ```
>
> Single-source, fully cited, zero hedging — and about reimbursement, not device
> access. It passed every mechanical check I had written and was still useless.

**Did it blend the IT and HR policies?**

> **No — and that turned out to be the more interesting result.** It did not
> blend; it picked one document and that document was the wrong one. Diagnosing
> why exposed two scoring flaws:
>
> 1. Section headings were scored at full weight, so Finance 5.2 (*internet
>    reimbursement*) inherited the word "PHONE" from its heading "MOBILE PHONE
>    AND INTERNET" and outranked the IT sections that actually govern personal
>    phones.
> 2. There was no stemming, so IT's "mobile **phones** issued by CMC" was
>    unreachable from the question's "personal **phone**".
>
> Both fixes were rules about retrieval, not about the answer — which is the
> part I would not have found without running the question and reading the
> output.

**After your fix — what does your system return for this question?**

> The refusal template, verbatim:
>
> ```
> This question is not covered in the available policy documents
> (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
> Please contact the HR, IT, or Finance department for guidance.
> ```
>
> with an inspectable routing record: `cross-document ambiguity:
> policy_finance_reimbursement.txt 5.75 vs policy_it_acceptable_use.txt 4.91
> (margin 14.6% < 20%) and policy_it_acceptable_use.txt uniquely covers
> "access"`. The system declines *and* names the term that made it ambiguous.

**Did your system use any hedging phrases in any answer?**

> **No.** 18 banned phrases are checked by exact substring match against the
> **assembled final string**, not against the parts it was built from, so the
> check cannot be bypassed by how the answer was constructed. A draft that
> trips it is discarded and replaced with the refusal template. Self-test
> reports `answers containing a hedging phrase: 0`.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> **Yes — 7 of 7** (`python app.py --selftest`, exit code 0):
>
> | # | Question | Result |
> |---|---|---|
> | 1 | Carry forward unused leave | HR 2.6, 2.7 — 5-day cap, forfeited 31 December |
> | 2 | Install Slack on work laptop | IT 2.1, 2.3, 2.6 — written IT approval required |
> | 3 | Home office equipment allowance | FIN 3.1, 3.2, 3.3 — Rs 8,000, permanent WFH only |
> | 4 | Personal phone for work files | **Refusal** — no blend |
> | 5 | View on flexible working culture | **Refusal** — below relevance threshold |
> | 6 | DA and meal receipts same day | FIN 2.5, 2.6 — cannot be claimed simultaneously |
> | 7 | Who approves LWP | HR 5.1, 5.2, 5.3 — Department Head **and** HR Director |
>
> `answers citing more than one document: 0`.
>
> Q7 nearly failed silently. HR 5.2 says *"LWP requires approval"* while the
> question asks *"who approves"* — the one clause naming both approvers shared
> no word with the question and was reachable only through its section heading.
> Once I reduced heading weight to fix Q4, clause 5.2 dropped out of the answer
> entirely. Adding derivational stemming (approve/approves/approval → `approv`)
> and acronym expansion on content words (`leave without pay` → `LWP`) brought
> it back.

**Your git commit message for UC-X:**

> `UC-X Fix cross-document blending: retrieval scored documents on term overlap alone and answered the personal-phone question from the finance policy -> select one document, then refuse when a rival is both close AND covers something the leader cannot`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> **Analyze** — by a distance. Run is mechanical and Fix is the enjoyable part;
> Analyze is where I kept being wrong, because in three of the four UCs the
> output *looked correct*. UC-0A produced a clean 15-row CSV with a plausible
> category on every line. UC-X returned a properly cited single-source answer
> to the personal-phone question. UC-0B reported `RESULT: FAIL` while every
> individual check read clean. None of those failures announce themselves; you
> only find them by picking a specific row and asking why *that* row got *that*
> answer. The habit that actually worked was writing down what I expected
> before reading the output, so a wrong-but-plausible result had something to
> contradict.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The second condition in UC-X's ambiguity rule. The rule initially read
> "refuse if the second-best document scores within 20% of the best" — which is
> the obvious anti-blending rule, and it is wrong. It refused Q2 ("Can I
> install Slack on my work laptop?") because the finance policy scored close by
> also mentioning laptops, while covering nothing the IT policy missed. It was
> withholding an answer the documents plainly contain.
>
> What I added:
>
> > "Both conditions are required. A close score on its own is not ambiguity:
> > ... It offers less of the same answer, not a competing one, and refusing
> > there would withhold an answer the documents plainly contain. Ambiguity
> > means a rival source could genuinely answer something the leader cannot."
>
> It matters because it is the difference between a system that is *safe* and
> one that is *useful*. A refusal is not free — an over-refusing assistant gets
> abandoned, and an abandoned assistant protects nobody. Encoding *why* two
> sources conflict, rather than just *that* their scores are close, is what let
> Q4 refuse and Q2 answer under one rule.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Any AI-assisted change I make to a data-processing script that touches
> incomplete records. The UC-0C null-propagation finding generalises well beyond
> this workshop: the dangerous row is not the one with the missing value — that
> one is obvious and usually handled — it is the *next* row, which looks
> complete and quietly inherits the gap. Before accepting generated code for
> that kind of task, I will write the Enforcement rules first ("a value derived
> from a null operand is itself null and must say so") and then run the CRAFT
> loop against a deliberately broken input, rather than against the happy path.

---

## Reviewer Notes *(tutor fills this section)*

| Criterion | Score /4 | Notes |
|---|---|---|
| RICE prompt quality | | |
| agents.md quality | | |
| skills.md quality | | |
| CRAFT loop evidence | | |
| Test coverage | | |
| **Total** | **/20** | |

**Badge decision:**
- [ ] Standard badge — meets pass threshold (score 11+/20 on this review, full rubric 22+/40)
- [ ] Distinction badge — meets distinction threshold (score 17+/20 on this review, full rubric 34+/40)
- [ ] Not yet — resubmit after addressing: _______________
