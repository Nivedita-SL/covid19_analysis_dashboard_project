# bokeh_app.py  (Bokeh server) - adapted for Kaggle CSV
import pandas as pd
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Select
from bokeh.plotting import figure
from bokeh.layouts import column, row

DATA_PATH = "covid_19_clean_complete.csv"

df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
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
chart_options = [
    ("total_cases","Total Cases Over Time"),
    ("new_cases","New Cases Over Time"),
    ("total_deaths","Total Deaths Over Time"),
    ("new_deaths","New Deaths Over Time"),
    ("recovered","Recovered Over Time"),
    ("active","Active Cases Over Time")
]

country_select = Select(title="Country", value=countries[0] if countries else "", options=countries)
chart_select = Select(title="Chart Type", value="total_cases", options=[c[0] for c in chart_options])

initial = df[df["location"]==country_select.value].sort_values("date")
source = ColumnDataSource(data=dict(date=initial["date"], y=initial["total_cases"] if "total_cases" in initial else []))

p = figure(x_axis_type="datetime", height=450, width=900, title="COVID Chart",
           tools="pan,wheel_zoom,box_zoom,reset,hover,save")
line = p.line("date","y", source=source, line_width=2)

def update_data():
    c = country_select.value
    chart = chart_select.value
    newdf = df[df["location"]==c].sort_values("date")
    if newdf.empty or chart not in newdf.columns:
        source.data = dict(date=[], y=[])
        p.title.text = f"No data for {c}"
        return
    source.data = dict(date=newdf["date"], y=newdf[chart])
    p.title.text = f"{chart.replace('_',' ').title()} - {c}"

def on_change(attr, old, new):
    update_data()

country_select.on_change("value", on_change)
chart_select.on_change("value", on_change)

layout = column(row(country_select, chart_select), p)
curdoc().add_root(layout)
curdoc().title = "COVID Bokeh Dashboard"
