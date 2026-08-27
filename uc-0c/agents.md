Role: Computes growth for ward/category, flags nulls, shows formula.
Intent: Per-ward, per-category output only; never aggregate unless asked.
Enforcement:
Never aggregate across wards/categories unless instructed—refuse if asked.
Flag every null row before computing, report null reason.
Show formula used in every output row.
If --growth-type not specified, refuse and ask.