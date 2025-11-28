# app.py  (Plotly + Dash) - with selectable chart STYLE
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

DATA_PATH = "covid_19_clean_complete.csv"  # adjust if needed

# ----- Load & preprocess -----
df = pd.read_csv(DATA_PATH, parse_dates=["Date"], dayfirst=False)
df = df.rename(columns={
    "Country/Region": "location",
    "Province/State": "province",
    "Date": "date",
    "Confirmed": "total_cases",
    "Deaths": "total_deaths",
    "Recovered": "recovered",
    "Active": "active",
    "WHO Region": "who_region",
    "Lat": "lat",
    "Long": "long"
})
df = df.sort_values(["location", "date"]).reset_index(drop=True)
df["new_cases"] = df.groupby("location")["total_cases"].diff().fillna(0).clip(lower=0)
df["new_deaths"] = df.groupby("location")["total_deaths"].diff().fillna(0).clip(lower=0)

countries = sorted(df["location"].dropna().unique())

# chart type mapping (metric)
CHARTS = {
    "total_cases": "total_cases",
    "new_cases": "new_cases",
    "total_deaths": "total_deaths",
    "new_deaths": "new_deaths",
    "recovered": "recovered",
    "active": "active",
    "bar_total_cases": "bar_total_cases"
}

# chart style options
STYLE_OPTIONS = [
    ("line", "Line"),
    ("scatter", "Scatter"),
    ("bar", "Bar"),
    ("area", "Area"),
    ("histogram", "Histogram"),
    ("box", "Box")
]

app = Dash(__name__)
app.layout = html.Div([
    html.H2("COVID-19 Interactive Dashboard (Plotly + Dash) - Kaggle Dataset"),
    html.Div([
        html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(id="country",
                         options=[{"label": c, "value": c} for c in countries],
                         value="India" if "India" in countries else countries[0],
                         clearable=False,
                         style={"width": "320px"})
        ], style={"display": "inline-block", "margin-right": "30px"}),

        html.Div([
            html.Label("Select Chart Type (Metric):"),
            dcc.Dropdown(id="chart-type",
                         options=[
                             {"label": "Total Cases Over Time", "value": "total_cases"},
                             {"label": "New Cases Over Time", "value": "new_cases"},
                             {"label": "Total Deaths Over Time", "value": "total_deaths"},
                             {"label": "New Deaths Over Time", "value": "new_deaths"},
                             {"label": "Recovered Over Time", "value": "recovered"},
                             {"label": "Active Cases Over Time", "value": "active"},
                             {"label": "Country Comparison - Top 20 Total Cases (Bar)", "value": "bar_total_cases"},
                         ],
                         value="total_cases",
                         clearable=False,
                         style={"width": "420px"})
        ], style={"display": "inline-block"})
    ], style={"margin-bottom": "10px"}),

    html.Div([
        html.Label("Select Chart Style:"),
        dcc.Dropdown(id="chart-style",
                     options=[{"label": lab, "value": val} for val, lab in STYLE_OPTIONS],
                     value="line",
                     clearable=False,
                     style={"width": "300px"})
    ], style={"margin-bottom": "10px"}),

    dcc.Graph(id="main-graph", style={"height": "700px"})
], style={"margin": "18px"})


@app.callback(
    Output("main-graph", "figure"),
    [Input("country", "value"),
     Input("chart-type", "value"),
     Input("chart-style", "value")]
)
def update_graph(country, chart_type, chart_style):
    # Special case: top-20 bar across countries
    if chart_type == "bar_total_cases":
        latest = df.sort_values("date").groupby("location").tail(1)
        latest = latest.dropna(subset=["total_cases"])
        top = latest.sort_values("total_cases", ascending=False).head(20)
        fig = px.bar(top, x="location", y="total_cases", title="Top 20 Countries by Total Confirmed Cases",
                     text="total_cases")
        fig.update_layout(xaxis_tickangle=-45)
        return fig

    # Standard country-level selection
    d = df[df["location"] == country].sort_values("date")
    col = CHARTS.get(chart_type, chart_type)

    # If metric column missing or no rows
    if d.empty or col not in d.columns:
        fig = px.line(title=f"No data available for {country} / {col}")
        return fig

    # Build figure based on style
    if chart_style == "line":
        fig = px.line(d, x="date", y=col, title=f"{col.replace('_',' ').title()} - {country}")
        fig.update_traces(mode="lines+markers")
        if col in ["new_cases", "new_deaths"]:
            d2 = d.set_index("date")
            d2["rolling7"] = d2[col].rolling(7, min_periods=1).mean()
            fig.add_scatter(x=d2.index, y=d2["rolling7"], mode="lines", name="7-day avg")
    elif chart_style == "scatter":
        fig = px.scatter(d, x="date", y=col, title=f"{col.replace('_',' ').title()} (Scatter) - {country}",
                         trendline=None)
    elif chart_style == "bar":
        fig = px.bar(d, x="date", y=col, title=f"{col.replace('_',' ').title()} (Bar) - {country}")
    elif chart_style == "area":
        fig = px.area(d, x="date", y=col, title=f"{col.replace('_',' ').title()} (Area) - {country}")
    elif chart_style == "histogram":
        # histogram of metric values for the chosen country (ignores date axis)
        fig = px.histogram(d, x=col, nbins=30, title=f"{col.replace('_',' ').title()} Distribution - {country}")
    elif chart_style == "box":
        fig = px.box(d, y=col, title=f"{col.replace('_',' ').title()} (Box) - {country}")
    else:
        fig = px.line(d, x="date", y=col, title=f"{col.replace('_',' ').title()} - {country}")

    fig.update_layout(hovermode="x unified")
    return fig


if __name__ == "__main__":
    app.run(debug=True)
