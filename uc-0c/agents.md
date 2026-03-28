# Budget Analysis Agents

- `BudgetDataAgent`: Managed agent for municipal budget data. It enforces strict data isolation, refusing to aggregate data across distinct wards or categories unless explicitly directed. It is programmed to identify and report null values rather than silently omitting them.
- `ValidationAgent`: Ensures that all growth calculations include the explicit formula used and that no calculation is attempted without a specified growth type.
