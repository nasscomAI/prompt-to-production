# UC-X Skills

## Skill: retrieve_documents
**Input:** List of file paths
**Output:** Dict mapping document_name -> {section_number -> section_text}
**Logic:**
- Read each .txt file
- Parse section numbers (e.g. 1.1, 2.3, 5.2) and their text
- Index by filename and section number
- Return full index

## Skill: answer_question
**Input:** User question string, document index dict
**Output:** Answer string with citation OR refusal template string
**Logic:**
- Search all documents for sections relevant to the question
- If single-source match found: return answer citing document name + section number
- If cross-document match that would create new permission: return refusal template
- If no match: return refusal template verbatim
- Never combine claims from two different documents
