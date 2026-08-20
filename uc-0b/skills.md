skills:



&#x20; - name: retrieve\_policy



&#x20;   description: >

&#x20;     Load the supplied policy text file and identify its numbered

&#x20;     policy clauses without changing their meaning.



&#x20;   input: >

&#x20;     Path to a policy .txt file.



&#x20;   output: >

&#x20;     A structured collection of numbered clauses and their source text.



&#x20;   error\_handling: >

&#x20;     If the policy file cannot be read, report the error instead of

&#x20;     inventing policy content.





&#x20; - name: summarize\_policy



&#x20;   description: >

&#x20;     Produce a clause-complete policy summary from the structured

&#x20;     policy content.



&#x20;   input: >

&#x20;     Structured numbered policy clauses.



&#x20;   output: >

&#x20;     A concise summary containing clause references and preserving

&#x20;     every obligation, condition, threshold, deadline, approval

&#x20;     requirement, exception, and prohibition.



&#x20;   enforcement:

&#x20;     - "Do not omit required clauses."

&#x20;     - "Do not drop conditions from multi-condition obligations."

&#x20;     - "Do not weaken binding language."

&#x20;     - "Do not add information not present in the source."

&#x20;     - "Preserve approval requirements exactly."

&#x20;     - "Flag clauses when meaning cannot be safely summarized."





&#x20; - name: batch\_summarize



&#x20;   description: >

&#x20;     Read the policy document, retrieve its clauses, generate a

&#x20;     compliant summary, and write the summary to the requested output file.



&#x20;   input: >

&#x20;     Input policy path and output summary path.



&#x20;   output: >

&#x20;     A text file containing the verified policy summary.



&#x20;   error\_handling: >

&#x20;     Handle missing or unreadable input files without silently

&#x20;     generating invented content.
