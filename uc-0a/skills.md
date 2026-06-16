---
name: complaint-classifier-skills
description: Skills for the Complaint Classifier use case — taxonomy-enforced complaint classification
skills:
  - name: classify-complaint
    description: One complaint row in → category + priority + reason + flag out
    file: .opencode/skills/classify_complaint/SKILL.md
  - name: batch-classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV
    file: .opencode/skills/batch_classify/SKILL.md
