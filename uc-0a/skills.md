# Skills

## classify_complaint

### Purpose
Classify a single citizen complaint into the predefined complaint taxonomy.

### Input
A single complaint record containing a textual complaint description.

### Processing
- Read the complaint description.
- Match the description against the allowed complaint categories.
- Assign exactly one category from:
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
- Determine the priority:
  - Urgent
  - Standard
  - Low
- Assign **Urgent** if the complaint contains any of these severity keywords:
  - injury
  - child
  - school
  - hospital
  - ambulance
  - fire
  - hazard
  - fell
  - collapse
- Generate a one-sentence reason explaining the classification.
- If the complaint cannot be classified confidently, set:
  - flag = NEEDS_REVIEW

### Output
Returns:
- category
- priority
- reason
- flag

---

## batch_classify

### Purpose
Process an entire CSV file of citizen complaints.

### Input
CSV file containing multiple complaint records.

### Processing
- Read every complaint from the CSV file.
- Call `classify_complaint()` for each complaint.
- Append the following columns:
  - category
  - priority
  - reason
  - flag
- Preserve all existing columns.
- Write the classified records to a new CSV file.

### Output
A CSV file containing all original complaint data together with:
- category
- priority
- reason
- flag