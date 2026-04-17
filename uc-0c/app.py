print("UC-0C running")

data = [
    {"ward": "A", "amount": 100},
    {"ward": "B", "amount": 200},
    {"ward": "A", "amount": 150}
]

result = {}

for item in data:
    ward = item["ward"]
    amount = item["amount"]

    if ward not in result:
        result[ward] = 0
    result[ward] += amount

with open("growth_output.csv", "w") as f:
    for k, v in result.items():
        f.write(f"{k},{v}\n")

print("UC-0C done")
