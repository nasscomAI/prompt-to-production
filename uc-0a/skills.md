# notepad uc-0a\\skills.md

# ```

# 

# Then \*\*Ctrl+A → Delete\*\* and paste this:

# ```

# \# UC-0A — Classifier Skills

# 

# \## Skill: extract\_category

# \- Read the complaint text carefully

# \- Match to exactly ONE of the 9 allowed categories

# \- If multiple categories fit, pick the most prominent issue

# \- Never create a new category

# 

# \## Skill: assign\_severity

# \- Scan for URGENT trigger keywords first

# \- If any trigger word is present → URGENT, regardless of tone

# \- If no trigger word → assess disruption level → HIGH / MEDIUM / LOW

# \- Tone alone (angry, frustrated) does NOT make something URGENT

# 

# \## Skill: format\_output

# \- Output exactly one CSV row

# \- Format: complaint\_id,complaint\_text,category,severity,department

# \- No headers, no explanation, no extra lines

# \- Wrap complaint\_text in quotes if it contains commas

# 

# \## Skill: handle\_ambiguity

# \- If category is unclear → Other

# \- If severity is unclear → LOW

# \- Never leave a field blank

