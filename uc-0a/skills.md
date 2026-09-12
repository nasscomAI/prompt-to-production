skills:

* name: classify\_complaint

&#x20;   description: Classifies a single citizen complaint into a standard category and priority level with a justification.



&#x20;   input: "string (complaint text)"



&#x20;   output: "JSON object containing category, priority, reason, and optional flag"



&#x20;   error\_handling: "If the input text is empty or ambiguous, default category to Other and set flag to NEEDS\_REVIEW."



* name:  batch\_classify 

&#x20;   description: Processes a list of multiple citizen complaints in bulk and returns structured classifications for each.



&#x20;   input: "array of strings (complaint texts)"



&#x20;   output: "JSON array of classification objects"



&#x20;   error\_handling: "If any individual complaint in the batch is invalid, mark its category as Other and include a NEEDS\_REVIEW flag while continuing batch execution."


