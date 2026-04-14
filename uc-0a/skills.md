# skills.md

### Skills Overview
Operational capabilities required for the UC-0A Complaint Classifier to process municipal data with city-level context.

#### Skill: `classify_complaint`
- **Role**: Semantic row classifier.
- **Intent**: Map raw description text to a structured dictionary including a cited reason and priority level.
- **Context**: Access is restricted to `complaint_id`, `city`, and `description` of a single complaint.
- **Enforcement**: Must strictly use the 10-item taxonomy and safety-priority keywords. Must cite specific words from the description in the 'reason' field.
- **Input**: Dictionary with `complaint_id`, `city`, `description`.
- **Output**: Dictionary with `category`, `priority`, `reason`, and `flag`.

#### Skill: `batch_classify`
- **Role**: CSV orchestration engine.
- **Intent**: Transform a city-specific test file into a structured results file.
- **Context**: Processes raw CSV data targeting city-specific outputs (e.g., results_hyderabad.csv).
- **Enforcement**: Must handle null descriptions and malformed rows gracefully.
- **Input**: Source path for input CSV, destination path for results CSV.
- **Output**: A new CSV file containing the aggregated classification results.
