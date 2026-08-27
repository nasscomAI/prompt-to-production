# UC-X — Ask My Documents: Skill Definitions

## Skill: retrieve_documents

### Description
Searches all loaded policy document sections for relevance to a user question
using keyword matching. Returns scored sections from a single best-matching document.

### Trigger
User submits a natural-language question.

### Input
- `question` (str): The user's question text

### Steps
1. Tokenize the question into lowercase words
2. Remove stop words (is, the, a, an, can, i, my, what, who, how, do, does, on, in, of, to, for, from, and, or, with, it, be, that, this, at, by, are, was, were, have, has, had, will, would, should, could, may, not, no, all)
3. For each section in each document:
   - Count how many query keywords appear in the section text (case-insensitive)
   - Record the score (number of matching keywords)
4. Filter out sections with score = 0
5. Group remaining sections by document
6. Select the document with the highest total relevance score
7. Return the top-scoring section(s) from that single document only

### Output
- List of matching sections, each with:
  - `document_name` (str): filename of the source document
  - `section_number` (str): e.g., "2.6", "3.1"
  - `section_text` (str): full text of the section
  - `score` (int): number of keyword matches
- OR empty list if no sections match any keywords

### Constraints
- NEVER return sections from more than one document
- Minimum score threshold: at least 1 keyword must match
- Sections are defined by numbered headings (e.g., "2.1", "3.4")

---

## Skill: answer_question

### Description
Formulates a user-facing answer from retrieved document sections, enforcing
citation rules and single-source attribution.

### Trigger
`retrieve_documents` returns results (or empty).

### Input
- `question` (str): Original user question
- `retrieved_sections` (list): Output from retrieve_documents

### Steps
1. If `retrieved_sections` is empty → output the refusal template exactly
2. If sections exist:
   a. Verify all sections come from the same document (enforced by retrieve_documents)
   b. For each relevant section, extract the factual answer
   c. Cite document name and section number for every claim
   d. Compose the answer in clear, direct language
3. Validate answer contains NO hedging phrases
4. Validate answer references only ONE document

### Output
- Formatted answer string with citations
- OR the exact refusal template text

### Refusal Template
```
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance.
```

### Constraints
- Never combine claims from multiple documents
- Never use hedging language
- Every factual claim must have a citation in format: [document_name, Section X.Y]
- If no match: use refusal template verbatim
