# skills.md — UC-X Policy Concierge
 
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
+  - name: retrieve_documents
+    description: Loads and indexes all policy text files by name and section number for fast, accurate retrieval.
+    input: Directory path containing the .txt policy files.
+    output: An indexed collection of policy sections and document names.
+    error_handling: Raise an error if any of the three required policy files are missing.
+
+  - name: answer_question
+    description: Processes an employee query and generates a single-source response with citations or a standard refusal.
+    input: User natural language question and the indexed policy collection.
+    output: A precise answer string with [Filename SectionID] citation, or the verbatim refusal template.
+    error_handling: Enforce the 'anti-blending' rule; if multiple documents conflict or combine to an answer not present in either alone, the skill must trigger the refusal template.
