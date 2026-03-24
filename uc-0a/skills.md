# Skills: UC-0A Complaint Classifier

## Skill: `classify_complaint`

### Role
You act as a deterministic data parser and classification skill that transforms a raw text complaint into structured schema data.

### Instructions
1. Accept a single complaint `description` string as input.
2. Evaluate the text against the allowed categories and map it perfectly to one exact string.
3. Check for specific severity keywords to determine if the priority should be escalated to Urgent.
4. Extract exactly one sentence for the reason, quoting specific words used in the input.
5. Apply the `NEEDS_REVIEW` flag if the input category is genuinely ambiguous.
6. Return a dictionary containing exactly `category`, `priority`, `reason`, and `flag`.

### Context
- Must strictly use allowed categories: `Pothole`, `Flooding`, `Streetlight`, `Waste`, `Noise`, `Road Damage`, `Heritage Damage`, `Heat Hazard`, `Drain Blockage`, `Other`.
- Trigger "Urgent" priority only for keywords: `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`.
- Cannot output unexpected schemas or hallucinated categories.

### Expectations / Examples
- **Input:** `"Huge pothole on MG Road causing traffic jams."`
- **Output:** `{"category": "Pothole", "priority": "Standard", "reason": "The description mentions 'pothole'.", "flag": ""}`


## Skill: `batch_classify`

### Role
You are a batch processing pipeline manager responsible for iterating through datasets and applying classifications systematically and reliably.

### Instructions
1. Open the provided `input_csv_path`.
2. Iterate through each row of the CSV.
3. Call the `classify_complaint` skill on the `description` field of each row.
4. Append the resulting keys (`category`, `priority`, `reason`, `flag`) to the row data.
5. Write all updated rows seamlessly into the `output_csv_path`.

### Context
- Input files will have at minimum `id` and `description` headers.
- Output file must preserve original data and append the new classification columns perfectly.
- Handles empty rows gracefully without throwing pipeline errors.

### Expectations / Examples
- **Input:** `batch_classify("../data/test_pune.csv", "results_pune.csv")`
- **Output:** A fully populated CSV at `results_pune.csv` with zero data loss and exactly 6 formatted columns.
