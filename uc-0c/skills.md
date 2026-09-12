# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates its columns, and reports the count and identity of every null actual_spend row before returning the data.
    input: >
      path (str): filesystem path to a UTF-8 CSV whose header contains
      exactly the columns period, ward, category, budgeted_amount,
      actual_spend, notes. period values are YYYY-MM strings.
    output: >
      A dict with keys:
      rows (list of dicts in file order, with budgeted_amount parsed to
      float, actual_spend parsed to float or None when blank, and all
      string columns stripped of surrounding whitespace),
      wards (sorted list of distinct ward strings),
      categories (sorted list of distinct category strings),
      periods (sorted list of distinct period strings),
      null_rows (list of dicts with period, ward, category, notes for
      every row whose actual_spend is None),
      null_count (int, equal to len(null_rows)).
      The null_rows list is printed to stderr as a NULL REPORT at load time
      so nulls are visible before any computation starts.
    error_handling: >
      If the file does not exist or cannot be decoded, raise a clear error
      naming the path. If any required column is missing or an unexpected
      column is present, raise an error listing the actual header; do not
      guess column meanings by position. If budgeted_amount is blank or
      non-numeric on any row, raise an error naming the row, because the
      dataset guarantees it is always present. If actual_spend is non-blank
      but non-numeric, raise an error naming the row rather than treating
      it as null. If a period is not of the form YYYY-MM, raise an error.
      A blank actual_spend is NOT an error; it becomes None and is added
      to null_rows. Blank notes on a null row are reported as
      'no reason given in notes'.

  - name: compute_growth
    description: Takes one ward, one category, and an explicit growth type, and returns a per-period table where every row shows the numbers used, the formula applied, the growth, and a status.
    input: >
      dataset (dict): the structure returned by load_dataset.
      ward (str): exact ward string as it appears in the file.
      category (str): exact category string as it appears in the file.
      growth_type (str): exactly "MoM" or "YoY"; no default.
    output: >
      A list of dicts, one per period in ascending order, each with keys:
      period, ward, category, budgeted_amount, actual_spend,
      prior_period, prior_actual, formula, growth_pct, status, notes.
      growth_pct is a float rounded to 1 decimal or an empty string.
      status is one of: OK, NULL, NO_PRIOR, PRIOR_NULL, NO_PRIOR_YEAR,
      DIV_ZERO. formula always holds the substituted expression, such as
      "(19.7 - 14.8) / 14.8 * 100", or a plain-language reason when growth
      is not computed. Rows are scoped to exactly one ward and one category
      and no aggregate row is ever appended.
    error_handling: >
      If ward or category is empty, None, or a wildcard word such as all,
      total, or *, raise a refusal error naming the missing scope; never
      aggregate. If ward or category does not exactly match a value in the
      dataset, raise an error listing the valid values from the file. If
      growth_type is missing, empty, or not MoM/YoY, raise a refusal error
      listing the two valid options; never default. If the scoped subset has
      zero rows, raise an error. For MoM, the prior period is the previous
      calendar month; for YoY it is the same month one year earlier. If the
      prior period is not present in the dataset, status is NO_PRIOR (MoM)
      or NO_PRIOR_YEAR (YoY) and growth is blank. If the current row's
      actual_spend is None, status is NULL, growth is blank, and notes
      carries the reason. If the prior row's actual_spend is None, status is
      PRIOR_NULL and the formula names the null period. If the prior value
      is 0, status is DIV_ZERO. Under no condition is a null replaced by 0,
      the budgeted amount, or a neighbouring value.
