---
name: retrieve-policy
description: Loads a .txt policy file, returns content as structured numbered sections
---

## What I do
- Load a policy document from a .txt file
- Parse and structure it into numbered sections
- Return structured content for downstream summarization

## Input
- File path: string (path to .txt policy file)

## Output
- Structured document content with numbered clause references

## Error handling
- Return error if file does not exist or cannot be parsed
