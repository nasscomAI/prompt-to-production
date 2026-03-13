skills:

\- name: policy\_text\_reader

&nbsp; description: Reads policy documents from text files.

&nbsp; input: Path to policy text file.

&nbsp; output: Raw text string of policy.

&nbsp; error\_handling: If file missing or empty, return empty string and flag NEEDS\_REVIEW.



\- name: clause\_identifier

&nbsp; description: Detects key clauses in the policy text.

&nbsp; input: Raw policy text string.

&nbsp; output: List of clauses.

&nbsp; error\_handling: If no clauses detected, return empty list and flag NEEDS\_REVIEW.



\- name: summary\_generator

&nbsp; description: Produces a concise summary that retains the meaning of the policy.

&nbsp; input: List of clauses.

&nbsp; output: Summary text string.

&nbsp; error\_handling: If clauses are missing, include a note in summary and set flag NEEDS\_REVIEW.



\- name: summary\_writer

&nbsp; description: Writes the summary to a text file.

&nbsp; input: Summary string and output file path.

&nbsp; output: Summary written to file.

&nbsp; error\_handling: If writing fails, log error and set flag FAILED.

