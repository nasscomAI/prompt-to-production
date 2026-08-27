# agents.md — UC-0A Complaint Classifier

# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.

# Delete these comments before committing.

agents:

&nbsp; - name: complaint\_classifier\_agent

&nbsp;   role: Reads complaints and assigns categories.

&nbsp;   skills\_used: \[classify\_complaint, extract\_location]

&nbsp;   decision\_logic: Uses keywords and text analysis to classify complaints.

&nbsp;   error\_handling: Flags as "unclassified" if no match is found.



&nbsp; - name: reporting\_agent

&nbsp;   role: Generates summary reports for ward officers.

&nbsp;   skills\_used: \[classify\_complaint, extract\_location]

&nbsp;   decision\_logic: Groups complaints by ward and type, outputs CSV/JSON.

&nbsp;   error\_handling: Skips incomplete complaints and logs errors.

