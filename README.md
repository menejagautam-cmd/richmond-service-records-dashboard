# Richmond Civic Service Dashboard

Interactive dashboard analyzing 5,000+ community service requests across 20 Richmond, VA neighborhoods. Built with Python, pandas, and Plotly.

**[View Live Dashboard](https://menejagautam-cmd.github.io/richmond-civic-dashboard/richmond_civic_dashboard.html)**

## Dashboard Pages

### Civic Service Overview
6 KPI cards, top service requests by volume, category breakdown, monthly trends with resolution rate overlay, submission source analysis, and priority distribution.

### Neighborhood Analysis
Top 10 neighborhoods by request volume, service category × neighborhood heatmap, and neighborhood performance scorecard with letter grades.

### Response & Performance
Average response time by category and priority level, department performance scorecard, satisfaction score distribution, and request status breakdown.

## Tech Stack
- **Python** — data generation and analysis
- **pandas** — data manipulation
- **Plotly** — interactive JavaScript visualizations
- **HTML/CSS/JS** — single-file dashboard with tabbed navigation

## Key Metrics
- 5,000 service requests analyzed
- 20 Richmond neighborhoods covered
- 6 service categories, 24 service types
- Interactive charts with hover tooltips and clickable navigation

## How to Run
```bash
pip install pandas plotly numpy
python richmond_civic_dashboard.py
```

## Context
This project connects to my experience building the myRVA civic engagement platform, where I designed analytics pipelines to analyze community reports and surface geographic patterns for local government partners.
