# Skills for UC-X

## `retrieve_documents`
- **Purpose**: Loads all 3 policy files and indexes them cleanly by document name and section number.
- **Constraints**: Keeps content distinctly siloed to avoid cross-document blending.

## `answer_question`
- **Purpose**: Searches the indexed documents and returns a single-source answer with a strict citation.
- **Constraints**: Will return the exact refusal template if the answer cannot be found in a single source. Does not hedge.
