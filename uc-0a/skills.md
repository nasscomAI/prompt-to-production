skills:

&#x20; - name: classify\_complaint

&#x20;   description: Classifies a single complaint row into category, priority, reason, and flag.

&#x20;   input: A dict representing one row (complaint\_id, description, and other CSV columns).

&#x20;   output: A dict with keys category, priority, reason, flag, following the enforcement rules in agents.md.

&#x20;   error\_handling: If description is missing or empty, set category to Other, priority to Low, flag to NEEDS\_REVIEW, and reason to "No description provided."



&#x20; - name: batch\_classify

&#x20;   description: Reads the input CSV, classifies every row using classify\_complaint, and writes results to the output CSV.

&#x20;   input: input\_path (path to test\_\[city].csv), output\_path (path to write results CSV).

&#x20;   output: A CSV file at output\_path with one classified row per input row, including complaint\_id.

&#x20;   error\_handling: If a row is malformed or causes an error, skip that row (or mark NEEDS\_REVIEW) and continue — never crash the whole batch.

