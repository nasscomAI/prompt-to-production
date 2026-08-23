\# skills.md — UC-X Ask My Documents



skills:

&#x20; - name: retrieve\_documents

&#x20;   description: Loads all three policy documents and creates an indexed structure by document name and section number for quick lookup.

&#x20;   input: List of file paths to the three policy documents

&#x20;   output: A dictionary with document names as keys, containing structured sections with section numbers and text

&#x20;   error\_handling: If any document is missing, raise clear error listing which ones. Log loaded sections per document.



&#x20; - name: answer\_question

&#x20;   description: Searches the indexed documents for the user's question and returns an answer from a SINGLE document with citation, OR the exact refusal template if not found.

&#x20;   input: 

&#x20;     - question (string) - user's question

&#x20;     - documents (dict) - indexed policy documents

&#x20;   output: A string containing the answer with document name + section citation, OR the exact refusal template

&#x20;   error\_handling: 

&#x20;     - If question matches multiple documents, return answer from the most relevant SINGLE document (do NOT blend)

&#x20;     - If question not found in any document, return refusal template exactly

&#x20;     - Never use hedging language

