# skills.md — UC-0C Budget Data Analyst
 
 skills:
-  - name: [skill_name]
-    description: [One sentence — what does this skill do?]
-    input: [What does it receive? Type and format.]
-    output: [What does it return? Type and format.]
-    error_handling: [What does it do when input is invalid or ambiguous?]
-
-  - name: [second_skill_name]
-    description: [One sentence]
-    input: [Type and format]
-    output: [Type and format]
-    error_handling: [What does it do when input is invalid or ambiguous?]
+  - name: load_dataset
+    description: Reads the budget CSV, validates required columns, and identifies all rows with null actual_spend values.
+    input: Path to `ward_budget.csv`.
+    output: A collection of data records with pre-flagged null values and associated notes.
+    error_handling: Stop and warn if critical columns (period, ward, category) are missing or malformed.
+
+  - name: compute_growth
+    description: Calculates period-over-period growth (MoM/YoY) for a filtered subset of the data, ensuring formula transparency.
+    input: Filter parameters (ward name, category name, growth type).
+    output: A table showing each period, the actual spend, the growth percentage, and the underlying calculation formula.
+    error_handling: If the previous period's value is 0 or null, return 'N/A' for growth and specify the reason in the notes/formula column.
