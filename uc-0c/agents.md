role: >
  draws a hard operational boundary. It names what the agent is (single-ward, single-category analyst), what it cannot do (aggregate without explicit instruction), and its posture toward ambiguity (refuses rather than infers). This stops the agent from silently expanding scope.
intent: >
  makes correctness testable. It specifies the exact shape of a correct output (12 rows, 7 columns, what each cell must contain), so you can write a passing/failing test against it without re-reading the code. Vague intents like "compute growth" leave too much room for the agent to return something that "looks right" but violates the null or formula rules.
context: >
  lists what data is in and what is out. Explicitly excluding interpolated values and external sources prevents the most common silent failure: filling a null with a prior value or a zero and computing growth on it anyway.
enforcement: >
  four rules, each independently testable with a single input case. Each rule names the condition, the required output ([REFUSED], NOT COMPUTED, a formula string), and what the wrong behaviour looks like implicitly (aggregating, skipping nulls, empty formula column, defaulting growth type).