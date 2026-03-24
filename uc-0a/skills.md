# Skills: UC-0A Complaint Classifier

## `classify_complaint`
**Description:** Takes a single complaint description and strictly maps it to a category, priority, reason, and flag using exactly the allowed schema.
**Input:** `description` (string)
**Output:** Dictionary with keys: `category`, `priority`, `reason`, `flag`
**Logic:**
1. Match the description against the allowed exact categories: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage. Default to "Other" if completely unrelated.
2. If genuine ambiguity exists, set `flag` to "NEEDS_REVIEW", otherwise empty string.
3. Check for exact severity keywords (`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`). If present, `priority` is "Urgent". Otherwise, "Standard" or "Low".
4. Extract a one-sentence `reason` that cites specific words from the description.

## `batch_classify`
**Description:** Reads an input CSV of complaints, applies `classify_complaint` to each row, and writes the required output CSV.
**Input:** `input_csv_path`, `output_csv_path`
**Output:** Writes a CSV with columns: `id`, `description`, `category`, `priority`, `reason`, `flag`.
