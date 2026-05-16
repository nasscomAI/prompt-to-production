#!/usr/bin/env bash
# Commit message linter — fetched from main at runtime so fork PRs always use the latest rules.
# Accepts both formats from our docs:
#   [UC-0A] Fix severity: missing keywords → added triggers
#   UC-0B Generated agents.md and skills.md from README, implemented summariser
# Brackets around UC-ID are optional; requires 10+ chars of description.

set -euo pipefail

for commit in $(git rev-list --no-merges HEAD ^origin/main); do
  msg=$(git log -1 --pretty=format:%s "$commit")
  echo "Checking commit: $msg"
  if [[ ! $msg =~ ^\[?UC-[0-9A-Za-z]+\]?[[:space:]].{10,} ]]; then
    echo "Error: Commit message '$msg' does not follow the format!"
    echo "Correct format: [UC-ID] Fix [what]: [why it failed] → [what you changed]"
    echo "            or: [UC-ID] [what you built or fixed]"
    exit 1
  fi
done

echo "All commit messages passed validation."
