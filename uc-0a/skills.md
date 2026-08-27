skills:



\* name: complaint\_text\_parser

&nbsp; description: Extracts and prepares complaint text from a CSV row for analysis.

&nbsp; input: Dictionary row from CSV containing complaint\_id and complaint\_text.

&nbsp; output: Cleaned complaint text string and complaint\_id.

&nbsp; error\_handling: If complaint\_text is missing or empty, return empty text and mark flag as NEEDS\_REVIEW.



\* name: complaint\_category\_classifier

&nbsp; description: Determines the complaint category based on keywords in the complaint description.

&nbsp; input: Complaint text string.

&nbsp; output: Category label (Water, Sanitation, Roads, Electricity, Other).

&nbsp; error\_handling: If no matching keywords are found, return category "Other" and set flag NEEDS\_REVIEW.



\* name: complaint\_priority\_detector

&nbsp; description: Assigns priority level to complaints based on severity keywords.

&nbsp; input: Complaint description text.

&nbsp; output: Priority level (High, Medium, Low).

&nbsp; error\_handling: If severity cannot be determined, default priority to Low and include explanation in reason field.



\* name: result\_writer

&nbsp; description: Writes classified complaint results into a structured CSV output file.

&nbsp; input: Classification result dictionary containing complaint\_id, category, priority, reason, and flag.

&nbsp; output: Row written to output CSV file.

&nbsp; error\_handling: If writing fails or row data is incomplete, log error and write fallback row with flag FAILED.



