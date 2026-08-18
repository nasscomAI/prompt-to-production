skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return its numbered clauses as structured sections.
    input: >
      input_path (str) to a UTF-8 policy .txt file such as
      policy_hr_leave.txt.
    output: >
      A dict with keys title_block (str, preamble lines before clause 1.1)
      and clauses (list of dicts). Each clause dict has id (str, e.g. "5.2"),
      text (str, full clause with wrapped lines joined), and section (str,
      nearest section heading if present).
    error_handling: >
      Missing file → raise FileNotFoundError.
      Empty file or no lines matching N.N clause ids → return clauses=[]
      so summarize_policy can refuse. Continuation lines are joined; section
      headings like "2. ANNUAL LEAVE" are not treated as clauses.

  - name: summarize_policy
    description: Turn structured numbered sections into a source-faithful summary with clause references.
    input: >
      The dict returned by retrieve_policy (title_block + clauses).
    output: >
      A UTF-8 string written to summary_hr_leave.txt. Each clause is one
      line starting with [id]. Inventory clauses and any clause that cannot
      be shortened without meaning loss are prefixed FLAG:VERBATIM and
      quoted from source text. Ends with a completeness line listing
      clause counts.
    error_handling: >
      Zero clauses → return a single refusal line; do not guess content.
      Never insert IT or Finance policy text. Never emit banned scope-bleed
      phrases.
