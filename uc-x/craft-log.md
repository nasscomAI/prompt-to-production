# UC-X — CRAFT log

## C — The refusal template, written before opening any tool

Per the README, the exact wording was fixed first and lives in `app.py` as
`REFUSAL_TEMPLATE`. It is printed character for character and is never appended to.
A refusal with a helpful hint stapled on is not a refusal — the hint is exactly where
the invented permission gets in.

## R — Run: the naive prompt, and the trap question

Naive prompt: `"Answer questions about company policy."`
Test question: *"Can I use my personal phone to access work files when working from home?"*

The blended answer looks like this:

> "Yes — personal phones can be used for approved remote work tools and CMC email,
> provided you follow the usual security requirements."

Both premises are real:

| Source | What it actually says |
|---|---|
| IT 3.1 | personal devices may access CMC email **and the self-service portal only** |
| HR / FIN | mention approved remote-work arrangements |

The conclusion appears in neither. And note where the damage is: the word **"only"**
is gone. A restriction became an authorisation, and the sentence reads more helpful for
having done it.

| Failure mode | How it shows up |
|---|---|
| Cross-document blending | premises from IT + HR, conclusion from neither |
| Hedged hallucination | "while not explicitly covered, it's generally understood that…" — the hedge signals low confidence while still granting the permission |
| Condition dropping | "requires approval" for LWP, with both named approvers gone |
| Stopword confidence | "flexible working culture" matches "working" in "within 10 **working** days" and produces a researched-looking answer about leave grievances |

## A — Structural defences, not instructions

Telling a system "don't blend" leaves blending possible. Here the answer is assembled
from clauses belonging to **one** document, and the property is asserted before printing:

| Enforcement | Mechanism |
|---|---|
| single source | answer built only from `in_winner`; `len(cited_docs) != 1` → refuse |
| no invented permission | answer text is verbatim clause text — there is no paraphrase path |
| no hedging | output scanned against `BANNED_HEDGES`; a hit replaces the answer with the template |
| limits survive | `only` / `not` / `cannot` counted in source vs answer; any loss → refuse |
| stopword confidence | a distinctive-term (idf) requirement **and** a ≥2-matched-term requirement |
| not covered | template verbatim, asserted equal to `REFUSAL_TEMPLATE` in the test run |

Because answers are verbatim quotations, condition dropping is impossible by
construction: "Department Head and the HR Director" cannot become "requires approval"
when nothing rewrites the clause.

## F — Three rounds of fixes, each found by running the 7 questions

**Round 1 — scoring documents by their single best clause.** Q7 *"Who approves leave
without pay?"* **refused**, which is wrong — HR 5.2 answers it directly. HR's best clause
scored 9.01 and Finance's 7.37, or 82%, tripping the 80% contention threshold. One
incidental Finance match was rivalling three on-topic HR clauses.

Fix: score a document by its **top 3 clauses summed** (`DOC_SCORE_CLAUSES`). Measured
across all 7 questions:

| Question | best-clause ratio | top-3-summed ratio |
|---|---|---|
| Q4 personal phone | 88% → refuse | 70% → IT answer |
| Q7 LWP | 82% → **wrong refusal** | 49% → HR answer |

**Round 2 — refusing for the wrong reason.** Q5 *"flexible working culture"* refused, but
the reason logged was cross-document contention (HR 3.01 vs FIN 3.01, a 100% tie). The
real reason is that the question shares exactly one incidental word with the corpus —
"working", from "within 10 working days". A right answer for a wrong reason breaks as
soon as the data shifts.

Fix: `MIN_MATCHED_TERMS = 2` and a raised `MIN_SCORE`. Q5 now refuses with
*"best match shares only 1 term (working) with the question — a single incidental term is
coincidence, not coverage."*

**Round 3 — right document, wrong section.** Q4 then answered from IT, but cited
2.1/3.2/3.5 and **missed 3.1** — the clause the README names, and the one carrying
"only". Clause 2.1 topped the ranking because *"mobile phones issued by CMC"* matched
"phone"… in the **Corporate Devices** section. The question is about a personal phone.
Same document, wrong subject.

Fix: a second narrowing stage. After the governing document, pick the governing
**section** by the same top-N-summed method — section 3 (Personal Devices/BYOD) beats
section 2 — then cite only clauses from it. This also cleaned up Q1 (dropped a
sick-leave clause) and Q7 (dropped an unrelated Loss-of-Pay clause).

## T — All 7 test questions

| # | Question | Result | Expected |
|---|---|---|---|
| 1 | carry forward unused annual leave | HR **2.6** + 2.7 | HR 2.6 — limit and forfeiture date ✔ |
| 2 | install Slack on work laptop | IT 2.1 + **2.3** + 2.4 | IT 2.3 — written IT approval ✔ |
| 3 | home office equipment allowance | FIN **3.1** + 3.2 + 3.3 | FIN 3.1 — Rs 8,000, permanent WFH only ✔ |
| 4 | personal phone for work files | IT **3.1** + 3.2 + 3.5, IT only | single-source IT **or** refusal ✔ |
| 5 | flexible working culture | refusal template | refusal template ✔ |
| 6 | DA and meal receipts same day | FIN 2.5 + **2.6** | FIN 2.6 — explicitly prohibited ✔ |
| 7 | who approves LWP | HR 5.1 + **5.2** + 5.3 | HR 5.2 — both approvers ✔ |

```
7 questions: 6 single-source answers, 1 template refusals, 0 blended answers.
Every answer cited exactly one document. Every refusal was the template character for character.
```

Q4 returns IT 3.1 with the limit intact — *"may be used to access CMC email and the CMC
employee self-service portal **only**"* — which is the restrictive truth the blend
destroys. Q7 returns 5.2 with **both** approvers and the "Manager approval alone is not
sufficient" exclusion.

Adversarial questions:

| Question | Result |
|---|---|
| "What is the dress code?" | refusal — no clause shares a content term |
| "What is the parking policy at the office?" | refusal — only "office" matched |
| "asdfgh qwerty" | refusal |
| "Can I get maternity leave for a third child?" | HR 4.2 + 4.3, single source |

## The limitation this UC surfaced — and what I did about it

Compound questions expose a gap that "never blend" does not cover on its own:

> "How many casual leaves do I get **and** can I expense my broadband?"

The system answers from Finance alone. That is correctly not a blend — and it is still
misleading, because half the question went unanswered with nothing saying so. Refusing to
blend does not by itself make a partial answer honest.

Fix: when another document holds substantive material (`PARTIAL_COVERAGE_RATIO`), it is
named in an audit line printed **outside** the answer text, so it can never become part
of the answer:

```
[AUDIT] sources cited: ['policy_it_acceptable_use.txt'] (count must be 1)
[AUDIT] NOT addressed above — policy_finance_reimbursement.txt also holds material
        matching this question. Ask about it separately; it is deliberately not
        merged into the answer.
```

## The rule the AI would not have written unprompted

> "A question that matches a clause only through common words — 'working', 'employee',
> 'policy', 'company' — is not covered. Require the match to rest on at least one
> distinctive term, or refuse. A confident answer assembled from stopword overlap is the
> worst possible output because it looks researched."

Every generated draft had a "refuse if you don't know" rule. None had a definition of
*not knowing* that a program could evaluate. "Refuse when unsure" is unimplementable;
"refuse when the match rests on one common word" is a threshold — and it is what turns
the refusal from an intention into a behaviour.
