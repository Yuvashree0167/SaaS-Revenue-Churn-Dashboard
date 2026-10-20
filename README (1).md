# Business Intelligence Dashboard (Streamlit + Plotly)

Interactive dashboard over a SaaS subscription dataset (`data.csv`, ~13k rows, Jan 2025 – Oct 2026).

**KPI cards:** Total Revenue, Active Users (daily avg), Churn %, Avg Ticket Size, each with change vs. the previous period of equal length.
**Filters:** Date range, Region, Category (sidebar).
**Charts:** revenue + active-users trend (daily/weekly/monthly), revenue by region, category share, monthly churn %, region x category heatmap, plus a downloadable data table.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
(`python generate_data.py` regenerates `data.csv`.)
