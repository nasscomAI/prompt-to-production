# skills.md

# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.

# Delete these comments before committing.

skills:

&nbsp; - name: classify\_complaint

&nbsp;   description: Categorizes a citizen complaint into types (pothole, streetlight, flooding, garbage).

&nbsp;   input: Complaint text (string)

&nbsp;   output: Complaint category (string label)

&nbsp;   error\_handling: Returns "unknown" if no category matches.



&nbsp; - name: extract\_location

&nbsp;   description: Finds ward and location details from complaint text.

&nbsp;   input: Complaint text (string)

&nbsp;   output: Ward number and location (JSON format)

&nbsp;   error\_handling: Leaves fields empty if location cannot be parsed.



