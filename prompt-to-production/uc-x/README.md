# UC-X — Ask My Documents

**Core failure modes:** Cross-document blending · Hedged hallucination · Condition dropping

---

## Your Input Files
```
../data/policy-documents/policy_hr_leave.txt
../data/policy-documents/policy_it_acceptable_use.txt
../data/policy-documents/policy_finance_reimbursement.txt
```

## Run Command
```bash
python app.py
```
Interactive CLI — type questions, read answers.

---

## Do This Before Writing Any Prompt

Define your **refusal template** — the exact wording the system must use when a question is not in the documents. Write it here before opening your AI tool:

```
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance.
```

This template goes verbatim into your RICE Enforcement and agents.md.
It is what prevents hedged hallucination — the system has a required response format that leaves no room for "while not explicitly covered..."

---

## The Critical Cross-Document Test Question

```
Can I use my personal phone to access work files when working from home?
```

**Why this is the trap:**
- IT policy (section 3.1): personal devices may access CMC email and the employee self-service portal only
- HR policy mentions approved remote work tools

The AI must NOT blend these into: "Yes, personal phones can be used for approved remote work tools and email."
That answer is not in either document. It is a blend — and it gives permission that does not exist.

A correctly built system must either:
- Answer from IT policy section 3.1 only (email + portal, that's it), OR
- Refuse — if the HR+IT combination creates genuine ambiguity

---

## The 7 Test Questions — Run All of These

| Question | Expected behaviour |
|---|---|
| "Can I carry forward unused annual leave?" | HR policy section 2.6 — exact limit, exact forfeiture date |
| "Can I install Slack on my work laptop?" | IT policy section 2.3 — requires written IT approval |
| "What is the home office equipment allowance?" | Finance section 3.1 — Rs 8,000 one-time, permanent WFH only |
| "Can I use my personal phone for work files from home?" | Single-source IT answer OR clean refusal — must NOT blend |
| "What is the company view on flexible working culture?" | Refusal template — not in any document |
| "Can I claim DA and meal receipts on the same day?" | Finance section 2.6 — NO, explicitly prohibited |
| "Who approves leave without pay?" | HR section 5.2 — Department Head AND HR Director, both required |

---

## Enforcement Rules Your agents.md Must Include
1. Never combine claims from two different documents into a single answer
2. Never use hedging phrases: "while not explicitly covered", "typically", "generally understood", "it is common practice"
3. If question is not in the documents — use the refusal template exactly, no variations
4. Cite source document name + section number for every factual claim

---

## Skills to Define in skills.md
- `retrieve_documents` — loads all 3 policy files, indexes by document name and section number
- `answer_question` — searches indexed documents, returns single-source answer + citation OR refusal template

---

## What Will Fail From the Naive Prompt
Run `"Answer questions about company policy."` first.
Test the personal-phone question immediately.
Watch for: blended answer citing both IT and HR; answer that starts with "while not explicitly covered"; missing section citations.

---

## Commit Formula
```
UC-X Fix [failure mode]: [why it failed] → [what you changed]
```
