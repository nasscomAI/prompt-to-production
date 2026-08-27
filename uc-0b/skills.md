# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections keyed by clause number.
    input: file_path (str) pointing to a .txt policy document.
    output: A dict mapping clause numbers (e.g. '2.3', '5.2') to their full text as read from the file.
    error_handling: If the file is missing or unreadable, raise an error identifying the file path and halt — do not proceed with partial data.

  - name: summarize_policy
    description: Takes the structured clause dict from retrieve_policy and produces a compliant summary that preserves every clause, all multi-condition obligations, and all binding verbs.
    input: A dict of clause numbers to clause text (output of retrieve_policy), and the source document name (str).
    output: A plain-text summary where every numbered clause appears, multi-condition obligations are fully preserved, and each summary line cites its clause number.
    error_handling: If a clause cannot be summarised without meaning loss (e.g. multi-condition approval chains), quote it verbatim and append [VERBATIM — conditions preserved] rather than paraphrasing.
