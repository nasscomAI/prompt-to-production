# Policy Expert Skills

## retrieve_documents
- **Input:** Paths to all 3 policy text files.
- **Task:** 
  1. Load all policy documents into a searchable structure.
  2. Index the content by document name and section number (e.g., `1.1`, `2.3`).
  3. Ensure all sections are correctly identified.
- **Output:** A structured, indexed collection of all policies.

## answer_question
- **Input:** Indexed collection of policies, user question.
- **Task:** 
  1. Identify the single most relevant policy document for the question.
  2. Locate the specific section(s) within that document that address the query.
  3. Formulate an answer that uses only the information from that single source.
  4. Ensure all conditions from the source text are included.
  5. Provide a citation (e.g., `policy_hr_leave.txt, Section 2.6`).
  6. If no single source provides a clear answer, use the exact refusal template.
  7. Verify the answer against the "no hedging" and "no blending" enforcement rules.
- **Output:** A single-source cited answer or the refusal template.
