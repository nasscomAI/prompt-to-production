    output: A plain-text summary file containing each required clause either
      paraphrased safely or quoted verbatim with `QUOTED:` prefix.
    processing: For each required clause, attempt a minimal paraphrase that
      preserves binding verbs and all conditions; if paraphrase would drop
      conditions, include verbatim with `QUOTED:` marker.
    validation: Ensure the output contains entries for clauses 2.3,2.4,2.5,2.6,
      2.7,3.2,3.4,5.2,5.3,7.2.
    failure_behavior: If any required clause is missing, fail with non-zero exit
      code and write a diagnostic file.
