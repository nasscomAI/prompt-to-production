import os
import glob
import csv
import json
from classifier import classify_complaint

def main():
    # Gather files from both city_test_files and city-test-files directories
    data_dirs = [
        os.path.join("..", "data", "city_test_files"),
        os.path.join("..", "data", "city-test-files")
    ]
    
    csv_files = []
    for d in data_dirs:
        if os.path.exists(d):
            csv_files.extend(glob.glob(os.path.join(d, "test_*.csv")))
            csv_files.extend(glob.glob(os.path.join(d, "*.csv")))
            
    # Resolve absolute paths and remove duplicates
    csv_files = sorted(list(set(os.path.abspath(f) for f in csv_files)))
    
    all_complaints = []
    processed_files = []
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        # Skip results files or non-test files
        if filename.startswith("results_") or not filename.endswith(".csv"):
            continue
            
        processed_files.append(filename)
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                except Exception as e:
                    # Fallback classification in case of parser error
                    classified = {
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error parsing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    }
                
                # Derive city from row or filename
                city = row.get('city', '')
                if not city:
                    if filename.startswith('test_'):
                        city = filename[5:-4].capitalize()
                    else:
                        city = filename[:-4].capitalize()
                
                all_complaints.append({
                    "id": classified.get("complaint_id", "UNKNOWN"),
                    "city": city,
                    "category": classified.get("category", "Other"),
                    "priority": classified.get("priority", "Standard"),
                    "reason": classified.get("reason", "No reason provided."),
                    "flag": classified.get("flag", ""),
                    "date_raised": row.get("date_raised", ""),
                    "ward": row.get("ward", ""),
                    "location": row.get("location", ""),
                    "description": row.get("description", ""),
                    "reported_by": row.get("reported_by", ""),
                    "days_open": row.get("days_open", "")
                })

    print(f"Successfully processed {len(all_complaints)} complaints from {len(processed_files)} files: {processed_files}")
    json_data = json.dumps(all_complaints, indent=2)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Civic AI Dispatch System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: rgba(17, 24, 39, 0.6);
            --card-border: rgba(255, 255, 255, 0.08);
            --primary-text: #f3f4f6;
            --secondary-text: #9ca3af;
            --accent-blue: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.3);
            --urgent-color: #ef4444;
            --urgent-glow: rgba(239, 68, 68, 0.3);
            --standard-color: #10b981;
            --standard-glow: rgba(16, 185, 129, 0.3);
            --review-color: #f59e0b;
            --review-glow: rgba(245, 158, 11, 0.3);
            --low-color: #6b7280;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }}

        body {{
            background: linear-gradient(135deg, #070a13 0%, #0f172a 40%, #1e1b4b 100%);
            color: var(--primary-text);
            min-height: 100vh;
            padding: 2rem;
            overflow-x: hidden;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header Styling */
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--card-border);
        }}

        .header-left {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }}

        h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #ffffff, #93c5fd, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            text-shadow: 0 0 30px rgba(59, 130, 246, 0.2);
        }}

        h1::before {{
            content: '';
            display: inline-block;
            width: 14px;
            height: 14px;
            background-color: var(--accent-blue);
            border-radius: 50%;
            box-shadow: 0 0 15px var(--accent-blue), 0 0 30px var(--accent-blue);
            animation: pulse 2s infinite;
        }}

        .glass-select {{
            background: rgba(17, 24, 39, 0.8);
            border: 1px solid var(--card-border);
            color: var(--primary-text);
            padding: 0.6rem 1.5rem;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            outline: none;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}

        .glass-select:hover, .glass-select:focus {{
            border-color: var(--accent-blue);
            box-shadow: 0 0 15px var(--accent-glow);
        }}

        .glass-select option {{
            background: #0f172a;
            color: var(--primary-text);
        }}

        /* KPI Layout */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .kpi-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 1.8rem;
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .kpi-card:hover {{
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
        }}

        .kpi-card.total {{ border-left: 4px solid var(--accent-blue); }}
        .kpi-card.urgent {{ border-left: 4px solid var(--urgent-color); }}
        .kpi-card.review {{ border-left: 4px solid var(--review-color); }}

        .kpi-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.8rem;
        }}

        .kpi-title {{
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--secondary-text);
            font-weight: 600;
        }}

        .kpi-icon {{
            font-size: 1.8rem;
            opacity: 0.8;
        }}

        .kpi-value {{
            font-size: 2.8rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.5rem;
        }}

        .kpi-value.blue {{ color: #60a5fa; text-shadow: 0 0 15px rgba(96, 165, 250, 0.3); }}
        .kpi-value.red {{ color: var(--urgent-color); text-shadow: 0 0 15px var(--urgent-glow); }}
        .kpi-value.amber {{ color: var(--review-color); text-shadow: 0 0 15px var(--review-glow); }}

        .kpi-subtext {{
            font-size: 0.8rem;
            color: var(--secondary-text);
        }}

        /* City Criticality Index Card */
        .criticality-index-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 1.8rem;
            margin-bottom: 2rem;
            backdrop-filter: blur(20px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        }}

        .section-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1.2rem;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 0.8rem;
        }}

        .city-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1.2rem;
        }}

        .city-card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 1rem;
            transition: all 0.3s ease;
        }}

        .city-card:hover {{
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.15);
        }}

        .city-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.8rem;
        }}

        .city-name {{
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--primary-text);
        }}

        .city-total-badge {{
            font-size: 0.75rem;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.1);
            padding: 0.2rem 0.5rem;
            border-radius: 8px;
        }}

        /* Segmented Progress Bar */
        .stacked-bar {{
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            display: flex;
            background: rgba(255, 255, 255, 0.05);
            margin-bottom: 0.8rem;
        }}

        .bar-segment {{
            height: 100%;
            transition: width 0.5s ease;
        }}

        .bar-segment.urgent {{ background-color: var(--urgent-color); box-shadow: 0 0 8px var(--urgent-glow); }}
        .bar-segment.review {{ background-color: var(--review-color); box-shadow: 0 0 8px var(--review-glow); }}
        .bar-segment.standard {{ background-color: var(--standard-color); box-shadow: 0 0 8px var(--standard-glow); }}
        .bar-segment.low {{ background-color: var(--low-color); }}

        .city-stats-legend {{
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--secondary-text);
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }}

        .dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
        }}
        .dot.urgent {{ background-color: var(--urgent-color); }}
        .dot.review {{ background-color: var(--review-color); }}
        .dot.standard {{ background-color: var(--standard-color); }}
        .dot.low {{ background-color: var(--low-color); }}

        /* Filter Controls */
        .controls-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(20px);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }}

        .filter-group {{
            display: flex;
            align-items: center;
            gap: 0.8rem;
            flex-wrap: wrap;
        }}

        .search-wrapper {{
            position: relative;
            min-width: 280px;
        }}

        .search-input {{
            width: 100%;
            background: rgba(17, 24, 39, 0.8);
            border: 1px solid var(--card-border);
            color: var(--primary-text);
            padding: 0.6rem 1rem 0.6rem 2.5rem;
            border-radius: 12px;
            outline: none;
            transition: all 0.3s ease;
        }}

        .search-input:focus {{
            border-color: var(--accent-blue);
            box-shadow: 0 0 15px var(--accent-glow);
        }}

        .search-icon {{
            position: absolute;
            left: 0.9rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--secondary-text);
            font-size: 0.95rem;
            pointer-events: none;
        }}

        .pill-filters {{
            display: flex;
            gap: 0.5rem;
        }}

        .pill-btn {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--secondary-text);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .pill-btn:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--primary-text);
        }}

        .pill-btn.active {{
            background: var(--accent-blue);
            color: white;
            border-color: var(--accent-blue);
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.4);
        }}

        /* Table Design */
        .table-container {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            overflow: hidden;
            backdrop-filter: blur(20px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            margin-bottom: 1.5rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th, td {{
            padding: 1.1rem 1.4rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        th {{
            font-size: 0.8rem;
            color: var(--secondary-text);
            text-transform: uppercase;
            letter-spacing: 1px;
            background: rgba(0, 0, 0, 0.2);
            font-weight: 600;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr.complaint-row {{
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        tr.complaint-row:hover {{
            background: rgba(255, 255, 255, 0.03);
            transform: scale(1.002);
        }}

        /* Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.3rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}

        .badge.city {{
            background: rgba(168, 85, 247, 0.12);
            color: #d8b4fe;
            border: 1px solid rgba(168, 85, 247, 0.3);
        }}

        .badge.category {{
            background: rgba(59, 130, 246, 0.12);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }}

        .badge.priority-urgent {{
            background: rgba(239, 68, 68, 0.12);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.4);
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.1);
        }}

        .badge.priority-urgent::before {{
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            background-color: #f87171;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 1.5s infinite;
        }}

        .badge.priority-standard {{
            background: rgba(16, 185, 129, 0.12);
            color: #6ee7b7;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .badge.priority-low {{
            background: rgba(107, 114, 128, 0.12);
            color: #d1d5db;
            border: 1px solid rgba(107, 114, 128, 0.3);
        }}

        .badge.flag-review {{
            background: rgba(245, 158, 11, 0.12);
            color: #fcd34d;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}

        .reason-text {{
            color: #cbd5e1;
            font-size: 0.85rem;
            max-width: 450px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .no-data {{
            text-align: center;
            padding: 3rem;
            color: var(--secondary-text);
            font-style: italic;
        }}

        /* Pagination Controls */
        .pagination {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            background: rgba(0, 0, 0, 0.1);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .pagination-info {{
            font-size: 0.8rem;
            color: var(--secondary-text);
        }}

        .pagination-btns {{
            display: flex;
            gap: 0.5rem;
        }}

        .page-btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--primary-text);
            padding: 0.4rem 0.8rem;
            border-radius: 8px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .page-btn:hover:not(:disabled) {{
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.2);
        }}

        .page-btn:disabled {{
            opacity: 0.4;
            cursor: not-allowed;
        }}

        /* Premium Modal Details */
        .modal-overlay {{
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(3, 7, 18, 0.8);
            backdrop-filter: blur(8px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }}

        .modal-overlay.active {{
            opacity: 1;
            pointer-events: auto;
        }}

        .modal-content {{
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 24px;
            padding: 2.2rem;
            width: 90%;
            max-width: 650px;
            position: relative;
            transform: scale(0.9);
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(59, 130, 246, 0.1);
        }}

        .modal-overlay.active .modal-content {{
            transform: scale(1);
        }}

        .close-btn {{
            position: absolute;
            top: 1.2rem; right: 1.2rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--secondary-text);
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.1rem;
            transition: all 0.2s ease;
        }}

        .close-btn:hover {{
            background: rgba(239, 68, 68, 0.15);
            color: var(--urgent-color);
            border-color: rgba(239, 68, 68, 0.3);
        }}

        .modal-header {{
            margin-bottom: 1.5rem;
        }}

        .modal-title-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }}

        .modal-title {{
            font-size: 1.3rem;
            font-weight: 700;
        }}

        .modal-meta-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.2rem;
            margin-bottom: 1.5rem;
            background: rgba(255, 255, 255, 0.02);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.04);
        }}

        .meta-item {{
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }}

        .meta-label {{
            font-size: 0.75rem;
            color: var(--secondary-text);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .meta-val {{
            font-size: 0.9rem;
            font-weight: 500;
        }}

        .modal-body-section {{
            margin-bottom: 1.2rem;
        }}

        .section-label {{
            font-size: 0.8rem;
            color: var(--secondary-text);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.4rem;
            font-weight: 600;
        }}

        .description-box {{
            background: rgba(0, 0, 0, 0.2);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.95rem;
            line-height: 1.5;
            color: #e2e8f0;
        }}

        .reason-box {{
            background: rgba(59, 130, 246, 0.05);
            border: 1px solid rgba(59, 130, 246, 0.15);
            padding: 1rem;
            border-radius: 12px;
            font-size: 0.95rem;
            line-height: 1.5;
            color: #93c5fd;
        }}

        /* Buttons styling */
        .btn {{
            background: var(--accent-blue);
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s ease;
        }}

        .btn:hover {{
            background: #2563eb;
            box-shadow: 0 0 15px rgba(37, 99, 235, 0.4);
        }}

        .btn-outline {{
            background: rgba(255, 255, 255, 0.05);
            color: var(--primary-text);
            border: 1px solid var(--card-border);
        }}

        .btn-outline:hover {{
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: none;
        }}

        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }}
            70% {{ box-shadow: 0 0 0 6px rgba(59, 130, 246, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }}
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Responsiveness */
        @media (max-width: 1024px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            .city-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 640px) {{
            .city-grid {{
                grid-template-columns: 1fr;
            }}
            .controls-card {{
                flex-direction: column;
                align-items: stretch;
            }}
            .search-wrapper {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>

    <div class="container">
        <header>
            <div class="header-left">
                <h1>Civic AI Dispatch System</h1>
                <select id="city-select" class="glass-select" onchange="onCityChange(this.value)">
                    <!-- Options populated dynamically -->
                </select>
            </div>
            <button class="btn btn-outline" onclick="exportToCSV()">
                📥 Export CSV
            </button>
        </header>

        <!-- KPIs -->
        <div class="dashboard-grid">
            <div class="kpi-card total">
                <div class="kpi-header">
                    <span class="kpi-title">Total Complaints</span>
                    <span class="kpi-icon">📊</span>
                </div>
                <div class="kpi-value blue" id="kpi-total">0</div>
                <div class="kpi-subtext">Active items in selected scope</div>
            </div>
            
            <div class="kpi-card urgent">
                <div class="kpi-header">
                    <span class="kpi-title">Urgent Incidents</span>
                    <span class="kpi-icon">🔴</span>
                </div>
                <div class="kpi-value red" id="kpi-urgent">0</div>
                <div class="kpi-subtext">Immediate severity threats</div>
            </div>

            <div class="kpi-card review">
                <div class="kpi-header">
                    <span class="kpi-title">Pending Review</span>
                    <span class="kpi-icon">⚠️</span>
                </div>
                <div class="kpi-value amber" id="kpi-review">0</div>
                <div class="kpi-subtext">Taxonomy/ambiguity flags</div>
            </div>
        </div>

        <!-- All Cities Criticality Breakdown Card -->
        <div class="criticality-index-card">
            <div class="section-title">
                🌐 Cities Criticality Comparison
            </div>
            <div class="city-grid" id="city-criticality-grid">
                <!-- Populated dynamically -->
            </div>
        </div>

        <!-- Filter Controls -->
        <div class="controls-card">
            <div class="filter-group">
                <div class="search-wrapper">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="search-input" class="search-input" placeholder="Search by description, location..." oninput="onSearchChange(this.value)">
                </div>
                
                <select id="category-filter" class="glass-select" onchange="onCategoryChange(this.value)">
                    <!-- Populated dynamically -->
                </select>
            </div>

            <div class="filter-group">
                <span style="font-size: 0.8rem; color: var(--secondary-text); font-weight:600; text-transform:uppercase;">Priority:</span>
                <div class="pill-filters">
                    <button class="pill-btn active" id="prio-all" onclick="onPriorityChange('All')">All</button>
                    <button class="pill-btn" id="prio-urgent" onclick="onPriorityChange('Urgent')">Urgent</button>
                    <button class="pill-btn" id="prio-standard" onclick="onPriorityChange('Standard')">Standard</button>
                    <button class="pill-btn" id="prio-low" onclick="onPriorityChange('Low')">Low</button>
                </div>

                <span style="font-size: 0.8rem; color: var(--secondary-text); font-weight:600; text-transform:uppercase; margin-left: 1rem;">Status:</span>
                <div class="pill-filters">
                    <button class="pill-btn active" id="status-all" onclick="onStatusChange('All')">All</button>
                    <button class="pill-btn" id="status-auto" onclick="onStatusChange('Auto')">Auto</button>
                    <button class="pill-btn" id="status-review" onclick="onStatusChange('Review')">Review</button>
                </div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="table-container">
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
                    <!-- Rows injected dynamically -->
                </tbody>
            </table>
            
            <!-- Pagination -->
            <div class="pagination">
                <div class="pagination-info" id="page-info">
                    Showing 0-0 of 0 complaints
                </div>
                <div class="pagination-btns">
                    <button class="page-btn" id="prev-btn" onclick="changePage(-1)">Previous</button>
                    <button class="page-btn" id="next-btn" onclick="changePage(1)">Next</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Complaint Details Modal -->
    <div class="modal-overlay" id="details-modal">
        <div class="modal-content">
            <button class="close-btn" onclick="closeModal()">✕</button>
            
            <div class="modal-header">
                <div class="modal-title-row">
                    <span class="modal-title" id="modal-id">UNKNOWN-ID</span>
                    <span class="badge city" id="modal-city">Unknown City</span>
                </div>
                <div style="display:flex; gap:0.5rem; margin-top:0.5rem;">
                    <span class="badge" id="modal-category">Category</span>
                    <span class="badge" id="modal-priority">Priority</span>
                    <span class="badge" id="modal-status">Status</span>
                </div>
            </div>

            <div class="modal-meta-grid">
                <div class="meta-item">
                    <span class="meta-label">Date Raised</span>
                    <span class="meta-val" id="modal-date">N/A</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Days Open</span>
                    <span class="meta-val" id="modal-days">N/A</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Ward / Area</span>
                    <span class="meta-val" id="modal-ward">N/A</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Location</span>
                    <span class="meta-val" id="modal-location">N/A</span>
                </div>
                <div class="meta-item" style="grid-column: span 2;">
                    <span class="meta-label">Reported Via</span>
                    <span class="meta-val" id="modal-reported">N/A</span>
                </div>
            </div>

            <div class="modal-body-section">
                <div class="section-label">Citizen Description</div>
                <div class="description-box" id="modal-desc">
                    No description available.
                </div>
            </div>

            <div class="modal-body-section">
                <div class="section-label">AI Justification & Citations</div>
                <div class="reason-box" id="modal-reason">
                    No justification provided.
                </div>
            </div>
        </div>
    </div>

    <script>
        const complaintsData = {json_data};
        
        let activeCity = 'All';
        let activePriority = 'All';
        let activeStatus = 'All';
        let activeCategory = 'All';
        let searchQuery = '';

        // Pagination state
        let currentPage = 1;
        const rowsPerPage = 10;

        function initFilters() {{
            const citySelect = document.getElementById('city-select');
            const catSelect = document.getElementById('category-filter');
            
            const cities = [...new Set(complaintsData.map(c => c.city))].sort();
            const categories = [...new Set(complaintsData.map(c => c.category))].sort();

            // Populate City Select
            citySelect.innerHTML = '<option value="All">All Cities</option>';
            cities.forEach(city => {{
                const opt = document.createElement('option');
                opt.value = city;
                opt.textContent = city;
                citySelect.appendChild(opt);
            }});

            // Populate Category Select
            catSelect.innerHTML = '<option value="All">All Categories</option>';
            categories.forEach(cat => {{
                const opt = document.createElement('option');
                opt.value = cat;
                opt.textContent = cat;
                catSelect.appendChild(opt);
            }});
        }}

        function renderCriticalityIndex() {{
            const container = document.getElementById('city-criticality-grid');
            container.innerHTML = '';

            const cities = [...new Set(complaintsData.map(c => c.city))].sort();
            
            cities.forEach(city => {{
                const cityData = complaintsData.filter(c => c.city === city);
                const total = cityData.length;
                const urgent = cityData.filter(c => c.priority === 'Urgent').length;
                const review = cityData.filter(c => c.flag === 'NEEDS_REVIEW' || c.flag === 'NEEDS REVIEW').length;
                const standard = cityData.filter(c => c.priority === 'Standard').length;
                const low = cityData.filter(c => c.priority === 'Low').length;

                // Percentages
                const urgentPct = total > 0 ? (urgent / total) * 100 : 0;
                const reviewPct = total > 0 ? (review / total) * 100 : 0;
                const standardPct = total > 0 ? (standard / total) * 100 : 0;
                const lowPct = total > 0 ? (low / total) * 100 : 0;

                const card = document.createElement('div');
                card.className = 'city-card';
                card.innerHTML = `
                    <div class="city-card-header">
                        <span class="city-name">${{city}}</span>
                        <span class="city-total-badge">${{total}} total</span>
                    </div>
                    <div class="stacked-bar">
                        <div class="bar-segment urgent" style="width: ${{urgentPct}}%" title="Urgent: ${{urgent}}"></div>
                        <div class="bar-segment review" style="width: ${{reviewPct}}%" title="Needs Review: ${{review}}"></div>
                        <div class="bar-segment standard" style="width: ${{standardPct}}%" title="Standard: ${{standard}}"></div>
                        <div class="bar-segment low" style="width: ${{lowPct}}%" title="Low: ${{low}}"></div>
                    </div>
                    <div class="city-stats-legend">
                        <div class="legend-item"><span class="dot urgent"></span><span>${{urgent}} Urg</span></div>
                        <div class="legend-item"><span class="dot review"></span><span>${{review}} Rev</span></div>
                        <div class="legend-item"><span class="dot standard"></span><span>${{standard}} Std</span></div>
                    </div>
                `;
                container.appendChild(card);
            }});
        }}

        function updateDashboard() {{
            let filtered = complaintsData.filter(c => {{
                const cityMatch = activeCity === 'All' || c.city === activeCity;
                const priorityMatch = activePriority === 'All' || c.priority === activePriority;
                const statusMatch = activeStatus === 'All' || 
                                    (activeStatus === 'Review' && (c.flag === 'NEEDS_REVIEW' || c.flag === 'NEEDS REVIEW')) ||
                                    (activeStatus === 'Auto' && !c.flag);
                const categoryMatch = activeCategory === 'All' || c.category === activeCategory;
                
                const searchStr = `${{c.id}} ${{c.city}} ${{c.category}} ${{c.description}} ${{c.location}} ${{c.ward}} ${{c.reason}}`.toLowerCase();
                const searchMatch = searchQuery === '' || searchStr.includes(searchQuery);

                return cityMatch && priorityMatch && statusMatch && categoryMatch && searchMatch;
            }});

            // Update KPI values
            const total = filtered.length;
            const urgent = filtered.filter(c => c.priority === 'Urgent').length;
            const review = filtered.filter(c => c.flag === 'NEEDS_REVIEW' || c.flag === 'NEEDS REVIEW').length;

            animateValue('kpi-total', 0, total, 400);
            animateValue('kpi-urgent', 0, urgent, 400);
            animateValue('kpi-review', 0, review, 400);

            // Paginated items
            const totalPages = Math.max(1, Math.ceil(total / rowsPerPage));
            if (currentPage > totalPages) currentPage = totalPages;

            const startIndex = (currentPage - 1) * rowsPerPage;
            const endIndex = Math.min(startIndex + rowsPerPage, total);
            const pageData = filtered.slice(startIndex, endIndex);

            // Populate Table
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';

            if (pageData.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="6" class="no-data">No complaints matching current filters found.</td></tr>';
            }} else {{
                pageData.forEach((complaint, index) => {{
                    const tr = document.createElement('tr');
                    tr.className = 'complaint-row';
                    tr.style.opacity = '0';
                    tr.style.animation = `fadeIn 0.3s ease forwards ${{index * 0.03}}s`;
                    
                    tr.onclick = () => showModal(complaint);
                    
                    let pBadgeClass = 'priority-low';
                    if (complaint.priority === 'Urgent') pBadgeClass = 'priority-urgent';
                    else if (complaint.priority === 'Standard') pBadgeClass = 'priority-standard';

                    const fBadge = complaint.flag ? 
                        `<span class="badge flag-review">⚠️ ${{complaint.flag.replace('_', ' ')}}</span>` : 
                        `<span style="color:var(--secondary-text); font-size:0.75rem;">✓ Auto</span>`;

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

            // Update Pagination Info
            document.getElementById('page-info').textContent = `Showing ${{total === 0 ? 0 : startIndex + 1}}-${{endIndex}} of ${{total}} complaints`;
            document.getElementById('prev-btn').disabled = currentPage === 1;
            document.getElementById('next-btn').disabled = currentPage === totalPages;
        }}

        function animateValue(id, start, end, duration) {{
            const el = document.getElementById(id);
            if (!el) return;
            if (start === end) {{
                el.textContent = end;
                return;
            }}
            let startTimestamp = null;
            const step = (timestamp) => {{
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                el.textContent = Math.floor(progress * (end - start) + start);
                if (progress < 1) {{
                    window.requestAnimationFrame(step);
                }}
            }};
            window.requestAnimationFrame(step);
        }}

        // Filters Handlers
        function onCityChange(val) {{
            activeCity = val;
            currentPage = 1;
            updateDashboard();
        }}

        function onCategoryChange(val) {{
            activeCategory = val;
            currentPage = 1;
            updateDashboard();
        }}

        function onSearchChange(val) {{
            searchQuery = val.trim().toLowerCase();
            currentPage = 1;
            updateDashboard();
        }}

        function onPriorityChange(val) {{
            activePriority = val;
            currentPage = 1;
            
            // Toggle active class on buttons
            ['All', 'Urgent', 'Standard', 'Low'].forEach(p => {{
                const id = `prio-${{p.toLowerCase()}}`;
                const btn = document.getElementById(id);
                if (btn) {{
                    if (p === val) btn.classList.add('active');
                    else btn.classList.remove('active');
                }}
            }});
            updateDashboard();
        }}

        function onStatusChange(val) {{
            activeStatus = val;
            currentPage = 1;
            
            ['All', 'Auto', 'Review'].forEach(s => {{
                const id = `status-${{s.toLowerCase()}}`;
                const btn = document.getElementById(id);
                if (btn) {{
                    if (s === val) btn.classList.add('active');
                    else btn.classList.remove('active');
                }}
            }});
            updateDashboard();
        }}

        // Pagination
        function changePage(direction) {{
            currentPage += direction;
            updateDashboard();
        }}

        // Modal Controls
        function showModal(complaint) {{
            document.getElementById('modal-id').textContent = complaint.id;
            document.getElementById('modal-city').textContent = complaint.city;
            document.getElementById('modal-date').textContent = complaint.date_raised || 'N/A';
            document.getElementById('modal-ward').textContent = complaint.ward || 'N/A';
            document.getElementById('modal-location').textContent = complaint.location || 'N/A';
            document.getElementById('modal-reported').textContent = complaint.reported_by || 'N/A';
            document.getElementById('modal-days').textContent = complaint.days_open ? `${{complaint.days_open}} days` : 'N/A';
            
            const categoryBadge = document.getElementById('modal-category');
            categoryBadge.className = 'badge category';
            categoryBadge.textContent = complaint.category;

            const priorityBadge = document.getElementById('modal-priority');
            let pBadgeClass = 'priority-low';
            if (complaint.priority === 'Urgent') pBadgeClass = 'priority-urgent';
            else if (complaint.priority === 'Standard') pBadgeClass = 'priority-standard';
            priorityBadge.className = `badge ${{pBadgeClass}}`;
            priorityBadge.textContent = complaint.priority;

            const statusBadge = document.getElementById('modal-status');
            if (complaint.flag) {{
                statusBadge.style.display = 'inline-flex';
                statusBadge.className = 'badge flag-review';
                statusBadge.textContent = complaint.flag.replace('_', ' ');
            }} else {{
                statusBadge.style.display = 'none';
            }}

            document.getElementById('modal-desc').textContent = complaint.description || 'No description available.';
            document.getElementById('modal-reason').textContent = complaint.reason || 'No justification provided.';

            document.getElementById('details-modal').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('details-modal').classList.remove('active');
        }}

        // Close modal when clicking outside content
        window.onclick = function(event) {{
            const modal = document.getElementById('details-modal');
            if (event.target === modal) {{
                closeModal();
            }}
        }}

        // Export to CSV
        function exportToCSV() {{
            let filtered = complaintsData.filter(c => {{
                const cityMatch = activeCity === 'All' || c.city === activeCity;
                const priorityMatch = activePriority === 'All' || c.priority === activePriority;
                const statusMatch = activeStatus === 'All' || 
                                    (activeStatus === 'Review' && (c.flag === 'NEEDS_REVIEW' || c.flag === 'NEEDS REVIEW')) ||
                                    (activeStatus === 'Auto' && !c.flag);
                const categoryMatch = activeCategory === 'All' || c.category === activeCategory;
                
                const searchStr = `${{c.id}} ${{c.city}} ${{c.category}} ${{c.description}} ${{c.location}} ${{c.ward}} ${{c.reason}}`.toLowerCase();
                const searchMatch = searchQuery === '' || searchStr.includes(searchQuery);

                return cityMatch && priorityMatch && statusMatch && categoryMatch && searchMatch;
            }});

            if (filtered.length === 0) {{
                alert('No complaints to export!');
                return;
            }}

            const headers = ["Complaint ID", "City", "Date Raised", "Ward", "Location", "Category", "Priority", "AI Reasoning", "Status Flag", "Reported By", "Days Open", "Description"];
            const rows = filtered.map(c => [
                c.id, c.city, c.date_raised, c.ward, c.location, c.category, c.priority, c.reason, c.flag, c.reported_by, c.days_open, c.description
            ]);

            const csvContent = [headers, ...rows]
                .map(row => row.map(val => `"${{String(val || '').replace(/"/g, '""')}}"`).join(","))
                .join("\\n");

            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.setAttribute("href", url);
            link.setAttribute("download", `civic_complaints_${{activeCity.toLowerCase()}}_export.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}

        // Initialize on page load
        initFilters();
        renderCriticalityIndex();
        updateDashboard();
    </script>
</body>
</html>
"""
    
    output_path = "dashboard.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Successfully wrote updated dashboard: {output_path}")

if __name__ == "__main__":
    main()
