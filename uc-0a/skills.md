skills:
  - name: complaint_classifier
    description: Classifies a municipal complaint into a valid department and sub_category using only the approved taxonomy.
    input: Complaint text in plain language.
    output: JSON object with department, sub_category, severity, rationale, and ambiguity flag.
    error_handling: If the complaint is unclear or does not match a valid taxonomy category, mark ambiguity_flag as true and provide the closest safe classification with rationale.

  - name: severity_detector
    description: Detects complaint urgency using explicit severity cues such as safety risk, outage, blocked access, or hazard.
    input: Complaint text.
    output: Severity level as low, medium, or high based only on defined severity rules.
    error_handling: If severity cannot be clearly determined from the complaint text, default conservatively and explain the reasoning in rationale.
