# UC-0A Complaint Classifier Skills

## Defined Skills

### 1. `classify_complaint`
- **Description**: Evaluates a single citizen complaint row and determines category, priority, reason, and flag according to strict taxonomy rules.
- **Input**: Complaint dictionary containing `description`, `location`, `days_open`, etc.
- **Rules**:
  - `category`: Must be one of `Pothole`, `Flooding`, `Streetlight`, `Waste`, `Noise`, `Road Damage`, `Heritage Damage`, `Heat Hazard`, `Drain Blockage`, `Other`.
  - `priority`: Urgent if severity keywords (`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`) are present.
  - `reason`: One sentence referencing exact keywords from description.
  - `flag`: Set to `NEEDS_REVIEW` if ambiguous.

### 2. `batch_classify`
- **Description**: Reads input CSV, invokes `classify_complaint` for every record, and writes the output CSV.
- **Input**: Input CSV file path, Output CSV file path.
- **Output**: Output CSV populated with classification results.
