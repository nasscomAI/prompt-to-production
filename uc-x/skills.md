# Skills — UC-X Ask My Documents

## retrieve_documents
**Input:** `data_dir` — path to the folder containing the 3 policy .txt files
**Output:** dict of {filename: {section_number: section_text}}
**Behavior:**
- Parses each of the 3 documents independently using the same clause-
  extraction logic as UC-0B (detects "N.N <text>" headers, closes a
  clause on section dividers or headers).
- Keeps each document's sections in a separate namespace - documents
  are never merged into a single searchable blob, which is what
  prevents cross-document blending downstream.

## answer_question
**Input:** `question` string, the index from retrieve_documents
**Output:** a single-source answer string with citation, OR the exact
refusal template
**Behavior:**
- Checks the question against the known cross-document trap first
  (personal phone + work files) and routes it to IT section 3.1 only,
  with an explicit note that it does not extend to general file access.
- Checks against a known refusal trigger (flexible working culture)
  and returns the refusal template immediately.
- Otherwise matches the question against a fixed set of keyword rules,
  each mapped to exactly one document and section number.
- If no rule matches, returns the exact refusal template - never a
  hedged or partial answer.
