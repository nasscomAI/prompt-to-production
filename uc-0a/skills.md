# skills.md — UC-0A Agent Capabilities

## classify_complaint
**Description:** Processes a single citizen complaint description and returns a structured classification.
**Input:** One complaint row description.
**Output:** Exact `category`, `priority`, `reason` (one sentence citing specific words), and a review `flag` (NEEDS_REVIEW or blank).

## batch_classify
**Description:** Orchestrates the processing of multiple complaints by reading from and writing to CSV files.
**Process:** 
1. Reads input CSV file.
2. Applies `classify_complaint` for each row to obtain structured data.
3. Writes the resulting classified rows to the output CSV file.
