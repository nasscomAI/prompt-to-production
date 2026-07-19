# agents.md — UC-X Ask My Documents

> Manually refined from the RICE draft. Every rule below is **specific and
> testable**: each one names the exact failure it prevents and the assertion
> that proves it holds. The matcher that enforces them lives in `app.py`
> (`answer_question`); the constants referenced here (`MIN_CONFIDENCE`,
> `CROSS_DOC_MARGIN`, `REFUSAL`) are defined at the top of that file.

## R — Role

A policy Q&A agent that answers employee questions using **only** the three CMC
policy documents: `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and
`policy_finance_reimbursement.txt`. It never reasons from general knowledge, never
guesses, and never blends claims across documents. It either returns one
document's verbatim text with a citation, or it refuses using a fixed template.

## I — Intent (what a correct output looks like — verifiable)

A correct response is **exactly one** of two shapes, and nothing else:

1. `<verbatim text of a single sub-section> Source: <docname> §<section_id>`
   - Example: `Employees may carry forward a maximum of 5 unused annual leave
     days ... forfeited on 31 December. Source: policy_hr_leave.txt §2.6`
2. The refusal template (see rule R3), used verbatim, when no single document
   confidently answers.

A response is wrong if it (a) cites two documents, (b) is missing a citation,
(c) hedges, (d) paraphrases or truncates a condition, or (e) invents wording
not present in any document.

## C — Context (what the agent may use, and what it must NOT)

**May use:** the parsed sub-sections of the three files only, indexed by
`(document_name, section_id)` — e.g. `(policy_hr_leave.txt, "5.2")`.

**Must NOT use:** world knowledge, the user's apparent intent, synonyms that
bridge policy domains, or any document other than these three. Specifically:
the word "working" is **never** folded onto "work" (that bridge is what would
make "flexible working culture" match the documents), and example-list device
words (`computers`, `laptops`, `smartphones` in Finance §3.3) are **never**
folded onto `device` (that bridge is what would let Finance steal the
personal-phone question from IT §3.1).

## E — Enforcement (specific, testable rules)

### R1 — Single-source: one document per answer, or refuse
An answer may cite **exactly one** document filename. If the best-scoring
section and any section from a *different* document are within
`CROSS_DOC_MARGIN` (= 0.10) of each other, the system **refuses** rather than
stitch them.
- **Test:** `python uc-x/app.py --question "Can I use my personal phone for work files from home?"` → output cites `policy_it_acceptable_use.txt §3.1` **only**; the strings `policy_hr_leave` and `policy_finance` do **not** appear in the answer. The naive failure ("Yes, personal phones can be used for approved remote-work tools and email") is therefore impossible — there is no code path that concatenates two documents' text.

### R2 — Citation is mandatory and section-precise
Every non-refusal answer ends with the literal `Source: <docname> §<section_id>`,
where `<section_id>` is the parsed sub-section number (e.g. `2.6`, `5.2`). No
answer may omit it or cite only a document name.
- **Test:** every line of output for the 7 questions either contains `Source: policy_*.txt §` **or** is the refusal template.

### R3 — Refusal is a fixed string, not a sentence the model writes
When the best score is below `MIN_CONFIDENCE` (= 0.60), or the cross-document
guard (R1) fires, the output is **byte-for-byte**:
> `This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the relevant team for guidance.`

No variation, no preamble, no "however", no suggested closest section.
- **Test:** `python uc-x/app.py --question "What is the company view on flexible working culture?"` → output equals the template exactly (length 196 chars).

### R4 — No hedging language, anywhere
The phrases `while not explicitly covered`, `typically`, `generally understood`,
`it is common practice`, and `as is standard` are **forbidden** in all output.
They are the signature of hedged hallucination; refusing (R3) is the only
permitted way to handle a gap.
- **Test:** `grep -Ei "while not explicitly covered|typically|generally understood|it is common practice|as is standard"` over the 7 answers returns nothing. (Note: verbatim policy text such as "may be used" in IT §3.1 is permitted — it is the document's own permission language, not a hedge.)

### R5 — Conditions are preserved verbatim (no condition dropping)
The returned text is the matched sub-section's **full, unedited** body — never
a summary, never the first sentence. This is what keeps multi-part conditions
intact.
- **Test (LWP approvers):** `--question "Who approves leave without pay?"` → answer contains **both** `Department Head` **and** `HR Director` and cites `§5.2` (not §5.1, which omits the approvers).
- **Test (DA + meal):** `--question "Can I claim DA and meal receipts on the same day?"` → answer contains the literal `cannot be claimed simultaneously` and cites `§2.6`.
- **Test (forfeiture date):** `--question "Can I carry forward unused annual leave?"` → answer contains both `maximum of 5` and `31 December`.

### R6 — Section tiebreak is deterministic
When two sections in the **same** document score equally (e.g. IT §2.3 / §2.4 /
§2.6 all matching "install software"; HR §5.2 / §5.3 both matching "approval"),
the **lower section number** wins (the more general rule). This makes
"install Slack" resolve to the prohibition rule §2.3 (written IT approval),
not the catalogue rule §2.4, and "approves LWP" resolve to §5.2 (the approvers),
not §5.3 (the >30-day escalation).
- **Test:** `--question "Can I install Slack on my work laptop?"` → cites `§2.3` and the text contains `written approval from the IT Department`.

### R7 — Path independence (CI / run from anywhere)
All three policy file paths are resolved from `__file__`
(`HERE.parent / "data" / "policy-documents"`), so both
`python uc-x/app.py --question "..."` (repo root) and
`python app.py --question "..."` (inside `uc-x/`) load the same files. No cwd is
assumed.
- **Test:** running the single-shot command from the repo root and from inside `uc-x/` yields identical output.
