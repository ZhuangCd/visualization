import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# --------------------------------------
# Load data
# --------------------------------------
raw_df = pd.read_csv("global_leader_ideologies.csv")

df = raw_df[["year", "hog_ideology"]]
df["hog_ideology"] = df["hog_ideology"].str.lower()
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

valid_ideologies = ["leftist", "centrist", "rightist"]

# Color map
color_map = {
    "leftist": "#2067CA",    # blue
    "centrist": "#F1C40F",   # yellow
    "rightist": "#C00C1B"    # red
}

# --------------------------------------
# Default world map plot
# --------------------------------------
map_df = raw_df[["country_name", "hog_ideology", "year", "region"]].copy()
map_df["hog_ideology"] = map_df["hog_ideology"].str.lower()
map_df["year"] = pd.to_numeric(map_df["year"], errors="coerce").astype("Int64")
map_df = map_df[map_df["hog_ideology"].isin(valid_ideologies)]
map_df = map_df.drop_duplicates(subset=["country_name", "year"], keep="last")

available_years = sorted(map_df["year"].dropna().unique())
min_year = int(min(available_years)) if available_years else None
max_year = int(max(available_years)) if available_years else None
year_marks = {
    int(y): str(int(y))
    for y in available_years
    if y == min_year or y == max_year or int(y) % 10 == 0
}

def make_world_map(selected_region="all", selected_year=None):
    filtered = map_df
    if selected_region and selected_region != "all":
        filtered = map_df[map_df["region"] == selected_region]
    if selected_year is not None:
        filtered = filtered[filtered["year"] == selected_year]

    if not filtered.empty:
        year_label = selected_year if selected_year is not None else "latest available"
        title_text = f"Head-of-Government Ideology by Country (year: {year_label})"
        fig = px.choropleth(
            filtered,
            locations="country_name",
            locationmode="country names",
            color="hog_ideology",
            hover_name="country_name",
            hover_data={"year": True, "region": True},
            color_discrete_map=color_map,
            title=title_text,
        )

        fig.update_geos(
            showland=True,
            landcolor="#e0e0e0",
            showcountries=True,
            countrycolor="#ffffff",
            fitbounds="locations"
        )

        fig.update_layout(
            width=1000,
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        return fig

    country_counts = raw_df.groupby("country_name").size().reset_index(name="Count")
    country_counts = country_counts.rename(columns={"country_name": "Country"})

    fig = px.scatter_geo(
        country_counts,
        locations="Country",
        locationmode="country names",
        size="Count",
        hover_name="Country",
        size_max=40,
        title="Records per Country"
    )

    fig.update_geos(showland=True, landcolor="#e0e0e0")

    fig.update_layout(
        width=1000,
        height=600,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig

default_world_map_fig = make_world_map(selected_year=max_year)

region_options = ["all"] + sorted(map_df["region"].dropna().unique())

# --------------------------------------
# Build Dash app
# --------------------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Political Ideology Trends Over Time", style={"textAlign": "center"}),

    html.Div([
        html.Label("Filter by Region:", style={"fontSize": 18}),
        dcc.Dropdown(
            id="region_selector",
            options=[{"label": r, "value": r} for r in region_options],
            value="all",
            clearable=False,
            style={"width": "40%", "marginBottom": "20px"}
        )
    ]),

    dcc.Graph(
        id="world_map",
        figure=default_world_map_fig,
        style={"marginBottom": "0px", "paddingBottom": "0px"}
    ),

    html.Div([
        html.Label("Display mode:", style={"fontSize": 18}),
        dcc.RadioItems(
            id="mode",
            options=[
                {"label": "Single Ideology", "value": "single"},
                {"label": "All Ideologies", "value": "all"},
            ],
            value="single",
            inline=True,
            style={"marginBottom": "20px"}
        )
    ]),

    html.Div([
        html.Label("Select Ideology:", style={"fontSize": 18}),
        dcc.Dropdown(
            id="ideology_selector",
            options=[{"label": ide.capitalize(), "value": ide} for ide in valid_ideologies],
            value="leftist",
            clearable=False,
            style={"width": "40%"}
        )
    ], id="single_selector_div"),

    dcc.Graph(id="trend_chart", style={"marginBottom": "-5px"}),

    html.Div([
        html.Label("Select Year:", style={"fontSize": 18, "marginBottom": "4px"}),
        dcc.Slider(
            id="year_slider",
            min=min_year if min_year is not None else 0,
            max=max_year if max_year is not None else 0,
            value=max_year if max_year is not None else 0,
            included=False,
            marks=year_marks if year_marks else {},
            step=1,
            tooltip={"always_visible": False, "placement": "bottom"}
        )
    ], style={"marginTop": "-25px", "paddingTop": "0px", "marginBottom": "0px", "paddingBottom": "0px"})
])


# --------------------------------------
# Callbacks
# --------------------------------------
@app.callback(
    Output("world_map", "figure"),
    Input("region_selector", "value"),
    Input("year_slider", "value"),
)
def update_world_map(selected_region, selected_year):
    year_value = int(selected_year) if selected_year is not None else max_year
    return make_world_map(selected_region, year_value)


@app.callback(
    Output("trend_chart", "figure"),
    Output("single_selector_div", "style"),
    Input("mode", "value"),
    Input("ideology_selector", "value"),
)
def update_chart(mode, selected_ideology):

    # Hide dropdown when "all" mode is used
    dropdown_style = {"display": "block"} if mode == "single" else {"display": "none"}

    if mode == "single":
        # ---------------------------
        # SINGLE IDEOLOGY VIEW
        # ---------------------------
        filtered = df[df["hog_ideology"] == selected_ideology]
        yearly_counts = filtered.groupby("year").size().reset_index(name="count")

        fig = px.bar(
            yearly_counts,
            x="year",
            y="count",
            title=f"{selected_ideology.capitalize()} Governments Over Time",
            color_discrete_sequence=[color_map[selected_ideology]],
            opacity=0.75
        )

        # Add trend line
        fig.add_traces(px.line(yearly_counts, x="year", y="count").update_traces(
            line=dict(color=color_map[selected_ideology])
        ).data)

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=60, r=30, t=60, b=10),
            xaxis_title=None,
            yaxis_title=None
        )
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        return fig, dropdown_style

    else:
        # ---------------------------
        # ALL IDEOLOGIES VIEW
        # ---------------------------
        grouped = df[df["hog_ideology"].isin(valid_ideologies)]
        grouped = grouped.groupby(["year", "hog_ideology"]).size().reset_index(name="count")

        fig = px.bar(
            grouped,
            x="year",
            y="count",
            color="hog_ideology",
            barmode="group",
            title="All Ideologies Over Time (Side-by-Side Bars)",
            color_discrete_map=color_map
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=60, r=30, t=60, b=10),
            xaxis_title=None,
            yaxis_title=None,
            legend_title_text="Ideology"
        )
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        return fig, dropdown_style


# --------------------------------------
# Run app
# --------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
