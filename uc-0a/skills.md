# skills.md

skills:
  - name: classify_complaint_category
    description: Determines the primary category for the civic complaint from a strict list of allowed categories.
    input: "description (string): The raw text of the civic complaint."
    output: "category (string): One of [Roads & Traffic, Drainage & Flooding, Streetlighting, Sanitation & Waste, Public Safety, Noise Pollution, Other]."
    error_handling: "If the complaint is entirely ambiguous, return 'Other'."

  - name: assess_complaint_priority
    description: Analyzes the complaint text for specific high-severity keywords to assign a priority status.
    input: "description (string): The raw text of the civic complaint."
    output: "priority (string): 'Urgent' if severity keywords exist, otherwise 'Standard'."
    error_handling: "If no keywords are matched, default to returning 'Standard'."

  - name: extract_reasoning_keywords
    description: Extracts the specific phrases or words from the description that justify the assigned category and priority.
    input: "description (string), category (string), priority (string)"
    output: "reason (string): A short sentence citing the exact words from the description used to classify."
    error_handling: "If no specific keywords stand out, summarize the main point of the description as the reason."
