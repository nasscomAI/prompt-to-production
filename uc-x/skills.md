# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three policy documents and indexes each by document name and section number.
    input: Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A dict mapping each document name to a list of (section_number, section_text) tuples in file order.
    error_handling: Raises FileNotFoundError when a policy document is missing; refuses to run otherwise.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a document + section citation, or the exact refusal template verbatim.
    input: A question string and the index returned by retrieve_documents.
    output: "policy_<name>.txt section <number>\n\n<verbatim section text>" for covered questions, otherwise the exact refusal template with no variations.
    error_handling: Never blends two documents; returns the refusal template when the question has no anchor topic in any document, the best match is below the coverage threshold without topic-heading confirmation, or answering would require combining documents.

  - name: analyze_complaints
    description: Reads a complaint CSV and writes a per-row classification CSV with category, priority, reason, and flag for every complaint.
    input: Path to a test_<city>.csv with a description column; optional output path (defaults to result_<city>.csv in the current folder).
    output: CSV with columns complaint_id, category, priority, reason, flag; category is drawn from the complaint taxonomy (Flooding, Drainage, Pothole, Road Damage, Heat Hazard, Tree Hazard, Waste, Streetlight, Noise, Heritage Damage, Infrastructure) and priority from severity keywords (Urgent/Standard/Low).
    error_handling: Rows whose description matches no category, or has no description, are flagged NEEDS_REVIEW instead of guessed; the reason always names the matched keyword or states why the row needs review.
