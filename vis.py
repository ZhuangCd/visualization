import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# --------------------------------------
# Load data
# --------------------------------------
raw_df = pd.read_csv("global_leader_ideologies.csv")

def normalize_democracy(series):
    normalized = series.astype(str).str.strip().str.lower()
    return normalized.where(normalized.isin(["yes", "no"]), "no data")


df = raw_df[["year", "hog_ideology", "region", "democracy"]].copy()
df["hog_ideology"] = df["hog_ideology"].str.lower()
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df["region"] = df["region"].fillna("Unknown")
df["democracy_flag"] = normalize_democracy(df["democracy"]) 

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
map_df = raw_df[["country_name", "hog_ideology", "year", "region", "democracy"]].copy()
map_df["hog_ideology"] = map_df["hog_ideology"].str.lower()
map_df["year"] = pd.to_numeric(map_df["year"], errors="coerce").astype("Int64")
map_df = map_df[map_df["hog_ideology"].isin(valid_ideologies)]
map_df["democracy_flag"] = normalize_democracy(map_df["democracy"])
map_df = map_df.drop_duplicates(subset=["country_name", "year"], keep="last")

available_years = sorted(map_df["year"].dropna().unique())
min_year = int(min(available_years)) if available_years else None
max_year = int(max(available_years)) if available_years else None
year_marks = {
    int(y): str(int(y))
    for y in available_years
    if y == min_year or y == max_year or int(y) % 10 == 0
}

def make_world_map(selected_region="all", selected_year=None, democracy_filter="all"):
    filtered = map_df
    if selected_region and selected_region != "all":
        filtered = filtered[filtered["region"] == selected_region]
    if selected_year is not None:
        filtered = filtered[filtered["year"] == selected_year]
    if democracy_filter and democracy_filter != "all":
        filtered = filtered[filtered["democracy_flag"] == democracy_filter]

    if not filtered.empty:
        year_label = selected_year if selected_year is not None else "latest available"
        fig = px.choropleth(
            filtered,
            locations="country_name",
            locationmode="country names",
            color="hog_ideology",
            hover_name="country_name",
            hover_data={"year": True, "region": True},
            color_discrete_map=color_map,
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
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False
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
            size_max=40
    )

    fig.update_geos(showland=True, landcolor="#e0e0e0")

    fig.update_layout(
        width=1000,
        height=600,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False
    )
    return fig

default_world_map_fig = make_world_map(selected_year=max_year)

region_options = ["all"] + sorted(map_df["region"].dropna().unique())
democracy_options = [
    {"label": "All regimes", "value": "all"},
    {"label": "Democracies", "value": "yes"},
    {"label": "Non-democracies", "value": "no"},
]

