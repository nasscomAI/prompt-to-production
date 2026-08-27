# Skills for UC-0B

## `retrieve_policy`
- **Input**: `input_path` to a `.txt` policy file.
- **Output**: The extracted text as structured numbered sections.
- **Behavior**: Reads the file completely without omitting any sections.

## `summarize_policy`
- **Input**: Structured sections from `retrieve_policy`.
- **Output**: A compliant summary with clause references.
- **Behavior**: Applies strict enforcement rules to ensure all clauses and multi-conditions are accurately preserved without scope bleed.
