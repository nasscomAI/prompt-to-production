\# Skills



\## classify\_complaint

Input: one complaint description

Output: category, priority, reason, flag



Rules:

\- Category must be one of:

&nbsp; Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,

&nbsp; Heritage Damage, Heat Hazard, Drain Blockage, Other



\- Priority rules:

&nbsp; Urgent if description contains severity keywords:

&nbsp; injury, child, school, hospital, ambulance, fire, hazard, fell, collapse

&nbsp; Otherwise Standard or Low.



\- Reason must reference words from the complaint text.



\- Flag should be NEEDS\_REVIEW if classification is ambiguous.





\## batch\_classify

Reads the input CSV file.



For each complaint row:

\- apply classify\_complaint



Writes results to output CSV with columns:



description, category, priority, reason, flag

