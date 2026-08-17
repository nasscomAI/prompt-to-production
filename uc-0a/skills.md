skills:



&#x20; - name: classify\_complaint



&#x20;   description: >

&#x20;     Classify one citizen complaint into an approved category,

&#x20;     priority, reason, and review flag.



&#x20;   input: >

&#x20;     A dictionary containing one complaint row.

&#x20;     The main fields used are complaint\_id and description.



&#x20;   output: >

&#x20;     A dictionary containing complaint\_id, category, priority,

&#x20;     reason, and flag.



&#x20;   categories:

&#x20;     - Pothole

&#x20;     - Flooding

&#x20;     - Streetlight

&#x20;     - Waste

&#x20;     - Noise

&#x20;     - Road Damage

&#x20;     - Heritage Damage

&#x20;     - Heat Hazard

&#x20;     - Drain Blockage

&#x20;     - Other



&#x20;   priority\_rules:

&#x20;     urgent:

&#x20;       - injury

&#x20;       - child

&#x20;       - school

&#x20;       - hospital

&#x20;       - ambulance

&#x20;       - fire

&#x20;       - hazard

&#x20;       - fell

&#x20;       - collapse

&#x20;       - gas leak



&#x20;     standard:

&#x20;       - unsafe

&#x20;       - dangerous

&#x20;       - fall risk

&#x20;       - risk

&#x20;       - inaccessible

&#x20;       - health concern

&#x20;       - flooding risk

&#x20;       - unbearable

&#x20;       - subsidence

&#x20;       - standing in water

&#x20;       - traders suffering losses



&#x20;     low:

&#x20;       - No urgent or standard safety indicator is present.



&#x20;   error\_handling: >

&#x20;     If the description is missing, return category Other,

&#x20;     priority Low, and flag NEEDS\_REVIEW.

&#x20;     If the category is genuinely ambiguous, use Other and

&#x20;     flag NEEDS\_REVIEW. Do not invent facts.



&#x20;   reason\_rule: >

&#x20;     The reason must be based on evidence from the complaint

&#x20;     description. When a severity keyword triggers Urgent,

&#x20;     the reason identifies the matched severity keyword.



&#x20; - name: batch\_classify



&#x20;   description: >

&#x20;     Read all complaint rows from a CSV, classify each row using

&#x20;     classify\_complaint, and write the results to an output CSV.



&#x20;   input: >

&#x20;     Input CSV path containing complaint records and output CSV path.



&#x20;   output: >

&#x20;     CSV containing complaint\_id, category, priority, reason,

&#x20;     and flag for every input row.



&#x20;   error\_handling: >

&#x20;     Handle invalid or incomplete rows without stopping the

&#x20;     entire batch. Flag problematic rows with NEEDS\_REVIEW

&#x20;     and continue processing the remaining rows.
