# UC-0B --- Meaning-Preserving Policy Summarization

## Objective

Build an AI system that summarizes an HR leave policy **without changing
its legal or operational meaning**.

## Input

``` text
../data/policy-documents/policy_hr_leave.txt
```

## Output

``` text
uc-0b/summary_hr_leave.txt
```

## Run

``` bash
python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
```

## Requirements

-   Preserve every numbered clause.
-   Preserve all mandatory conditions, approvals and deadlines.
-   Do not hallucinate or add external HR knowledge.
-   If summarization would lose meaning, quote the original clause.

## Critical Clauses

  Clause   Requirement
  -------- ------------------------------------------------------------------
  2.3      14-day advance leave application
  2.4      Written manager approval before leave; verbal approval invalid
  2.5      Unapproved absence = Loss of Pay
  2.6      Maximum 5 carry-forward days; excess forfeited on 31 December
  2.7      Carry-forward leave must be used Jan--Mar
  3.2      Medical certificate for 3+ sick days within 48 hours
  3.4      Medical certificate before/after holidays regardless of duration
  5.2      LWP requires Department Head **and** HR Director approval
  5.3      LWP \>30 days requires Municipal Commissioner approval
  7.2      Leave encashment during service is prohibited

## Evaluation

-   Complete clause coverage
-   Meaning preservation
-   No hallucinations
-   Accurate approvals and deadlines
-   Clear, concise summary

## Folder Structure

``` text
uc-0b/
├── README.md
├── agents.md
├── skills.md
├── app.py
└── summary_hr_leave.txt
```
