import json

def call_llm(system_prompt, user_input):
    """
    Simulates the AI call. Replace the return statement 
    with your actual workshop API call if provided.
    """
    # This matches the 'Printed Statement' expected during execution
    print(f"\n--- Calling LLM with CRAFT Prompt ---")
    
    # Example JSON response from the AI
    return '{"category": "Infrastructure", "priority": 4, "reason": "Pothole poses safety risk"}'

# CRAFT Framework Prompt
CRAFT_SYSTEM_PROMPT = """
CONTEXT: You are a city government administrative assistant.
ROLE: Act as a professional Complaint Classifier.
ACTION: Categorize the complaint and assign a priority score.
FORMAT: Return ONLY a valid JSON object with keys: "category", "priority", and "reason".
TARGET: Categories: [Infrastructure, Billing, Public Safety, Other]. Priority: 1-5.
"""

def run_classifier(complaint_text):
    print(f"Input received: {complaint_text}")
    
    # Get response from the simulated LLM
    response_text = call_llm(CRAFT_SYSTEM_PROMPT, complaint_text)
    
    try:
        data = json.loads(response_text)
        # EXACT PRINT STATEMENT FOR OUTPUT
        print(f"Result: {data['category']} (Priority: {data['priority']})")
        print(f"Reasoning: {data['reason']}")
        return data
    except json.JSONDecodeError:
        print("Error: Could not parse LLM response as JSON.")
        return None

if __name__ == "__main__":
    # Test Case
    sample_text = "There is a massive pothole on 5th Avenue causing traffic."
    run_classifier(sample_text)