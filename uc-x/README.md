# UC-X - Smart City Route Recommendation

This agent recommends a route only from supplied route candidates and verified traffic or civic evidence. It does not invent live traffic, closures, incidents, or routes.

## Natural-language request

```powershell
python app.py --text "Find a route from Vellore to Katpadi"
```

Without verified route data, the result explicitly reports that live traffic information is unavailable.

## Explicit locations

```powershell
python app.py --origin "Vellore" --destination "Katpadi" --traffic "heavy traffic on Main Road" --civic-reports "flooding reported on Main Road"
```

## Supplied route candidates

Use a JSON file containing route objects, for example:

```json
[
  {"name": "Main Road", "duration_minutes": 20, "evidence": "heavy traffic and flooding reported"},
  {"name": "East Bypass", "duration_minutes": 28, "evidence": "normal traffic"}
]
```

Run it with:

```powershell
python app.py --origin "Vellore" --destination "Katpadi" --routes-file routes.json
```

Required output fields are `Origin`, `Destination`, `Recommended Route`, `Condition`, `Reason`, and `Traffic Data`.
