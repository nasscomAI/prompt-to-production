# UC-0C — Number That Looks Right · skills.md

## Skill: read_budget_csv

### Purpose
Read `ward_budget.csv` and return list of budget rows.

```python
read_budget_csv(filepath: str) -> list[dict]
```

---

## Skill: compute_growth

### Purpose
Compute growth % for a single row (one ward, one category).

```python
compute_growth(previous_year: float, current_year: float) -> tuple[str, str]
# Returns: (growth_pct_str, direction)
```

### Formula
```
growth_pct = ((current_year - previous_year) / previous_year) * 100
```

### Rules
- Scope: **one row at a time** — never aggregate first
- If `previous_year == 0`: return `("DIV_ZERO", "DIV_ZERO")`
- If growth > 0: direction = "UP"
- If growth < 0: direction = "DOWN"
- If growth == 0: direction = "FLAT"
- Round to 2 decimal places

---

## Skill: write_growth_csv

### Purpose
Write growth results to `growth_output.csv`.

```python
write_growth_csv(filepath: str, results: list[dict])
```

---

## CRAFT Notes
- **C**ontext: Municipal ward budget data, Hyderabad
- **R**ole: Precise per-row growth calculator
- **A**ction: Read → compute per-row → write
- **F**ormat: CSV in, CSV out
- **T**one: No rounding errors, no silent aggregation

## Anti-Pattern (what NOT to do)
```python
# WRONG — aggregates before computing
total_prev = sum(row['previous_year'] for row in rows)
total_curr = sum(row['current_year'] for row in rows)
growth = (total_curr - total_prev) / total_prev  # ← silent aggregation error

# CORRECT — per row
for row in rows:
    growth = compute_growth(row['previous_year'], row['current_year'])
```
