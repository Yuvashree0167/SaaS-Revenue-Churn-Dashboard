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

## Deploy for a public URL (Streamlit Community Cloud)
1. Push this folder to a public GitHub repo (app.py, data.csv, requirements.txt at the root).
2. Go to https://share.streamlit.io, sign in with GitHub, click **Create app**.
3. Pick the repo, branch `main`, main file `app.py`, then **Deploy**.
4. Submit the resulting `https://<name>.streamlit.app` URL.
