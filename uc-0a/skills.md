# UC-0A Skills Definition

## Skill: classify_complaint
- **Description**: Classifies a single city complaint into a structured record enforcing taxonomy, priority triggers, reasoning, and review flags.
- **Input**: `dict` containing:
  - `description` (str): Detailed text of the complaint.
  - `location` (str, optional): Location or landmark of the incident.
- **Output**: `dict` containing:
  - `category` (str): One of [`Pothole`, `Flooding`, `Streetlight`, `Waste`, `Noise`, `Road Damage`, `Heritage Damage`, `Heat Hazard`, `Drain Blockage`, `Other`].
  - `priority` (str): One of [`Urgent`, `Standard`, `Low`].
  - `reason` (str): One sentence citing specific words from the description.
  - `flag` (str): `NEEDS_REVIEW` if ambiguous/vague, otherwise `""`.
- **Error Handling**: Vague, ambiguous, or short descriptions (< 10 words or lacking specific details) default to `category: "Other"` and `flag: "NEEDS_REVIEW"`.

---

## Skill: batch_classify
- **Description**: Reads a CSV file of complaints, executes `classify_complaint` for each valid row, and writes the classified output to a destination CSV file.
- **Input**:
  - `input_path` (str): File path to input complaints CSV (`id,description,location`).
  - `output_path` (str): File path to write classified results CSV (`id,description,location,category,priority,reason,flag`).
- **Output**: Path to the generated results CSV file.
- **Error Handling**: Malformed or unparseable rows are logged with error details and skipped, allowing batch processing of remaining valid rows to continue uninterrupted.
