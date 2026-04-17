# UC-0A Skills — Complaint Classification Engine

## `retrieve_vibe_context()`
- **Action**: Loads the classification rules and priority triggers from the workshop metadata (README and agents definition).
- **Format**: Returns a dictionary containing valid categories and severity keywords.
- **RAG Principle**: Ensures the system always operates on the most current "ground truth" logic rather than cached assumptions.

## `classify_complaint(row, context)`
- **Action**: Applies RAG-style grounding to a single complaint row.
- **Steps**:
    1.  Parse the `description`.
    2.  Check for **Severity Keywords** from `context` (Semantic Search).
    3.  Match `description` keywords against **Category Definitions** (Semantic Mapping).
    4.  Generate `reason` by extracting the matching pivot words.
- **Format**: Returns `category`, `priority`, `reason`, `flag`.

## `batch_classify(input_path, output_path)`
- **Action**: Orchestrates the classification of an entire city dataset.
- **Steps**:
    1.  Load CSV from `input_path`.
    2.  Instantiate `context` using `retrieve_vibe_context()`.
    3.  Apply `classify_complaint` to every row.
    4.  Write results to `output_path`.
- **RAG Principle**: Logs the retrieval source for each batch to ensure traceability.
