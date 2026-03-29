# Skills: Complaint Classifier

## Skill 1: classify_complaint
- **Description:** Classify a single complaint row into category, priority, reason, and ambiguity flag.
- **Input:** String description of citizen complaint (plain text)
- **Output:** Dictionary with keys: `category` (exact schema value), `priority` ("Urgent"/"Standard"/"Low"), `reason` (one sentence citing specific words), `flag` ("NEEDS_REVIEW" or blank)
- **Error Handling:** If description is ambiguous or cannot be mapped to allowed categories, returns category="Other" and sets flag="NEEDS_REVIEW".
- **Severity Detection:** Detects keywords (`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`) and forces priority="Urgent".

## Skill 2: batch_classify
- **Description:** Read complaints from input CSV, apply classify_complaint to each row, write output CSV with classifications.
- **Input:** File path to input CSV with columns: `complaint_id`, `description`, and others
- **Output:** File path to output CSV with added columns: `category`, `priority`, `reason`, `flag`
- **Error Handling:** Raises error if input file is empty or missing; writes partial results if individual row classification fails non-fatally.
- **Implementation:** Loops over each row, calls classify_complaint on description field, writes complete row + classification to output.

## Category Schema (Exact Enforcement)
- Pothole
- Flooding
- Streetlight
- Waste
- Noise
- Road Damage
- Heritage Damage
- Heat Hazard
- Drain Blockage
- Other

## Priority Rules
- **Urgent:** Triggered by severity keywords OR explicit electrical/fall hazards
- **Standard:** Default for non-emergency complaints
- **Low:** Reserved for minor, non-urgent issues
