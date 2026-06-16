---
name: policy-summarizer-skills
description: Skills for the Summary That Changes Meaning use case — complete clause preservation
skills:
  - name: retrieve-policy
    description: Loads .txt policy file, returns content as structured numbered sections
    file: .opencode/skills/retrieve_policy/SKILL.md
  - name: summarize-policy
    description: Takes structured sections, produces compliant summary with clause references
    file: .opencode/skills/summarize_policy/SKILL.md
