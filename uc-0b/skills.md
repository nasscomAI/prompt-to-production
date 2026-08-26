# UC-0B — skills.md (Policy Summariser)

## skill: retrieve_policy
**Purpose:** Load a .txt policy and return it as structured numbered clauses.
**Input:** path to policy .txt file.
**Output:** ordered list of (clause_number, clause_text) tuples, e.g. ("5.2", "...").
**Logic:**
1. Read the file.
2. A clause begins with a number like `2.3` followed by text.
3. Join wrapped continuation lines into the same clause.
4. Section dividers and ALL-CAPS section headers end a clause.

## skill: summarize_policy
**Purpose:** Produce a compliant, clause-referenced summary.
**Input:** the list of (clause_number, clause_text) tuples.
**Output:** plain-text summary, one entry per clause, prefixed with [number].
**Logic:**
1. Emit every clause, in order, tagged by its number.
2. Clauses known to carry multiple binding conditions (2.6, 3.2, 5.2) are
   emitted verbatim and labelled, so no condition can be lost.
3. Add nothing that is not in the source text.
4. Run a verification pass (every clause present, all conditions intact, no
   banned scope-bleed phrase) and append the result.
