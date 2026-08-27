# skills.md

skills:
  - name: complaint_text_analysis
    description: Analyze the complaint description and detect important keywords.
    input: Complaint text string from the dataset.
    output: List of detected keywords related to civic issues.
    error_handling: If the complaint text is empty or unclear, return an empty keyword list.


  - name: complaint_category_classification
    description: Classify the complaint into the correct civic category.
    input: Complaint text and detected keywords.
    output: A category label such as Pothole, Flooding, Garbage, Water Supply, or Other.
    error_handling: If no category can be determined, return category "Other" and mark NEEDS_REVIEW.
