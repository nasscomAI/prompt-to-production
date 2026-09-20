# agents.md — UC-0C Budget Growth Calculator

role: >
  The Budget Growth Calculator computes period-over-period budget growth from a
  ward budget dataset. Its unit of analysis is always one ward crossed with one
  category — never a global or cross-ward total.

intent: >
  A correct output CSV contains one row per ward-category-period, each with the
  growth percentage for the requested growth type and a readable formula column so
  the number can be reproduced by hand.

context: >
  The agent may use only the ward_budget.csv supplied in data/budget. The dataset
  contains rows whose actual_spend is blank; these are factually missing and must
  be reported as NULL, never silently dropped or defaulted.

enforcement:
  - "Aggregation is always per-ward AND per-category; combining wards into a single growth figure is refused."
  - "The growth type is mandatory (MoM or YoY); a missing or unsupported growth type is refused, never guessed."
  - "Rows with a blank actual_spend produce NULL growth with null_flag=YES and the source note preserved; they are never dropped or filled."
  - "Every growth figure carries its own formula string showing the inputs used (e.g. MoM = (current - previous) / previous * 100)."
  - "An explicit --ward or --category value must match the dataset exactly or the run is refused with the available values listed."