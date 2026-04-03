\# Skills: Budget Growth Computation



\## 1. Filtering

Filter dataset by:

\- ward

\- category



\## 2. Sorting

Sort by period (YYYY-MM)



\## 3. Null Handling

\- If `actual\_spend` is null → skip row OR mark growth as NA

\- Never treat null as 0



\## 4. Growth Formula

Growth = (current\_month - previous\_month) / previous\_month



\## 5. Edge Cases

\- First month → growth = NA

\- Previous month null → growth = NA



\## 6. Output Rules

\- Maintain per-month rows

\- Do not collapse into a single value

\- Preserve original data

