# Skills: Document Assistant

## retrieve_documents
**Description:** Loads all 3 policy files, indexes by document name and section number.
**Inputs:** None
**Outputs:** Dictionary of documents

## answer_question
**Description:** Searches indexed documents, returns single-source answer + citation OR refusal template.
**Rules:** 
1. Prevent cross-document blending. Find the best matching document.
2. Formulate answer using only the source text. No hedging.
3. If missing, output refusal.
4. Provide Source: Document - Section.
