# UC-X — skills.md (Ask My Documents)

## skill: retrieve_documents
**Purpose:** Load all 3 policy files and index them by document + section.
**Input:** path to the policy-documents directory.
**Output:** dict: filename -> { section_number: section_text }.
**Logic:**
1. For each of the 3 files, read the text.
2. Split into numbered sections (e.g. 3.1) using the same parser as UC-0B.
3. Keep each document's sections separate — the index never merges documents.

## skill: answer_question
**Purpose:** Return a single-source, cited answer OR the refusal template.
**Input:** the user's question, the document index.
**Output:** answer string with a [Source: file — section] citation, or the
verbatim refusal template.
**Logic:**
1. If the question matches a known not-in-docs topic -> refusal template.
2. Match the question against intent rules; each rule points to exactly ONE
   document + section, so the answer can only come from a single source.
3. Attach the citation (document filename + section number).
4. If nothing matches -> refusal template (never guess, never hedge).
5. A guard rejects any answer containing a banned hedge phrase.
