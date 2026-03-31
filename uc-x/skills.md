Replacing 16 lines with 12 lines in [](file:///c%3A/Users/TELUGU%20SUMANTH/OneDrive/Documents/GitHub/prompt-to-production/uc-x/skills.md)


```

```
skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of file paths (strings) to the policy documents.
    output: Dictionary indexed by document name and section number containing the content.
    error_handling: If any file is not found or cannot be read, raises an error indicating the missing file.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation or the refusal template.
    input: String containing the user's question.
    output: String containing the answer with document name and section number citation, or the exact refusal template.
    error_handling: If the question is ambiguous, involves cross-document blending, hedged hallucination, or condition dropping, returns the refusal template; if input is invalid, raises an error.

Made changes.