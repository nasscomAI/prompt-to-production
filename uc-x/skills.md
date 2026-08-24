# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads the three CMC policy files and indexes every numbered section by document filename and section number so any passage can be retrieved and cited exactly.
    input: None — fixed corpus paths ../data/policy-documents/policy_hr_leave.txt, ../data/policy-documents/policy_it_acceptable_use.txt, ../data/policy-documents/policy_finance_reimbursement.txt (UTF-8 plain text with N.M-numbered sections under numbered headings).
    output: An index mapping each document filename to its sections (section id "N.M" to verbatim section text), plus the loaded filename list used to build citations of the form (policy_<name>.txt, section N.M).
    error_handling: A missing, unreadable, or empty file aborts with a clear error naming the file — the system never answers from a partial corpus; a file that yields zero parseable numbered sections is a load failure, not silently skipped.

  - name: answer_question
    description: Scores one employee question against the section index and returns either a single-document verbatim answer with its citation, or the fixed refusal template — never a blend, never a hedge.
    input: One free-text question string typed at the interactive prompt, e.g. "Who approves leave without pay?".
    output: An answer block quoting policy text VERBATIM from exactly ONE document followed by its citation (policy_<name>.txt, section N.M), with every numeric limit, deadline, eligible group, and ALL required approvers preserved — OR the refusal template from agents.md with [relevant team] resolved deterministically to HR Department, IT Helpdesk, or Finance Department.
    error_handling: Empty or blank input is re-prompted, never answered; if no section reaches the evidence threshold, or the runner-up document scores ≥ 75% of the leader (cross-document ambiguity), the refusal template is issued instead of guessing; any drafted output containing a banned hedging phrase is discarded and replaced by the refusal template; unknown terms never draw on outside knowledge.
