skills:
  - name: Text Preprocessing
    description: Convert complaint descriptions to lowercase and standardize text for keyword detection.
    input: String (complaint description)
    output: String (normalized description)
    error_handling: If input is missing or empty, returns empty string and flags the row for review.

  - name: Category Detection
    description: Detect the category of a complaint based on keywords in the description.
    input: String (normalized complaint description)
    output: String (category: Pothole, Flooding, Garbage, Traffic, Noise, Infrastructure Damage, Other)
    error_handling: If keywords are missing or unmatched, assigns "Other".

  - name: Priority Assignment
    description: Assign priority based on sensitive keywords.
    input: String (normalized complaint description)
    output: String (priority: Urgent or Normal)
    error_handling: Defaults to "Normal" if no priority keywords are found.

  - name: Reason & Flag
    description: Provide reasoning for the assigned category/priority and flag rows needing review.
    input: String (description), String (category/priority)
    output: Dictionary {reason: String, flag: String}
    error_handling: If description is missing or row fails, sets reason="No description provided" and flag="NEEDS_REVIEW".

  - name: Batch Classification
    description: Process multiple complaint rows from a CSV file and generate results CSV.
    input: CSV file with fields (complaint_id, description)
    output: CSV file with fields (complaint_id, category, priority, reason, flag)
    error_handling: Each row is processed individually; errors do not stop the batch. Problematic rows are flagged.
