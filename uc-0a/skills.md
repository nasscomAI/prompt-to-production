\# Skills for Complaint Classification Agent



text\_processing:

\- Convert complaint text to lowercase

\- Remove unnecessary punctuation

\- Extract important words from the complaint description



keyword\_detection:

\- Detect keywords related to civic issues



Examples:

pothole → road damage

flood → flooding issue

garbage → sanitation issue

water → water supply issue

electricity → power issue



priority\_detection:

\- If the complaint description contains words like

&#x20; injury, child, school, hospital

&#x20; then priority must be set to "Urgent"



classification:

\- Map detected keywords to the allowed categories:

&#x20; Pothole

&#x20; Flooding

&#x20; Garbage

&#x20; Water

&#x20; Electricity

&#x20; Other



uncertainty\_handling:

\- If no clear category can be determined

&#x20; category = Other

&#x20; flag = NEEDS\_REVIEW

