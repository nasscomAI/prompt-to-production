if "pothole" in text:
    category = "Pothole"
    reason = "Found word 'pothole' in complaint"

elif "flood" in text or "waterlogging" in text:
    category = "Flooding"
    reason = "Found word 'flood' or 'waterlogging'"

elif "streetlight" in text or "light" in text:
    category = "Streetlight"
    reason = "Found issue related to 'streetlight/light'"

elif "garbage" in text or "waste" in text or "trash" in text:
    category = "Waste"
    reason = "Found word 'garbage/waste/trash'"

elif "noise" in text or "loud" in text:
    category = "Noise"
    reason = "Found word 'noise/loud'"

elif "road damage" in text or "damaged road" in text or "road broken" in text:
    category = "Road Damage"
    reason = "Found word 'road damage/broken road'"

elif "heritage" in text:
    category = "Heritage Damage"
    reason = "Found word 'heritage'"

elif "heat" in text:
    category = "Heat Hazard"
    reason = "Found word 'heat'"

elif "drain" in text or "blockage" in text:
    category = "Drain Blockage"
    reason = "Found word 'drain/blockage'"

else:
    category = "Other"
    reason = "No matching category keyword found"
    flag = "NEEDS_REVIEW"