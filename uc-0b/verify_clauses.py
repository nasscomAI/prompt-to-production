"""Detailed clause verification for UC-0B."""
clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
with open("summary_hr_leave.txt", "r", encoding="utf-8") as f:
    content = f.read()

print("CRITICAL CLAUSE CHECK:")
for c in clauses:
    status = "PASS" if c in content else "FAIL"
    print(f"  Clause {c}: {status}")

print()
print("MULTI-CONDITION CHECK (Clause 5.2):")
print(f"  Department Head: {'PASS' if 'Department Head' in content else 'FAIL'}")
print(f"  HR Director: {'PASS' if 'HR Director' in content else 'FAIL'}")
print(f"  AND condition: {'PASS' if 'Department Head and' in content else 'FAIL'}")

print()
print("SCOPE BLEED CHECK:")
bleed_phrases = ["as is standard practice", "typically in government", "employees are generally expected to"]
for p in bleed_phrases:
    status = "PASS" if p not in content.lower() else "FAIL"
    print(f"  '{p}': {status}")

print()
print("VERBATIM FLAG:", "PASS" if "[VERBATIM]" in content else "FAIL")
