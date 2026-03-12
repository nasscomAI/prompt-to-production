skills:

\- name: csv\_reader

&nbsp; description: Reads CSV input files for ward or budget data.

&nbsp; input: Path to CSV file.

&nbsp; output: List of row dictionaries.

&nbsp; error\_handling: If file missing or malformed, return empty list and flag FAILED.



\- name: number\_validator

&nbsp; description: Validates numeric fields are present and within expected ranges.

&nbsp; input: Row dictionary with numeric fields.

&nbsp; output: Row dictionary with validated values and reason/flag.

&nbsp; error\_handling: If invalid, set flag to NEEDS\_REVIEW and explain in reason.



\- name: sum\_checker

&nbsp; description: Checks if sums of sub-values equal totals.

&nbsp; input: Row dictionary with sub-values and totals.

&nbsp; output: Flag and reason for any mismatch.

&nbsp; error\_handling: If mismatch, set flag NEEDS\_REVIEW.



\- name: result\_writer

&nbsp; description: Writes validation results to a CSV output file.

&nbsp; input: Validated row dictionaries.

&nbsp; output: CSV file with complaint\_id/ward\_id, validated numbers, and flags.

&nbsp; error\_handling: If writing fails, log error and flag row as FAILED.

