# skills.md

skills:

  - name: classify_complaint

    description: >
      Classifies a single municipal complaint into one approved category,
      assigns priority, generates a justification, and determines
      whether manual review is required.

    input: >
      Dictionary representing one CSV row containing:
      complaint_id,
      description,
      and other optional metadata.

    output: >
      Dictionary containing:
      complaint_id,
      category,
      priority,
      reason,
      flag.

    error_handling: >
      If description is missing, empty, or cannot be classified
      confidently, return:
      category=Other,
      priority=Standard,
      flag=NEEDS_REVIEW,
      with an explanatory reason.


 - name: batch_classify

    description: >
      Reads an input CSV file, classifies every complaint using
      classify_complaint(), and writes the results into an output CSV.

    input: >
      Input CSV file path.

    output: >
      Output CSV containing:
      complaint_id,
      category,
      priority,
      reason,
      flag.

    error_handling: >
      Continue processing if an individual row fails.
      Invalid rows must not terminate execution.
      Failed rows should be written with:
      category=Other,
      priority=Standard,
      flag=NEEDS_REVIEW,
      and a processing error reason.