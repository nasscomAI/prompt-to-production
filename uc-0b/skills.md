skill: retrieve_policy
  input: file_path (str) — path to .txt policy file
  output: list of dicts [{clause_id: str, raw_text: str}]
  behaviour: splits file on numbered clause pattern (e.g. 2.3, 5.2), preserves all clauses in order

skill: summarize_policy
  input: sections (list of dicts), prompt (str)
  output: summary string
  behaviour: takes structured clauses, produces clause-by-clause summary,
  preserves clause numbers, keeps binding verbs exact, flags verbatim clauses
