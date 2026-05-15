"""
richmond_civic_dashboard.py
Generates an interactive multi-page HTML dashboard analyzing
civic service requests across Richmond, VA neighborhoods.

Connects to real Richmond geography and service categories.
Run: python richmond_civic_dashboard.py
Output: richmond_civic_dashboard.html (open in any browser)
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import os

np.random.seed(42)

# ============================================================
# GENERATE REALISTIC RICHMOND CIVIC DATA
# ============================================================

NEIGHBORHOODS = [
    "The Fan", "Carytown", "Church Hill", "Shockoe Bottom", "Scott's Addition",
    "Manchester", "Oregon Hill", "Jackson Ward", "Museum District", "Lakeside",
    "Short Pump", "Northside", "Southside", "East End", "West End",
    "Highland Park", "Ginter Park", "Woodland Heights", "Fulton", "Bon Air"
]

SERVICE_CATEGORIES = {
    "Road & Sidewalk": ["Pothole Repair", "Sidewalk Damage", "Street Light Out", "Crosswalk Faded"],
    "Sanitation": ["Missed Trash Pickup", "Illegal Dumping", "Overflowing Bin", "Bulk Pickup Request"],
    "Parks & Public Spaces": ["Park Maintenance", "Graffiti Removal", "Playground Repair", "Tree Hazard"],
    "Noise & Nuisance": ["Noise Complaint", "Abandoned Vehicle", "Property Maintenance", "Animal Control"],
    "Water & Utilities": ["Water Main Break", "Storm Drain Blocked", "Hydrant Issue", "Sewer Problem"],
    "Public Safety": ["Traffic Signal Issue", "Unsafe Structure", "Missing Sign", "Hazardous Condition"]
}

PRIORITIES = ["Low", "Medium", "High", "Emergency"]
STATUSES = ["Open", "In Progress", "Resolved", "Closed"]
SOURCES = ["Mobile App", "Phone", "Website", "Walk-in", "Email"]
DEPARTMENTS = ["Public Works", "Parks & Rec", "Public Utilities", "Code Enforcement", "Police", "Transportation"]

NUM_RECORDS = 5000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)


def generate_richmond_data():
    """Generate realistic civic service request data for Richmond, VA."""
    dates = [START_DATE + timedelta(days=np.random.randint(0, (END_DATE - START_DATE).days)) for _ in range(NUM_RECORDS)]
    
    # Build service types with their parent categories
    all_types = []
    all_categories = []
    for cat, types in SERVICE_CATEGORIES.items():
        for _ in range(NUM_RECORDS // len(SERVICE_CATEGORIES)):
            t = np.random.choice(types)
            all_types.append(t)
            all_categories.append(cat)
    
    # Pad to exact NUM_RECORDS
    while len(all_types) < NUM_RECORDS:
        cat = np.random.choice(list(SERVICE_CATEGORIES.keys()))
        t = np.random.choice(SERVICE_CATEGORIES[cat])
        all_types.append(t)
        all_categories.append(cat)
    
    # Shuffle
    indices = np.random.permutation(NUM_RECORDS)
    all_types = [all_types[i] for i in indices]
    all_categories = [all_categories[i] for i in indices]
    
    # Response times vary by priority
    priorities = np.random.choice(PRIORITIES, NUM_RECORDS, p=[0.25, 0.40, 0.25, 0.10])
    response_days = []
    for p in priorities:
        if p == "Emergency":
            response_days.append(round(np.random.exponential(0.5), 2))
        elif p == "High":
            response_days.append(round(np.random.exponential(2), 2))
        elif p == "Medium":
            response_days.append(round(np.random.exponential(5), 2))
        else:
            response_days.append(round(np.random.exponential(10), 2))
    
    statuses = np.random.choice(STATUSES, NUM_RECORDS, p=[0.08, 0.12, 0.45, 0.35])
    
    # Neighborhood weighting (some areas report more)
    neighborhood_weights = np.random.dirichlet(np.ones(len(NEIGHBORHOODS)) * 2)
    neighborhoods = np.random.choice(NEIGHBORHOODS, NUM_RECORDS, p=neighborhood_weights)
    
    df = pd.DataFrame({
        "request_id": [f"RVA-{10000 + i}" for i in range(NUM_RECORDS)],
        "date_submitted": dates,
        "neighborhood": neighborhoods,
        "category": all_categories,
        "service_type": all_types,
        "priority": priorities,
        "status": statuses,
        "response_days": response_days,
        "source": np.random.choice(SOURCES, NUM_RECORDS, p=[0.35, 0.25, 0.20, 0.10, 0.10]),
        "department": np.random.choice(DEPARTMENTS, NUM_RECORDS),
        "satisfaction_score": np.round(np.random.uniform(1, 5, NUM_RECORDS), 1)
    })
    
    df["date_submitted"] = pd.to_datetime(df["date_submitted"])
    df["month"] = df["date_submitted"].dt.to_period("M").astype(str)
    df["quarter"] = df["date_submitted"].dt.to_period("Q").astype(str)
    df["resolution_rate"] = np.where(df["status"].isin(["Resolved", "Closed"]), 1, 0)
    
    return df


# ============================================================
# BUILD DASHBOARD
# ============================================================

def build_dashboard(df):
    """Build a complete multi-page interactive HTML dashboard."""
    
    # Color palette
    NAVY = "#1B2A4A"
    TEAL = "#2CA58D"
    CORAL = "#E8614D"
    GOLD = "#F4A940"
    PURPLE = "#6C5CE7"
    BLUE = "#0984E3"
    COLORS = [TEAL, CORAL, GOLD, PURPLE, BLUE, NAVY, "#00B894", "#D63031", "#6C5CE7", "#636E72"]
    
    # KPI calculations
    total_requests = len(df)
    resolution_rate = df["resolution_rate"].mean() * 100
    avg_response = df["response_days"].mean()
    avg_satisfaction = df["satisfaction_score"].mean()
    mobile_pct = (df["source"] == "Mobile App").mean() * 100
    emergency_count = (df["priority"] == "Emergency").sum()
    
    # ============================================================
    # PAGE 1: CIVIC SERVICE OVERVIEW
    # ============================================================
    
    # Top complaints
    top_complaints = df["service_type"].value_counts().head(12)
    
    # By neighborhood
    by_neighborhood = df["neighborhood"].value_counts().head(10)
    
    # Monthly trend
    monthly = df.groupby("month").agg(
        count=("request_id", "count"),
        avg_response=("response_days", "mean"),
        resolution=("resolution_rate", "mean")
    ).reset_index()
    
    # By category
    by_category = df["category"].value_counts()
    
    # By source
    by_source = df["source"].value_counts()
    
    # ============================================================
    # PAGE 2: NEIGHBORHOOD ANALYSIS
    # ============================================================
    
    # Neighborhood performance
    hood_perf = df.groupby("neighborhood").agg(
        total=("request_id", "count"),
        avg_response=("response_days", "mean"),
        resolution_rate=("resolution_rate", "mean"),
        avg_satisfaction=("satisfaction_score", "mean")
    ).reset_index().sort_values("total", ascending=False)
    
    # Neighborhood x Category heatmap
    hood_cat = df.groupby(["neighborhood", "category"]).size().unstack(fill_value=0)
    
    # Priority distribution by neighborhood (top 10)
    top_hoods = df["neighborhood"].value_counts().head(10).index.tolist()
    priority_dist = df[df["neighborhood"].isin(top_hoods)].groupby(
        ["neighborhood", "priority"]).size().unstack(fill_value=0)
    
    # ============================================================
    # PAGE 3: RESPONSE & PERFORMANCE
    # ============================================================
    
    # Response time by category
    response_by_cat = df.groupby("category")["response_days"].mean().sort_values()
    
    # Response time by priority
    response_by_priority = df.groupby("priority")["response_days"].mean().sort_values()
    
    # Department performance
    dept_perf = df.groupby("department").agg(
        total=("request_id", "count"),
        avg_response=("response_days", "mean"),
        resolution_rate=("resolution_rate", "mean"),
        avg_satisfaction=("satisfaction_score", "mean")
    ).reset_index().sort_values("avg_response")
    
    # Satisfaction distribution
    sat_dist = df["satisfaction_score"].round(0).value_counts().sort_index()
    
    # ============================================================
    # BUILD HTML
    # ============================================================
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Richmond Civic Service Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0f2f5; color: #2d3436; }}
        
        .header {{ background: linear-gradient(135deg, {NAVY}, {TEAL}); color: white; padding: 40px 60px; }}
        .header h1 {{ font-size: 32px; margin-bottom: 8px; letter-spacing: -0.5px; }}
        .header p {{ opacity: 0.85; font-size: 15px; }}
        
        .nav {{ background: white; padding: 0 60px; border-bottom: 2px solid #e9ecef; position: sticky; top: 0; z-index: 100; }}
        .nav-links {{ display: flex; gap: 0; }}
        .nav-links a {{ padding: 16px 24px; text-decoration: none; color: #636e72; font-weight: 600; font-size: 14px; border-bottom: 3px solid transparent; transition: all 0.2s; cursor: pointer; }}
        .nav-links a:hover, .nav-links a.active {{ color: {NAVY}; border-bottom-color: {TEAL}; }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
        
        .kpi-grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; margin-bottom: 30px; }}
        .kpi-card {{ background: white; border-radius: 12px; padding: 24px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
        .kpi-card .value {{ font-size: 32px; font-weight: 700; color: {NAVY}; }}
        .kpi-card .label {{ font-size: 11px; color: #636e72; text-transform: uppercase; letter-spacing: 1px; margin-top: 6px; }}
        
        .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .chart-full {{ grid-column: 1 / -1; }}
        .chart-card {{ background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
        .chart-card h3 {{ font-size: 16px; color: {NAVY}; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid {TEAL}; }}
        
        .page {{ display: none; }}
        .page.active {{ display: block; }}
        
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: {NAVY}; color: white; padding: 12px 16px; text-align: left; font-size: 12px; text-transform: uppercase; }}
        td {{ padding: 10px 16px; border-bottom: 1px solid #eee; font-size: 14px; }}
        tr:hover {{ background: #f8f9fa; }}
        
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
        .badge-a {{ background: #d4edda; color: #155724; }}
        .badge-b {{ background: #fff3cd; color: #856404; }}
        .badge-c {{ background: #f8d7da; color: #721c24; }}
        
        .footer {{ text-align: center; padding: 40px; color: #636e72; font-size: 12px; }}
        
        @media (max-width: 768px) {{
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .chart-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Richmond Civic Service Dashboard</h1>
        <p>Analyzing {total_requests:,} community service requests across {len(df['neighborhood'].unique())} neighborhoods | {START_DATE.strftime('%b %Y')} – {END_DATE.strftime('%b %Y')}</p>
    </div>
    
    <div class="nav">
        <div class="nav-links">
            <a class="active" onclick="showPage('overview')">Overview</a>
            <a onclick="showPage('neighborhoods')">Neighborhood Analysis</a>
            <a onclick="showPage('performance')">Response & Performance</a>
        </div>
    </div>

    <!-- ==================== PAGE 1: OVERVIEW ==================== -->
    <div id="overview" class="page active">
        <div class="container">
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="value">{total_requests:,}</div>
                    <div class="label">Total Requests</div>
                </div>
                <div class="kpi-card">
                    <div class="value">{resolution_rate:.1f}%</div>
                    <div class="label">Resolution Rate</div>
                </div>
                <div class="kpi-card">
                    <div class="value">{avg_response:.1f}</div>
                    <div class="label">Avg Response (Days)</div>
                </div>
                <div class="kpi-card">
                    <div class="value">{avg_satisfaction:.1f}/5</div>
                    <div class="label">Satisfaction Score</div>
                </div>
                <div class="kpi-card">
                    <div class="value">{mobile_pct:.0f}%</div>
                    <div class="label">Mobile Submissions</div>
                </div>
                <div class="kpi-card">
                    <div class="value" style="color:{CORAL}">{emergency_count}</div>
                    <div class="label">Emergency Requests</div>
                </div>
            </div>
            
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>Top Service Requests</h3>
                    <div id="chart_top_complaints"></div>
                </div>
                <div class="chart-card">
                    <h3>Requests by Category</h3>
                    <div id="chart_by_category"></div>
                </div>
                <div class="chart-card chart-full">
                    <h3>Monthly Request Volume & Resolution Rate</h3>
                    <div id="chart_monthly_trend"></div>
                </div>
                <div class="chart-card">
                    <h3>Submission Source</h3>
                    <div id="chart_by_source"></div>
                </div>
                <div class="chart-card">
                    <h3>Priority Distribution</h3>
                    <div id="chart_priority"></div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- ==================== PAGE 2: NEIGHBORHOODS ==================== -->
    <div id="neighborhoods" class="page">
        <div class="container">
            <div class="chart-grid">
                <div class="chart-card chart-full">
                    <h3>Requests by Neighborhood (Top 10)</h3>
                    <div id="chart_by_hood"></div>
                </div>
                <div class="chart-card chart-full">
                    <h3>Service Category × Neighborhood Heatmap</h3>
                    <div id="chart_heatmap"></div>
                </div>
                <div class="chart-card chart-full">
                    <h3>Neighborhood Performance Scorecard</h3>
                    <table>
                        <thead>
                            <tr><th>Neighborhood</th><th>Total Requests</th><th>Avg Response (Days)</th><th>Resolution Rate</th><th>Satisfaction</th><th>Grade</th></tr>
                        </thead>
                        <tbody>"""
    
    for _, row in hood_perf.head(15).iterrows():
        rate = row["resolution_rate"] * 100
        grade = "A" if rate >= 85 else ("B" if rate >= 75 else "C")
        badge_class = "badge-a" if grade == "A" else ("badge-b" if grade == "B" else "badge-c")
        html += f"""
                            <tr>
                                <td><strong>{row['neighborhood']}</strong></td>
                                <td>{row['total']:,}</td>
                                <td>{row['avg_response']:.1f}</td>
                                <td>{rate:.1f}%</td>
                                <td>{row['avg_satisfaction']:.1f}/5</td>
                                <td><span class="badge {badge_class}">{grade}</span></td>
                            </tr>"""
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <!-- ==================== PAGE 3: PERFORMANCE ==================== -->
    <div id="performance" class="page">
        <div class="container">
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>Avg Response Time by Category</h3>
                    <div id="chart_response_cat"></div>
                </div>
                <div class="chart-card">
                    <h3>Avg Response Time by Priority</h3>
                    <div id="chart_response_priority"></div>
                </div>
                <div class="chart-card chart-full">
                    <h3>Department Performance Scorecard</h3>
                    <table>
                        <thead>
                            <tr><th>Department</th><th>Requests Handled</th><th>Avg Response (Days)</th><th>Resolution Rate</th><th>Satisfaction</th></tr>
                        </thead>
                        <tbody>"""
    
    for _, row in dept_perf.iterrows():
        html += f"""
                            <tr>
                                <td><strong>{row['department']}</strong></td>
                                <td>{row['total']:,}</td>
                                <td>{row['avg_response']:.1f}</td>
                                <td>{row['resolution_rate']*100:.1f}%</td>
                                <td>{row['avg_satisfaction']:.1f}/5</td>
                            </tr>"""
    
    html += f"""
                        </tbody>
                    </table>
                </div>
                <div class="chart-card">
                    <h3>Satisfaction Score Distribution</h3>
                    <div id="chart_satisfaction"></div>
                </div>
                <div class="chart-card">
                    <h3>Request Status Breakdown</h3>
                    <div id="chart_status"></div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        Richmond Civic Service Dashboard | Built with Python, pandas & Plotly | Data: {total_requests:,} service requests across {len(df['neighborhood'].unique())} neighborhoods
    </div>

    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        // Page navigation
        function showPage(pageId) {{
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            event.target.classList.add('active');
        }}

        const COLORS = {str(COLORS)};
        const NAVY = '{NAVY}';
        const TEAL = '{TEAL}';
        const CORAL = '{CORAL}';

        // Chart 1: Top Complaints (horizontal bar)
        Plotly.newPlot('chart_top_complaints', [{{
            type: 'bar',
            y: {list(top_complaints.index)},
            x: {list(top_complaints.values.astype(int))},
            orientation: 'h',
            marker: {{ color: TEAL }},
            hovertemplate: '%{{y}}: %{{x:,}} requests<extra></extra>'
        }}], {{
            margin: {{ l: 160, r: 20, t: 10, b: 40 }},
            yaxis: {{ autorange: 'reversed' }},
            xaxis: {{ title: 'Number of Requests' }},
            height: 380
        }}, {{ responsive: true }});

        // Chart 2: By Category (donut)
        Plotly.newPlot('chart_by_category', [{{
            type: 'pie',
            labels: {list(by_category.index)},
            values: {list(by_category.values.astype(int))},
            hole: 0.45,
            marker: {{ colors: COLORS }},
            textinfo: 'label+percent',
            textposition: 'outside',
            hovertemplate: '%{{label}}: %{{value:,}} requests (%{{percent}})<extra></extra>'
        }}], {{
            margin: {{ l: 20, r: 20, t: 10, b: 10 }},
            height: 380,
            showlegend: false
        }}, {{ responsive: true }});

        // Chart 3: Monthly Trend (dual axis)
        Plotly.newPlot('chart_monthly_trend', [
            {{
                type: 'bar',
                x: {list(monthly['month'])},
                y: {list(monthly['count'].astype(int))},
                name: 'Requests',
                marker: {{ color: TEAL, opacity: 0.7 }},
                hovertemplate: '%{{x}}: %{{y:,}} requests<extra></extra>'
            }},
            {{
                type: 'scatter',
                mode: 'lines+markers',
                x: {list(monthly['month'])},
                y: {[round(v*100, 1) for v in monthly['resolution'].values]},
                name: 'Resolution Rate (%)',
                yaxis: 'y2',
                line: {{ color: CORAL, width: 3 }},
                marker: {{ size: 6 }},
                hovertemplate: '%{{x}}: %{{y:.1f}}%<extra></extra>'
            }}
        ], {{
            margin: {{ l: 60, r: 60, t: 10, b: 60 }},
            height: 350,
            xaxis: {{ tickangle: -45 }},
            yaxis: {{ title: 'Number of Requests' }},
            yaxis2: {{ title: 'Resolution Rate (%)', overlaying: 'y', side: 'right', range: [0, 100] }},
            legend: {{ x: 0.01, y: 0.99, bgcolor: 'rgba(255,255,255,0.8)' }}
        }}, {{ responsive: true }});

        // Chart 4: By Source (donut)
        Plotly.newPlot('chart_by_source', [{{
            type: 'pie',
            labels: {list(by_source.index)},
            values: {list(by_source.values.astype(int))},
            hole: 0.45,
            marker: {{ colors: COLORS }},
            textinfo: 'label+percent',
            hovertemplate: '%{{label}}: %{{value:,}} (%{{percent}})<extra></extra>'
        }}], {{
            margin: {{ l: 20, r: 20, t: 10, b: 10 }},
            height: 300,
            showlegend: false
        }}, {{ responsive: true }});

        // Chart 5: Priority Distribution
        var priority_data = {df['priority'].value_counts().to_dict()};
        Plotly.newPlot('chart_priority', [{{
            type: 'bar',
            x: Object.keys(priority_data),
            y: Object.values(priority_data),
            marker: {{ color: [TEAL, '{GOLD}', CORAL, '{NAVY}'] }},
            hovertemplate: '%{{x}}: %{{y:,}} requests<extra></extra>'
        }}], {{
            margin: {{ l: 50, r: 20, t: 10, b: 40 }},
            height: 300,
            xaxis: {{ title: '' }},
            yaxis: {{ title: 'Count' }}
        }}, {{ responsive: true }});

        // Chart 6: By Neighborhood
        Plotly.newPlot('chart_by_hood', [{{
            type: 'bar',
            y: {list(by_neighborhood.index)},
            x: {list(by_neighborhood.values.astype(int))},
            orientation: 'h',
            marker: {{ color: COLORS.slice(0, {len(by_neighborhood)}) }},
            hovertemplate: '%{{y}}: %{{x:,}} requests<extra></extra>'
        }}], {{
            margin: {{ l: 140, r: 20, t: 10, b: 40 }},
            yaxis: {{ autorange: 'reversed' }},
            xaxis: {{ title: 'Number of Requests' }},
            height: 400
        }}, {{ responsive: true }});

        // Chart 7: Heatmap
        Plotly.newPlot('chart_heatmap', [{{
            type: 'heatmap',
            z: {hood_cat.head(12).values.tolist()},
            x: {list(hood_cat.columns)},
            y: {list(hood_cat.head(12).index)},
            colorscale: [[0, '#f0f2f5'], [0.5, '{TEAL}'], [1, '{NAVY}']],
            hovertemplate: '%{{y}} — %{{x}}: %{{z}} requests<extra></extra>'
        }}], {{
            margin: {{ l: 140, r: 20, t: 10, b: 100 }},
            height: 450,
            xaxis: {{ tickangle: -30 }}
        }}, {{ responsive: true }});

        // Chart 8: Response by Category
        Plotly.newPlot('chart_response_cat', [{{
            type: 'bar',
            y: {list(response_by_cat.index)},
            x: {[round(v, 2) for v in response_by_cat.values]},
            orientation: 'h',
            marker: {{ color: {[f"'{TEAL}'" if v < avg_response else f"'{CORAL}'" for v in response_by_cat.values]} }},
            hovertemplate: '%{{y}}: %{{x:.1f}} days<extra></extra>'
        }}], {{
            margin: {{ l: 160, r: 20, t: 10, b: 40 }},
            xaxis: {{ title: 'Avg Response (Days)' }},
            yaxis: {{ autorange: 'reversed' }},
            height: 350
        }}, {{ responsive: true }});

        // Chart 9: Response by Priority
        Plotly.newPlot('chart_response_priority', [{{
            type: 'bar',
            x: {list(response_by_priority.index)},
            y: {[round(v, 2) for v in response_by_priority.values]},
            marker: {{ color: [TEAL, '{GOLD}', CORAL, '{NAVY}'] }},
            hovertemplate: '%{{x}}: %{{y:.1f}} days<extra></extra>'
        }}], {{
            margin: {{ l: 50, r: 20, t: 10, b: 40 }},
            yaxis: {{ title: 'Avg Response (Days)' }},
            height: 350
        }}, {{ responsive: true }});

        // Chart 10: Satisfaction
        Plotly.newPlot('chart_satisfaction', [{{
            type: 'bar',
            x: {list(sat_dist.index.astype(int))},
            y: {list(sat_dist.values.astype(int))},
            marker: {{ color: [CORAL, CORAL, '{GOLD}', TEAL, TEAL] }},
            hovertemplate: 'Rating %{{x}}: %{{y:,}} responses<extra></extra>'
        }}], {{
            margin: {{ l: 50, r: 20, t: 10, b: 40 }},
            xaxis: {{ title: 'Satisfaction Score', dtick: 1 }},
            yaxis: {{ title: 'Count' }},
            height: 300
        }}, {{ responsive: true }});

        // Chart 11: Status
        var status_data = {df['status'].value_counts().to_dict()};
        Plotly.newPlot('chart_status', [{{
            type: 'pie',
            labels: Object.keys(status_data),
            values: Object.values(status_data),
            hole: 0.45,
            marker: {{ colors: [TEAL, '{GOLD}', '{NAVY}', CORAL] }},
            textinfo: 'label+percent',
            hovertemplate: '%{{label}}: %{{value:,}} (%{{percent}})<extra></extra>'
        }}], {{
            margin: {{ l: 20, r: 20, t: 10, b: 10 }},
            height: 300,
            showlegend: false
        }}, {{ responsive: true }});
    </script>
</body>
</html>"""
    
    return html


def main():
    print("Generating Richmond civic service data...")
    df = generate_richmond_data()
    print(f"Generated {len(df):,} records across {df['neighborhood'].nunique()} neighborhoods")
    
    print("Building interactive dashboard...")
    html = build_dashboard(df)
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "richmond_civic_dashboard.html")
    with open(output_path, "w") as f:
        f.write(html)
    
    # Also save the data
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "richmond_civic_data.csv")
    df.to_csv(data_path, index=False)
    
    print(f"\nDashboard saved to: {output_path}")
    print(f"Data saved to: {data_path}")
    print("Open the HTML file in any browser to view the dashboard.")


if __name__ == "__main__":
    main()
