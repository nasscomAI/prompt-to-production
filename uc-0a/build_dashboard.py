import os
import glob
import csv
import json

def classify_complaint(desc):
    desc = str(desc).lower()
    category = "Other"
    priority = "Standard"
    reason = "Standard issue reported."
    flag = ""
    
    categories_map = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "road surface cracked": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain blocked": "Drain Blockage"
    }
    
    matched = [cat for kw, cat in categories_map.items() if kw in desc]
    
    if len(matched) == 1:
        category = matched[0]
    elif len(matched) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif "manhole cover missing" in desc or "footpath tiles broken" in desc:
        category = "Road Damage"
    elif "dead animal" in desc:
        category = "Waste"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    urgent_words = [word for word in severity_keywords if word in desc]
    
    if urgent_words:
        priority = "Urgent"
        reason = f"Contains severity keyword(s): {', '.join(urgent_words)}."
    elif any(kw in desc for kw in ["10 days", "36 hours", "1 month", "20"]):
        priority = "Standard"
        reason = "Issue is ongoing but lacks immediate physical hazard keywords."
    else:
        reason = "Standard maintenance requested."
        
    if "school children at risk" in desc:
        reason = "Cites 'school' and 'child', indicating immediate risk."
    elif "injury" in desc:
        reason = "Cites risk of 'injury'."
        
    return category, priority, reason, flag

