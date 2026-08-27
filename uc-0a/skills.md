# skills.md
# UC-0A Complaint Classifier skills definition.

skills:
  - name: classify_complaint
    description: Classify one complaint row into UC-0A output fields.
    input: dict representing a CSV row.
    output: dict with keys [category, priority, reason, and flag].

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint, and writes results_pune.csv.
    input: input_path, output_path
    output: CSV file.

allowed_categories:
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

priority_rules:
  - Urgent: Must trigger if words like [injury, child, school, hospital, ambulance, fire, hazard, fell, collapse] appear.
  - Standard/Low: Based on general severity.
