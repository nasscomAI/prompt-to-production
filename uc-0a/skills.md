skills:
  -  name : classify_complaint 
     description: Classifies a single citizen complaint into a standard category and priority level with a justification.
     input: "string (complaint text)"
     output: "JSON object containing category, priority, reason, and optional flag"
     error_handling: "If the input text is empty or ambiguous, default category to Other and set flag to NEEDS_REVIEW."

  -  name: batch_classify
    description: Processes a list of multiple citizen complaints in bulk and returns structured classifications for each.
    input: "array of strings (complaint texts)"
    output: "JSON array of classification objects"
    error_handling: "If any individual complaint in the batch is invalid, mark its category as Other and include a NEEDS_REVIEW flag while continuing batch execution."