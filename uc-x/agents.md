# UC-X Agents

## Document Query Agent
- Reads policy documents CSV and answers questions.
- Each answer comes from a single document; cross-document blending forbidden.
- Input: CSV (doc_id, text)
- Output: CSV (doc_id, answer)