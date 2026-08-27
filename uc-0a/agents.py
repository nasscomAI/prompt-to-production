import re

class ComplaintAgent:
    def __init__(self):
        self.categories = [
            "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
            "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
        ]
        self.priority_keywords = [
            "injury", "child", "school", "hospital", "ambulance", 
            "fire", "hazard", "fell", "collapse"
        ]

    def classify(self, description):
        """
        Simulates an LLM classification based on RICE rules.
        In a real production environment, this would call an LLM API.
        """
        desc_lower = description.lower()
        
        # Determine Category
        category = "Other"
        if "pothole" in desc_lower:
            category = "Pothole"
        elif "flood" in desc_lower or "water logging" in desc_lower:
            category = "Flooding"
        elif "light" in desc_lower:
            category = "Streetlight"
        elif "garbage" in desc_lower or "waste" in desc_lower:
            category = "Waste"
        elif "noise" in desc_lower or "music" in desc_lower:
            category = "Noise"
        elif "crack" in desc_lower or "surface" in desc_lower:
            category = "Road Damage"
        elif "heritage" in desc_lower or "temple" in desc_lower or "statue" in desc_lower:
            category = "Heritage Damage"
        elif "heat" in desc_lower or "sun" in desc_lower:
            category = "Heat Hazard"
        elif "drain" in desc_lower:
            category = "Drain Blockage"

        # Determine Priority
        priority = "Standard"
        urgent_reason = ""
        for word in self.priority_keywords:
            if word in desc_lower:
                priority = "Urgent"
                urgent_reason = f"Keyword '{word}' found in description."
                break
        
        if priority == "Standard" and ("urgent" in desc_lower or "immediate" in desc_lower):
            priority = "Urgent"
            urgent_reason = "Urgency implied in text."

        # Reason Generation (Simulated)
        reason = f"Classified as {category} based on keywords in description. {urgent_reason}".strip()
        
        # Ambiguity Flag
        flag = ""
        if category == "Other":
            flag = "NEEDS_REVIEW"

        return {
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }
