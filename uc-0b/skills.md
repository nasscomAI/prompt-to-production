# UC-0B Skills

## retrieve_policy

### Purpose

Load the HR leave policy from the supplied `.txt` file and return
the policy as structured numbered sections.

### Input

Path to the source policy `.txt` file.

### Process

- Read the complete source file.
- Identify and preserve numbered policy clauses.
- Preserve the original clause numbers.
- Preserve all conditions, thresholds, deadlines, approvals,
  exceptions, and restrictions.
- Do not modify or invent policy information.

### Output

Structured policy sections that can be passed to `summarize_policy`.

---

## summarize_policy

### Purpose

Generate a faithful summary of the structured HR leave policy.

### Input

Structured numbered sections returned by `retrieve_policy`.

### Process

- Include every required numbered clause.
- Preserve every condition within each clause.
- Preserve binding requirements and prohibitions.
- Preserve multiple approval requirements.
- Preserve numerical thresholds and deadlines.
- Include clause references.
- Do not add information that is not present in the source.
- If summarizing a clause could change its meaning, quote the source
  clause and flag it.

### Output

A concise, verifiable summary containing all required clauses:

- 2.3
- 2.4
- 2.5
- 2.6
- 2.7
- 3.2
- 3.4
- 5.2
- 5.3
- 7.2

### Validation

Before returning the summary, verify:

1. All 10 required clauses are present.
2. No condition has been dropped.
3. No unsupported information has been added.
4. Binding obligations have not been weakened.
5. Clause 5.2 contains both Department Head and HR Director approval
   and states that Manager approval alone is insufficient.
6. Clause 5.3 retains the "exceeding 30 continuous days" threshold.