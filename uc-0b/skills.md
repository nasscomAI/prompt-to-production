# skills.md — UC-0B Policy Summarizer
 
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
+  - name: retrieve_policy
+    description: Loads a policy text file and parses it into structured numbered sections for precise analysis.
+    input: Path to the .txt policy document.
+    output: A collection of clauses, each with a Clause ID and its associated text.
+    error_handling: Raise an error if the file is missing or contains no recognizable numbered clauses.
+
+  - name: summarize_policy
+    description: Converts structured clauses into a high-fidelity summary adhering to strict condition preservation rules.
+    input: Collection of structured clauses.
+    output: A text summary where every clause is accounted for, conditions are preserved, and unsummarizable parts are quoted.
+    error_handling: If a multi-condition clause cannot be summarized without dropping a condition, the skill must default to verbatim quotation.
