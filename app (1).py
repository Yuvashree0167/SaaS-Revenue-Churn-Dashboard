from datetime import timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Business Intelligence Dashboard", page_icon="📊", layout="wide")

PALETTE = ["#2563EB", "#0EA5E9", "#14B8A6", "#F59E0B", "#8B5CF6"]


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data.csv", parse_dates=["date"])
    return df


df = load_data()

# ---------------------------------------------------------------- Sidebar filters
st.sidebar.header("Filters")
min_d, max_d = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df["category"].unique()), default=sorted(df["category"].unique()))

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
else:
    start, end = min_d, max_d

mask = (
    (df["date"].dt.date >= start)
    & (df["date"].dt.date <= end)
    & (df["region"].isin(regions))
    & (df["category"].isin(categories))
)
f = df[mask]

st.title("📊 Business Intelligence Dashboard")
st.caption(f"Showing {start:%d %b %Y} → {end:%d %b %Y} · {len(f):,} records")

if f.empty:
    st.warning("No data for the selected filters. Adjust the filters in the sidebar.")
    st.stop()


# ---------------------------------------------------------------- KPIs
def kpis(d: pd.DataFrame):
    revenue = d["revenue"].sum()
    orders = d["orders"].sum()
    # Active users: average daily active users across the period
    active = d.groupby("date")["active_users"].sum().mean()
    churn = d["churned_users"].sum() / max(d["active_users"].sum(), 1) * 100
    ticket = revenue / max(orders, 1)
    return revenue, active, churn, ticket


cur = kpis(f)

# Compare with the previous period of equal length (when available)
span = (end - start).days + 1
prev_start, prev_end = start - timedelta(days=span), start - timedelta(days=1)
prev = df[
    (df["date"].dt.date >= prev_start) & (df["date"].dt.date <= prev_end)
    & df["region"].isin(regions) & df["category"].isin(categories)
]
prv = kpis(prev) if not prev.empty else None


def delta(i, pct=True, invert=False):
    if prv is None or prv[i] == 0:
        return None
    if pct:
        return f"{(cur[i] / prv[i] - 1) * 100:+.1f}%"
    return f"{cur[i] - prv[i]:+.1f} pts"


c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"${cur[0]:,.0f}", delta(0))
c2.metric("Active Users (daily avg)", f"{cur[1]:,.0f}", delta(1))
c3.metric("Churn %", f"{cur[2]:.1f}%", delta(2, pct=False), delta_color="inverse")
c4.metric("Avg Ticket Size", f"${cur[3]:,.2f}", delta(3))

st.divider()

# ---------------------------------------------------------------- Row 1: trend (hero chart)
freq = st.radio("Trend granularity", ["Daily", "Weekly", "Monthly"], index=2, horizontal=True)
rule = {"Daily": "D", "Weekly": "W", "Monthly": "MS"}[freq]
trend = f.set_index("date").resample(rule)[["revenue", "active_users"]].sum().reset_index()

fig = go.Figure()
fig.add_bar(x=trend["date"], y=trend["revenue"], name="Revenue", marker_color=PALETTE[0])
fig.add_scatter(x=trend["date"], y=trend["active_users"], name="Active users",
                yaxis="y2", line=dict(color=PALETTE[3], width=3))
fig.update_layout(
    title="Revenue and active users over time",
    yaxis=dict(title="Revenue ($)"),
    yaxis2=dict(title="Active users", overlaying="y", side="right", showgrid=False),
    legend=dict(orientation="h", y=1.12), margin=dict(t=70, b=20), height=380,
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- Row 2: breakdowns
left, right = st.columns(2)

by_region = f.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue")
fig_r = px.bar(by_region, x="revenue", y="region", orientation="h", title="Revenue by region",
               color_discrete_sequence=[PALETTE[0]])
fig_r.update_layout(margin=dict(t=50, b=20), height=340, yaxis_title=None, xaxis_title="Revenue ($)")
left.plotly_chart(fig_r, use_container_width=True)

by_cat = f.groupby("category", as_index=False)["revenue"].sum()
fig_c = px.pie(by_cat, names="category", values="revenue", hole=0.55, title="Revenue share by category",
               color_discrete_sequence=PALETTE)
fig_c.update_layout(margin=dict(t=50, b=20), height=340)
right.plotly_chart(fig_c, use_container_width=True)

# ---------------------------------------------------------------- Row 3: churn + heatmap
left, right = st.columns(2)

ch = f.set_index("date").resample("MS")[["churned_users", "active_users"]].sum().reset_index()
ch["churn_pct"] = ch["churned_users"] / ch["active_users"] * 100
fig_ch = px.line(ch, x="date", y="churn_pct", markers=True, title="Monthly churn %",
                 color_discrete_sequence=[PALETTE[3]])
fig_ch.update_layout(margin=dict(t=50, b=20), height=340, yaxis_title="Churn %", xaxis_title=None)
left.plotly_chart(fig_ch, use_container_width=True)

pivot = f.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum").fillna(0)
fig_h = px.imshow(pivot, aspect="auto", color_continuous_scale="Blues", title="Revenue: region × category")
fig_h.update_layout(margin=dict(t=50, b=20), height=340, coloraxis_showscale=False)
left_h = right
left_h.plotly_chart(fig_h, use_container_width=True)

# ---------------------------------------------------------------- Data table
with st.expander("View filtered data"):
    st.dataframe(f.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Download CSV", f.to_csv(index=False), "filtered_data.csv", "text/csv")
