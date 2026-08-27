skills:
  - name: classify_category
    description: Determine the complaint category based on keywords in the description.
    input: complaint description string
    output: category string (Pothole, Flooding, Garbage, Streetlight, Other)
    error_handling: If description is empty or unclear, return category 'Other' and flag NEEDS_REVIEW.

  - name: assign_priority
    description: Determine the priority level of the complaint based on severity keywords.
    input: complaint description string
    output: priority string (High or Normal)
    error_handling: If description is missing or invalid, default priority to Normal.