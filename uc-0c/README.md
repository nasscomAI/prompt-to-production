# UC-X — Ask My Documents

**Core failure modes:** Cross-document blending · Hedged hallucination · Condition dropping

---

## Your Input Files

```
policy_hr_leave.txt
policy_it_acceptable_use.txt
policy_finance_reimbursement.txt
```

## Run Command

```bash
python app.py
```

Interactive CLI — type questions and read answers.

---

## Refusal Template

The assistant **must** use the following response exactly when the requested information is not available in the policy documents.

```
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance.
```

---

## System Requirements

The assistant must:

* Answer only from the provided policy documents.
* Never use external knowledge.
* Never infer missing information.
* Never combine information from multiple documents into one answer.
* Always provide the source document name and section number for every factual answer.
* Use the refusal template exactly when the answer is unavailable or requires combining multiple documents.

---

## Input Documents

* `policy_hr_leave.txt`
* `policy_it_acceptable_use.txt`
* `policy_finance_reimbursement.txt`

---

## Test Questions

| Question                                              | Expected Behaviour                                                                                    |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Can I carry forward unused annual leave?              | HR Policy Section 2.6                                                                                 |
| Can I install Slack on my work laptop?                | IT Policy Section 2.3                                                                                 |
| What is the home office equipment allowance?          | Finance Policy Section 3.1                                                                            |
| Can I use my personal phone for work files from home? | Answer only from IT Policy Section 3.1 or refuse if ambiguous. Do **not** combine HR and IT policies. |
| What is the company view on flexible working culture? | Return the refusal template.                                                                          |
| Can I claim DA and meal receipts on the same day?     | Finance Policy Section 2.6                                                                            |
| Who approves leave without pay?                       | HR Policy Section 5.2                                                                                 |

---

## Enforcement Rules

1. Never combine claims from different policy documents.
2. Never use hedging language such as:

   * "typically"
   * "generally"
   * "while not explicitly covered"
   * "common practice"
3. If the answer is not explicitly available, return the refusal template exactly.
4. Every factual statement must include the source document name and section number.

---

## Required Skills

### retrieve_documents

* Load all three policy documents.
* Index them by document name and section number.

### answer_question

* Retrieve information from a single policy document.
* Return:

  * the answer with document name and section number, or
  * the exact refusal template.

---

## Expected Behaviour

The application should:

* Load all three policy documents.
* Accept questions from the user through an interactive command-line interface.
* Search only the provided documents.
* Return a single-source answer with citation.
* Refuse questions outside the available documentation using the exact refusal template.

---
