# Skills

## load_dataset

Input:

* Budget CSV

Output:

* Validated dataset

Responsibilities:

* Check required columns.
* Report null values.
* Return cleaned records.

---

## compute_growth

Input:

* Ward
* Category
* Growth Type

Output:

* Per-period growth table

Rules:

* Never aggregate all wards.
* Skip null values.
* Show the formula used for each row.