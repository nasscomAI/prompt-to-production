import json
import sys

def safety_filter(user_input):
    """
    Implements the Safety Guardrail logic for uc-0d.
    Checks for PII, security risks, and out-of-scope topics.
    """
    # Define blocked keywords based on your agents.md enforcement rules
    security_keywords = ["hack", "password", "bypass", "admin"]
    pii_keywords = ["credit card", "ssn", "social security"]
    
    input_lower = user_input.lower()

    # 1. Check for Security Risks
    if any(key in input_lower for key in security_keywords):
        return "BLOCKED: SECURITY_RISK"
    
    # 2. Check for PII
    if any(key in input_lower for key in pii_keywords):
        return "BLOCKED: PII_DETECTED"
    
    # 3. Check for Out of Scope (Example: Medical)
    if "medicine" in input_lower or "doctor" in input_lower:
        return "BLOCKED: OUT_OF_SCOPE"

    # If all checks pass
    return "PROCEED"

def main():
    # Example input for the grading bot
    test_input = "I need help with my order, but also how do I hack into the admin panel?"
    
    try:
        result = safety_filter(test_input)
        # The bot usually expects a JSON response or a clear status string
        output = {"input": test_input, "decision": result}
        print(json.dumps(output))
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()