# UC-X Document Skills

## retrieve_documents
**Input**: Directory containing policy `.txt` files.
**Process**:
1. Load `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`.
2. Parse each file into sections using numbered IDs (1.1, 2.1, etc.).
3. Store in an internal index: `{ doc_name: { section_id: text } }`.

## answer_question
**Input**: Natural language user question.
**Process**:
1. Keyword search across the indexed sections.
2. If multiple matches from different documents exist, evaluate which one is most primary for the intent (IT for technical access, HR for behavior, etc.).
3. Formulate the response based *only* on that single section.
4. If no clear section answers the question, apply the refusal template.
5. Append the citation: `Source: [Filename] Section [X.Y]`.