# --------------------------------------
# Build Dash app
# --------------------------------------
app = Dash(__name__)
app.index_string = """
<!DOCTYPE html>
<html lang=\"en\" style=\"height:100%; overflow:hidden;\">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body style=\"margin:0; height:100%; overflow:hidden;\">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

MAP_CONFIG = {"displaylogo": False}
TREND_CONFIG = {"displayModeBar": False, "staticPlot": True}

app.layout = html.Div(
    style={
        "display": "flex",
        "height": "100%",
        "minHeight": "100vh",
        "width": "100%",
        "margin": "0",
        "overflow": "hidden",
        "backgroundColor": "#edf1f5"
    },
    children=[
        html.Div(
            id="sidebar",
            style={
                "width": "15%",
                "minWidth": "220px",
                "backgroundColor": "#ffffff",
                "padding": "20px",
                "boxShadow": "2px 0 12px rgba(0,0,0,0.08)",
                "display": "flex",
                "flexDirection": "column",
                "gap": "20px",
                "overflowY": "auto"
            },
            children=[
                html.H2("Global Ideologies", style={"margin": "0"}),
                html.P(
                    "Use the controls below to focus the map and histogram.",
                    style={"margin": "0", "color": "#6c757d"}
                ),
                html.Div([
                    html.Label("Continent / Region", style={"fontSize": 16}),
                    dcc.RadioItems(
                        id="region_selector",
                        options=[{"label": r, "value": r} for r in region_options],
                        value="all",
                        labelStyle={"display": "block", "marginBottom": "6px"}
                    )
                ]),
                html.Div([
                    html.Label("Regime Type", style={"fontSize": 16}),
                    dcc.RadioItems(
                        id="democracy_selector",
                        options=democracy_options,
                        value="all",
                        labelStyle={"display": "block", "marginBottom": "6px"}
                    )
                ]),
                html.Div([
                    html.Label("Display Mode", style={"fontSize": 16}),
                    dcc.RadioItems(
                        id="mode",
                        options=[
                            {"label": "Single Ideology", "value": "single"},
                            {"label": "All Ideologies", "value": "all"},
                        ],
                        value="single",
                        labelStyle={"display": "block", "marginBottom": "6px"}
                    )
                ]),
                html.Div(
                    id="single_selector_div",
                    children=[
                        html.Label("Select Ideology", style={"fontSize": 16}),
                        dcc.RadioItems(
                            id="ideology_selector",
                            options=[{"label": ide.capitalize(), "value": ide} for ide in valid_ideologies],
                            value="leftist",
                            labelStyle={"display": "block", "marginBottom": "6px"}
                        )
                    ]
                )
            ]
        ),
        html.Div(
            id="main_panel",
            style={
                "width": "85%",
                "height": "100%",
                "display": "flex",
                "flexDirection": "column",
                "overflow": "hidden",
                "boxSizing": "border-box"
            },
            children=[
                html.Div(
                    id="map_container",
                    style={
                        "flex": "0 0 55%",
                        "padding": "15px 30px 5px 30px",
                        "height": "55%",
                        "boxSizing": "border-box"
                    },
                    children=dcc.Graph(
                        id="world_map",
                        figure=default_world_map_fig,
                        config=MAP_CONFIG,
                        style={"height": "100%", "width": "100%", "borderRadius": "8px"}
                    )
                ),
                html.Div(
                    id="histogram_container",
                    style={
                        "flex": "0 0 45%",
                        "padding": "0 30px 10px 30px",
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "45%",
                        "boxSizing": "border-box"
                    },
                    children=[
                        dcc.Graph(
                            id="trend_chart",
                            config=TREND_CONFIG,
                            style={"height": "calc(100% - 60px)", "width": "100%"}
                        ),
                        html.Div([
                            html.Label("Select Year", style={"fontSize": 16, "marginBottom": "4px"}),
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
                        ], style={"paddingTop": "10px"})
                    ]
                )
            ]
        )
    ]
)


# --------------------------------------
# Callbacks
# --------------------------------------
@app.callback(
    Output("world_map", "figure"),
    Input("region_selector", "value"),
    Input("democracy_selector", "value"),
    Input("year_slider", "value"),
)
def update_world_map(selected_region, selected_democracy, selected_year):
    year_value = int(selected_year) if selected_year is not None else max_year
    return make_world_map(selected_region, year_value, selected_democracy)


@app.callback(
    Output("trend_chart", "figure"),
    Output("single_selector_div", "style"),
    Input("mode", "value"),
    Input("ideology_selector", "value"),
    Input("region_selector", "value"),
    Input("democracy_selector", "value"),
)
def update_chart(mode, selected_ideology, selected_region, selected_democracy):

    # Hide dropdown when "all" mode is used
    dropdown_style = {"display": "block"} if mode == "single" else {"display": "none"}

    filtered = df.copy()
    if selected_region and selected_region != "all":
        filtered = filtered[filtered["region"] == selected_region]
    if selected_democracy and selected_democracy != "all":
        filtered = filtered[filtered["democracy_flag"] == selected_democracy]

    if mode == "single":
        # ---------------------------
        # SINGLE IDEOLOGY VIEW
        # ---------------------------
        ideology_filtered = filtered[filtered["hog_ideology"] == selected_ideology]
        yearly_counts = ideology_filtered.groupby("year").size().reset_index(name="count")

        fig = px.bar(
            yearly_counts,
            x="year",
            y="count",
            color_discrete_sequence=[color_map[selected_ideology]],
            opacity=0.75
        )

        # Add trend line
        fig.add_traces(px.line(yearly_counts, x="year", y="count").update_traces(
            line=dict(color=color_map[selected_ideology])
        ).data)

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=60, r=30, t=20, b=10),
            xaxis_title=None,
            yaxis_title=None,
            title=None
        )
        fig.update_xaxes(showticklabels=False, fixedrange=True)
        fig.update_yaxes(showticklabels=False, fixedrange=True)
        return fig, dropdown_style

    else:
        # ---------------------------
        # ALL IDEOLOGIES VIEW
        # ---------------------------
        grouped = filtered[filtered["hog_ideology"].isin(valid_ideologies)]
        grouped = grouped.groupby(["year", "hog_ideology"]).size().reset_index(name="count")

        fig = px.bar(
            grouped,
            x="year",
            y="count",
            color="hog_ideology",
            barmode="group",
            color_discrete_map=color_map
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=60, r=30, t=20, b=10),
            xaxis_title=None,
            yaxis_title=None,
            legend_title_text="Ideology",
            title=None
        )
        fig.update_xaxes(showticklabels=False, fixedrange=True)
        fig.update_yaxes(showticklabels=False, fixedrange=True)
        return fig, dropdown_style


# --------------------------------------
# Run app
# --------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
