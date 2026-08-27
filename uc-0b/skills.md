# skills.md

# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.

# Delete these comments before committing.

skills:

&nbsp; - name: summarize\_text

&nbsp;   description: Creates a short summary of a document.

&nbsp;   input: Document text (string)

&nbsp;   output: Summary (string)

&nbsp;   error\_handling: Returns "summary unavailable" if text is too short.



&nbsp; - name: detect\_bias

&nbsp;   description: Checks if the summary changes the meaning of the original text.

&nbsp;   input: Original text and summary (strings)

&nbsp;   output: Boolean (true/false)

&nbsp;   error\_handling: Flags as "uncertain" if analysis fails.



