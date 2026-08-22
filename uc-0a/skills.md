\# skills.md



skills:

&#x20; - name: classify\_complaint

&#x20;   description: >

&#x20;     Classify one civic complaint into an allowed category and priority,

&#x20;     provide evidence from the complaint, and flag uncertain cases.

&#x20;   input: >

&#x20;     A dictionary containing complaint\_id and a complaint description.

&#x20;   output: >

&#x20;     A dictionary containing complaint\_id, category, priority, reason,

&#x20;     and flag.

&#x20;   error\_handling: >

&#x20;     If the description is missing, empty, malformed, or ambiguous,

&#x20;     return category Other and flag NEEDS\_REVIEW rather than crashing

&#x20;     or inventing information.



&#x20; - name: batch\_classify

&#x20;   description: >

&#x20;     Read a complaint CSV, classify every row independently, and write

&#x20;     a results CSV containing the required classification fields.

&#x20;   input: >

&#x20;     An input CSV path containing complaint records and an output CSV path.

&#x20;   output: >

&#x20;     A CSV containing complaint\_id, category, priority, reason, and flag

&#x20;     for every input row.

&#x20;   error\_handling: >

&#x20;     Continue processing when an individual row is malformed or missing

&#x20;     data. Produce a reviewable output row with NEEDS\_REVIEW instead of

&#x20;     crashing the entire batch.

