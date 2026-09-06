# skills.md — UC-0B Policy Summary Skills

## retrieve_policy

Purpose:
Load the provided `.txt` policy document and return its contents as structured,
numbered policy sections.

Inputs:
- Policy document path.

Process:
1. Read the policy document completely.
2. Preserve every numbered clause and its original meaning.
3. Keep clause numbers so each requirement can be traced back to the source.
4. Do not add, remove, or reinterpret policy information.

Output:
A structured list of policy sections and numbered clauses that can be used by
the summarization skill.

---

## summarize_policy

Purpose:
Create a concise but complete summary of the policy while preserving all
requirements and conditions.

Inputs:
- Structured policy sections produced by `retrieve_policy`.

Process:
1. Summarize the policy section by section.
2. Include every required clause from the clause inventory:
   2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2.
3. Preserve all important numbers, deadlines, forms, approvers, conditions,
   exceptions, and forfeiture rules.
4. Preserve strong obligation language such as "must", "requires", "will",
   and "not permitted".
5. For Clause 5.2, explicitly state that LWP requires approval from BOTH the
   Department Head AND the HR Director, and that manager approval alone is
   not sufficient.
6. Include clause references in the summary.
7. Do not invent information or use outside knowledge.
8. Do not silently omit any condition from a clause.
9. If a clause cannot be safely summarized without losing meaning, quote the
   clause and clearly flag it.
10. Perform a final completeness check against the required clause inventory
    before producing the output.

Output:
A concise, complete, clause-referenced policy summary with no invented
information and no omitted conditions.