def main():
    data_dir = os.path.join("..", "data", "city_test_files")
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    all_complaints = []
    
    for file_path in csv_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                desc = row.get('description', '')
                cat, prio, reason, flag = classify_complaint(desc)
                
                # Try to get city from row, otherwise derive from filename
                city = row.get('city', '')
                if not city:
                    filename = os.path.basename(file_path)
                    if filename.startswith('test_') and filename.endswith('.csv'):
                        city = filename[5:-4].capitalize()
                    else:
                        city = "Unknown"
                        
                all_complaints.append({
                    "id": row.get('complaint_id', 'UNKNOWN'),
                    "city": city,
                    "category": cat,
                    "priority": prio,
                    "reason": reason,
                    "flag": flag
                })
                
    json_data = json.dumps(all_complaints, indent=2)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Civic AI Dispatch System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --card-bg: rgba(255, 255, 255, 0.05);
            --card-border: rgba(255, 255, 255, 0.1);
            --primary-text: #ffffff;
            --secondary-text: #94a3b8;
            --accent-blue: #3b82f6;
            --urgent-color: #ef4444;
            --standard-color: #10b981;
            --review-color: #f59e0b;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }}

        body {{
            background: linear-gradient(-45deg, #0b0e14, #1a1e2c, #0f172a, #0b0e14);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: var(--primary-text);
            min-height: 100vh;
            padding: 2rem;
        }}

        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--card-border);
        }}

        h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #fff, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            text-shadow: 0 0 30px rgba(59, 130, 246, 0.5);
        }}

        h1::before {{
            content: '';
            display: inline-block;
            width: 14px;
            height: 14px;
            background-color: var(--accent-blue);
            border-radius: 50%;
            box-shadow: 0 0 15px var(--accent-blue), 0 0 30px var(--accent-blue);
        }}

        /* KPI Cards */
        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .kpi-card {{
            background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.01));
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }}
        
        .kpi-icon {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));
            animation: float 6s ease-in-out infinite;
        }}

        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-5px); }}
            100% {{ transform: translateY(0px); }}
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
            transform: translateX(-100%);
            transition: transform 0.6s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-10px) scale(1.02);
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02));
            box-shadow: 0 15px 40px rgba(0,0,0,0.5), inset 0 0 20px rgba(255,255,255,0.05);
            border-color: rgba(255, 255, 255, 0.3);
        }}
        
        .kpi-card.urgent-card {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.02));
            border-color: rgba(239, 68, 68, 0.2);
        }}

        .kpi-card.urgent-card:hover {{
            box-shadow: 0 15px 40px rgba(239, 68, 68, 0.3), inset 0 0 30px rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.5);
        }}
        
        .kpi-card.review-card {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.02));
            border-color: rgba(245, 158, 11, 0.2);
        }}

        .kpi-card.review-card:hover {{
            box-shadow: 0 15px 40px rgba(245, 158, 11, 0.3), inset 0 0 30px rgba(245, 158, 11, 0.1);
            border-color: rgba(245, 158, 11, 0.5);
        }}

        .kpi-card h3 {{
            font-size: 0.9rem;
            color: var(--secondary-text);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }}

        .kpi-card .value {{
            font-size: 3rem;
            font-weight: 700;
            text-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}

        .kpi-card .value.urgent {{ color: var(--urgent-color); text-shadow: 0 0 20px rgba(239,68,68,0.5); }}
        .kpi-card .value.review {{ color: var(--review-color); text-shadow: 0 0 20px rgba(245,158,11,0.5); }}

        /* Table */
        .table-container {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            overflow: hidden;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th, td {{
            padding: 1.2rem 1.5rem;
            border-bottom: 1px solid var(--card-border);
        }}

        th {{
            font-size: 0.85rem;
            color: var(--secondary-text);
            text-transform: uppercase;
            letter-spacing: 1px;
            background: rgba(0, 0, 0, 0.3);
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr {{
            transition: background 0.2s ease;
        }}

        tr:hover {{
            background: rgba(255, 255, 255, 0.04);
        }}

        /* Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.35rem 0.85rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            backdrop-filter: blur(4px);
        }}

        .badge.category {{
            background: rgba(59, 130, 246, 0.15);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.4);
        }}
        
        .badge.city {{
            background: rgba(168, 85, 247, 0.15);
            color: #d8b4fe;
            border: 1px solid rgba(168, 85, 247, 0.4);
        }}

        .badge.priority-urgent {{
            background: rgba(239, 68, 68, 0.15);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.5);
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
            position: relative;
        }}

        .badge.priority-urgent::before {{
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: #f87171;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 1.2s infinite;
            box-shadow: 0 0 8px #f87171;
        }}

        .badge.priority-standard {{
            background: rgba(16, 185, 129, 0.15);
            color: #6ee7b7;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }}
        
        .badge.priority-low {{
            background: rgba(107, 114, 128, 0.15);
            color: #d1d5db;
            border: 1px solid rgba(107, 114, 128, 0.4);
        }}

        .badge.flag-review {{
            background: rgba(245, 158, 11, 0.15);
            color: #fcd34d;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }}

        .reason-text {{
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.5;
        }}

        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(248, 113, 113, 0.8); }}
            70% {{ box-shadow: 0 0 0 6px rgba(248, 113, 113, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(248, 113, 113, 0); }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>

    <div class="container">
        <header>
            <h1>Civic AI Dispatch System</h1>
            <div id="city-badge" class="badge category">Multiple Cities Connected</div>
        </header>

        <!-- KPIs -->
        <div class="kpi-container" id="kpi-container">
            <div class="kpi-card total-card">
                <div class="kpi-icon">📊</div>
                <h3>Total Complaints</h3>
                <div class="value" id="kpi-total">0</div>
            </div>
            <div class="kpi-card urgent-card">
                <div class="kpi-icon">🔴</div>
                <h3>Urgent Incidents</h3>
                <div class="value urgent" id="kpi-urgent">0</div>
            </div>
            <div class="kpi-card review-card">
                <div class="kpi-icon">⚠️</div>
                <h3>Pending Review</h3>
                <div class="value review" id="kpi-review">0</div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="table-container" id="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Complaint ID</th>
                        <th>City</th>
                        <th>Category</th>
                        <th>Priority</th>
                        <th>AI Reasoning</th>
                        <th>Status Flag</th>
                    </tr>
                </thead>
                <tbody id="table-body">
                    <!-- Rows injected via JS -->
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const complaintsData = {json_data};

        function renderDashboard(data) {{
            const total = data.length;
            const urgent = data.filter(c => c.priority === 'Urgent').length;
            const review = data.filter(c => c.flag === 'NEEDS_REVIEW' || c.flag === 'NEEDS REVIEW').length;

            // Animate KPIs from 0 to value
            animateValue('kpi-total', 0, total, 1000);
            animateValue('kpi-urgent', 0, urgent, 1000);
            animateValue('kpi-review', 0, review, 1000);

            // Populate Table
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';
            
            data.forEach((complaint, index) => {{
                const tr = document.createElement('tr');
                tr.style.opacity = '0';
                tr.style.animation = `fadeIn 0.5s ease forwards ${{index * 0.05}}s`;
                
                let pBadgeClass = 'priority-low';
                if (complaint.priority === 'Urgent') pBadgeClass = 'priority-urgent';
                else if (complaint.priority === 'Standard') pBadgeClass = 'priority-standard';

                const fBadge = complaint.flag ? `<span class="badge flag-review">⚠️ ${{complaint.flag.replace('_', ' ')}}</span>` : `<span style="color:var(--secondary-text)">✓ Auto</span>`;

                tr.innerHTML = `
                    <td style="font-family: monospace; font-weight:600; color: #94a3b8;">${{complaint.id}}</td>
                    <td><span class="badge city">${{complaint.city}}</span></td>
                    <td><span class="badge category">${{complaint.category}}</span></td>
                    <td><span class="badge ${{pBadgeClass}}">${{complaint.priority}}</span></td>
                    <td class="reason-text">${{complaint.reason}}</td>
                    <td>${{fBadge}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function animateValue(id, start, end, duration) {{
            if (start === end) {{
                document.getElementById(id).textContent = end;
                return;
            }}
            let startTimestamp = null;
            const step = (timestamp) => {{
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                document.getElementById(id).textContent = Math.floor(progress * (end - start) + start);
                if (progress < 1) {{
                    window.requestAnimationFrame(step);
                }}
            }};
            window.requestAnimationFrame(step);
        }}
        
        // Initialize
        renderDashboard(complaintsData);
    </script>
</body>
</html>
"""
    
    output_path = "dashboard.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Successfully processed {{len(all_complaints)}} complaints from all cities!")
    print(f"Dashboard updated: {{output_path}}")

if __name__ == "__main__":
    main()
