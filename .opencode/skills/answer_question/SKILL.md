---
name: answer-question
description: Searches indexed policy documents, returns single-source answer with citation or exact refusal template
---

## What I do
- Take a natural language question about company policy
- Search the indexed document store
- Return an answer from exactly one source document with citation
- Return the refusal template if the question is not covered

## Input
- Question: string (natural language question)

## Output
- Answer with document name + section citation, or refusal template

## Error handling
- If no document covers the question, return the refusal template verbatim
- If multiple documents match, return answer from the most specific match only (no blending)
