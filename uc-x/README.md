# UC-X --- Ask My Documents

**Core failure modes:** Cross-document blending · Hedged hallucination ·
Condition dropping

## Your Input Files

``` text
policy_hr_leave.txt
policy_it_acceptable_use.txt
policy_finance_reimbursement.txt
```

## Run Command

``` bash
python app.py
```

Interactive CLI --- type questions and read answers.

## Refusal Template

``` text
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance.
```

## System Requirements

-   Answer only from the provided policy documents.
-   Never use external knowledge.
-   Never infer missing information.
-   Never combine information from multiple documents into one answer.
-   Always provide the source document name and section number for every
    factual answer.
-   Use the refusal template exactly when the answer is unavailable or
    requires combining multiple documents.

## Test Questions

  -----------------------------------------------------------------------
  Question                            Expected Behaviour
  ----------------------------------- -----------------------------------
  Can I carry forward unused annual   HR Policy Section 2.6
  leave?                              

  Can I install Slack on my work      IT Policy Section 2.3
  laptop?                             

  What is the home office equipment   Finance Policy Section 3.1
  allowance?                          

  Can I use my personal phone for     IT Policy Section 3.1 only (no
  work files from home?               cross-document blending).

  What is the company view on         Return the refusal template.
  flexible working culture?           

  Can I claim DA and meal receipts on Finance Policy Section 2.6
  the same day?                       

  Who approves leave without pay?     HR Policy Section 5.2
  -----------------------------------------------------------------------

## Enforcement Rules

1.  Never combine claims from different policy documents.
2.  Never use hedging language.
3.  If the answer is unavailable, return the refusal template exactly.
4.  Every factual answer must cite the source document and section
    number.

## Required Skills

### retrieve_documents

Load and index the three policy documents.

### answer_question

Return either a single-source answer with citation or the refusal
template.

## Commit Message Format

``` text
UC-X Fix [failure mode]: [why it failed] → [what you changed]
```
