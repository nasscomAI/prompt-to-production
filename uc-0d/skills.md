# Skills Specification: UC-0D Civic Budget Allocation

## 1. get_ward_balance
- **Description**: Returns the real-time available budget in INR for a specified ward ID.
- **Input**: `ward_id: str`
- **Output**: `{"ward_id": str, "balance_inr": float}`

## 2. verify_signoff
- **Description**: Validates whether the provided list of approver IDs meets the mandatory threshold requirements for the requested amount.
- **Input**: `approver_ids: list[str]`, `amount: float`
- **Output**: `{"valid": bool, "status": str, "missing": list[str]}`

## 3. commit_expenditure
- **Description**: Deducts the approved amount from the active ward balance and logs transaction.
- **Input**: `project_id: str`, `ward_id: str`, `amount: float`
- **Output**: `{"status": "COMMITTED", "remaining_balance": float}`
