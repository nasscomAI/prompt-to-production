# agents.md

# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.

# Delete these comments before committing.

agents:

&nbsp; - name: number\_agent

&nbsp;   role: Extracts and formats numbers from text.

&nbsp;   skills\_used: \[extract\_numbers]

&nbsp;   decision\_logic: Pulls numeric values and prepares them for reporting.

&nbsp;   error\_handling: Returns empty list if no numbers found.



&nbsp; - name: check\_agent

&nbsp;   role: Validates whether numbers look correct.

&nbsp;   skills\_used: \[validate\_range]

&nbsp;   decision\_logic: Checks if numbers are within expected ranges.

&nbsp;   error\_handling: Flags as "invalid" if out of range.



