---
name: budget-analysis-skills
description: Skills for the Number That Looks Right use case — per-ward per-category budget growth computation
skills:
  - name: load-dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning
    file: .opencode/skills/load_dataset/SKILL.md
  - name: compute-growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown
    file: .opencode/skills/compute_growth/SKILL.md
