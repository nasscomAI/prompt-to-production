# skills.md

skills:
  - name: classify_complaint
    description: Performs automated triage of a single complaint description into the fixed municipal taxonomy and determines priority based on safety-critical severity keywords.
    input: A single string containing the citizen's complaint description.
    output: A dictionary object with keys 'category' (Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), 'priority' (Urgent, Standard, Low), 'reason' (single sentence citing keywords), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: Genuinely ambiguous or unclassifiable text must be set to category 'Other' and flag 'NEEDS_REVIEW' to ensure manual oversight.

  - name: batch_classify
    description: Bulk classification workflow that reads an input CSV file and applies the 'classify_complaint' skill to each row, persisting results to a standardized output CSV.
    input: Absolute path to the input CSV file containing raw complaint descriptions.
    output: Absolute path to the generated results CSV file containing the full classification schema for all rows.
    error_handling: Must handle CSV parsing errors gracefully and ensure that every row in the input file is accounted for in the output, defaulting missing data to 'Other' with a 'NEEDS_REVIEW' flag.
