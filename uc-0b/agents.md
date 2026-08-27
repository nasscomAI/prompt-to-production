# agents.md

# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.

# Delete these comments before committing.

agents:

&nbsp; - name: summary\_agent

&nbsp;   role: Creates summaries of documents.

&nbsp;   skills\_used: \[summarize\_text]

&nbsp;   decision\_logic: Produces concise summaries of input text.

&nbsp;   error\_handling: Returns "summary unavailable" if text is too short.



&nbsp; - name: validation\_agent

&nbsp;   role: Checks if summaries change the meaning of the original text.

&nbsp;   skills\_used: \[detect\_bias]

&nbsp;   decision\_logic: Compares summary with original text.

&nbsp;   error\_handling: Flags as "uncertain" if analysis fails.



