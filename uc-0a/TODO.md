# UC-0A Implementation TODO

## Classifier.py Update Plan (detailed breakdown)
## Information Gathered from agents.md & skills.md
## - Categories exactly as listed
## - Priority Urgent only on severity keywords
## - Flag only for ambiguity/invalid
## Current TODO status incorporated.

- [x] Previous Step 4: Minor fixes done
- [x] Step 4.1: Refine category matching - count keywords per cat, pick max count, tie -> Other + flag
- [x] Step 4.2: Priority: Urgent *only* if severity keyword present, else Low (remove extra Standard triggers)
- [x] Step 4.3: Flag 'NEEDS_REVIEW' precisely for ties/empty desc/error; reason one sentence citing specifics
- [x] Step 4.4: Add classify_complaint docstring matching skills.md
- [x] Step 4.5: Test CLI on test_hyderabad.csv, verify results vs spec
- [ ] Step 4.6: Mark completion in TODO.md

## Planned Steps (from approved plan)
- [x] Step 1: Create this TODO.md
- [x] Step 2: Update skills.md with concrete skill definitions
- [x] Step 3: Update agents.md with RICE agent definition
- [ ] Step 4: Classifier.py updates (detailed above)
- [x] Step 5: Test classifier.py on test_hyderabad.csv and verify output CSV
- [x] Step 6: Update TODO.md with completion marks
- [ ] Step 7: Commit changes with UC-0A format
