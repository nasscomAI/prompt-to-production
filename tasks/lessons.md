# Centralized Lessons Registry

- **Argparse Hyphen Conversion**: When using `argparse` with flags containing hyphens (e.g. `--growth-type`), `argparse` automatically translates the hyphen to an underscore in the parsed arguments namespace (e.g. `args.growth_type`). Attempting to use `args.growth-type` results in a python syntax error.
- **Artifact Directory Boundaries**: Always make sure artifact files (such as `implementation_plan.md`, `task.md`, `walkthrough.md`) are written strictly under the designated brain folder (`C:\Users\2016tu\.gemini\antigravity-ide\brain\<conversation-id>\`) and NOT in the workspace root.
