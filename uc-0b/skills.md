# Skills: Policy Summarizer

## retrieve_policy
**Description:** Opens and reads a .txt policy file, returning the text content grouped by sections.
**Inputs:** `filepath`
**Outputs:** Array of section texts.

## summarize_policy
**Description:** Iterates through policy sections, extracting or summarizing critical clauses while preserving every condition strictly.
**Rules:**
- specifically check for dual-approval conditions and preserve both (e.g., Department Head AND HR Director).
- if meaning might be lost, copy the clause verbatim and add `[VERBATIM]`.
**Inputs:** Sections array
**Outputs:** Compliant summary text.
