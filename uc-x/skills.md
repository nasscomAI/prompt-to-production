# skills.md
# UC-X — Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance) and indexes them systematically by document name and section number.
    input: File paths to the three plain text policy documents.
    output: A vectorized or indexed mapping of text segments grouped securely by origin document identity.
    error_handling: Halts index creation if any source file is missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a strict citation format or a strict refusal.
    input: The user's natural language question string.
    output: Either a single-source explicitly cited answer, or the mandated verbatim refusal template.
    error_handling: Systematically falls back to the exact refusal template if retrieval confidence is low or if blending is required to form a full answer.
