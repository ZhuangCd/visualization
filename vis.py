import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html


# --------------------------------------
# Data prep
# --------------------------------------
raw_df = pd.read_csv("global_leader_ideologies.csv")


def normalize_democracy(series: pd.Series) -> pd.Series:
    normalized = series.astype(str).str.strip().str.lower()
    return normalized.where(normalized.isin(["yes", "no"]), "no data")


df = raw_df[["year", "hog_ideology", "region", "democracy"]].copy()
df["hog_ideology"] = df["hog_ideology"].str.lower()
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df["region"] = df["region"].fillna("Unknown")
df["democracy_flag"] = normalize_democracy(df["democracy"])

valid_ideologies = ["leftist", "centrist", "rightist"]
color_map = {
    "leftist": "#1d76db",
    "centrist": "#b094b0",
    "rightist": "#db231d",
}
FONT_FAMILY = "Omega, Arial, sans-serif"
CHOICE_LABEL_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "gap": "8px",
    "padding": "4px 0",
    "lineHeight": "1.3",
}

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


def _resolve_regions(selection):
    if not selection or "all" in selection:
        return None
    return selection


# --------------------------------------
# Figure factories
# --------------------------------------
def make_world_map(selected_regions=None, selected_year=None, democracy_filter="all"):
    filtered = map_df
    if selected_regions:
        filtered = filtered[filtered["region"].isin(selected_regions)]
    if democracy_filter and democracy_filter != "all":
        filtered = filtered[filtered["democracy_flag"] == democracy_filter]
    if selected_year is not None:
        filtered = filtered[filtered["year"] == selected_year]

    if filtered.empty:
        placeholder = map_df.groupby("country_name").size().reset_index(name="count")
        fig = px.scatter_geo(
            placeholder,
            locations="country_name",
            locationmode="country names",
            size="count",
            hover_name="country_name",
            size_max=20,
        )
    else:
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
        landcolor="#F0F0F0",
        showcountries=True,
        countrycolor="#ffffff",
        showframe=False,
    )
    if selected_regions:
        fig.update_geos(fitbounds="locations")
    else:
        fig.update_geos(fitbounds=None)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        font=dict(family=FONT_FAMILY),
    )
    return fig


def make_trend_chart(filtered_df, mode, selected_ideology):
    if mode == "single":
        ideology_df = filtered_df[filtered_df["hog_ideology"] == selected_ideology]
        yearly_counts = ideology_df.groupby("year").size().reset_index(name="count")
        fig = px.bar(
            yearly_counts,
            x="year",
            y="count",
            color_discrete_sequence=[color_map[selected_ideology]],
            opacity=0.75,
        )
    else:
        grouped = filtered_df[filtered_df["hog_ideology"].isin(valid_ideologies)]
        grouped = grouped.groupby(["year", "hog_ideology"]).size().reset_index(name="count")
        fig = px.bar(
            grouped,
            x="year",
            y="count",
            color="hog_ideology",
            barmode="group",
            color_discrete_map=color_map,
        )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=30, r=20, t=5, b=5),
        xaxis_title=None,
        yaxis_title=None,
        legend_title_text="Ideology" if mode != "single" else None,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY),
    )
    fig.update_xaxes(showticklabels=False, fixedrange=True, showgrid=False)
    fig.update_yaxes(showticklabels=False, fixedrange=True, showgrid=False, zeroline=False)
    return fig


# --------------------------------------
# Layout helpers
# --------------------------------------
def build_color_legend_items():
    return [
        html.Div(
            children=[
                html.Span(
                    style={
                        "display": "inline-block",
                        "width": "14px",
                        "height": "14px",
                        "borderRadius": "50%",
                        "backgroundColor": color_map[label],
                        "marginRight": "8px",
                    }
                ),
                html.Span(label.capitalize()),
            ],
            style={"display": "flex", "alignItems": "center", "marginBottom": "6px"},
        )
        for label in valid_ideologies
    ]


def build_sidebar():
    region_values = sorted(map_df["region"].dropna().unique())
    region_options = [{"label": "All", "value": "all"}] + [
        {"label": region.title(), "value": region}
        for region in region_values
    ]
    democracy_options = [
        {"label": "All regimes", "value": "all"},
        {"label": "Democracies", "value": "yes"},
        {"label": "Non-democracies", "value": "no"},
    ]

    return html.Div(
        id="sidebar",
        style={
            "width": "15%",
            "minWidth": "230px",
            "padding": "20px",
            "boxShadow": "2px 0 12px rgba(0,0,0,0.08)",
            "display": "flex",
            "flexDirection": "column",
            "gap": "18px",
            "overflowY": "auto",
            "overflowX": "hidden",
            "maxHeight": "100vh",
            "boxSizing": "border-box",
        },
        children=[
            html.H2("Global Ideologies", style={"margin": "0"}),
            html.Div([
                html.Label("Region", style={"fontSize": 16}),
                dcc.Checklist(
                    id="region_selector",
                    options=region_options,
                    value=["all"],
                    labelStyle=CHOICE_LABEL_STYLE,
                    inputStyle={"marginRight": "4px"},
                ),
            ]),
            html.Div([
                html.Label("Regime Type", style={"fontSize": 16}),
                dcc.RadioItems(
                    id="democracy_selector",
                    options=democracy_options,
                    value="all",
                    labelStyle=CHOICE_LABEL_STYLE,
                ),
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
                    labelStyle=CHOICE_LABEL_STYLE,
                ),
            ]),
            html.Div(
                id="single_selector_div",
                children=[
                    html.Label("Select Ideology", style={"fontSize": 16}),
                    dcc.RadioItems(
                        id="ideology_selector",
                        options=[{"label": ide.capitalize(), "value": ide} for ide in valid_ideologies],
                        value="leftist",
                        labelStyle=CHOICE_LABEL_STYLE,
                    ),
                ],
            ),
            html.Div([
                html.Label("Map Legend", style={"fontSize": 16}),
                html.Div(build_color_legend_items()),
            ]),
        ],
    )


# --------------------------------------
# Dash app
# --------------------------------------
MAP_CONFIG = {
    "displaylogo": False,
    "displayModeBar": False,
    "responsive": True,
    "scrollZoom": False,
}
TREND_CONFIG = {"displayModeBar": False, "staticPlot": True, "responsive": True}

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

default_world_map_fig = make_world_map(selected_year=max_year)

default_trend_fig = make_trend_chart(df.copy(), "single", "leftist")

app.layout = html.Div(
    style={
        "display": "flex",
        "height": "100vh",
        "width": "100vw",
        "margin": 0,
        "overflow": "hidden",
        "backgroundColor": "#ffffff00",
        "fontFamily": FONT_FAMILY,
    },
    children=[
        build_sidebar(),
        html.Div(
            id="main_panel",
            style={
                "flex": "1 1 auto",
                "height": "100vh",
                "display": "flex",
                "flexDirection": "column",
                "overflow": "hidden",
            },
            children=[
                dcc.Graph(
                    id="world_map",
                    figure=default_world_map_fig,
                    config=MAP_CONFIG,
                    style={
                        "flex": "1 1 85%",
                        "width": "100%",
                        "height": "100%",
                    },
                ),
                html.Div(
                    id="histogram_container",
                    style={
                        "flex": "0 0 25%",
                        "width": "100%",
                        "padding": "10px 30px 15px 30px",
                        "boxSizing": "border-box",
                        "backgroundColor": "transparent",
                        "boxShadow": "none",
                        "display": "flex",
                        "flexDirection": "column",
                    },
                    children=[
                        dcc.Graph(
                            id="trend_chart",
                            figure=default_trend_fig,
                            config=TREND_CONFIG,
                            style={
                                "flex": "1 1 auto",
                                "width": "100%",
                                "height": "100%",
                            },
                        ),
                        html.Div(
                            style={"paddingTop": "6px"},
                            children=[
                                dcc.Slider(
                                    id="year_slider",
                                    min=min_year if min_year is not None else 0,
                                    max=max_year if max_year is not None else 0,
                                    value=max_year if max_year is not None else 0,
                                    included=False,
                                    marks=year_marks if year_marks else {},
                                    step=1,
                                    tooltip={"always_visible": False, "placement": "bottom"},
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
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
def update_world_map(selected_regions, selected_democracy, selected_year):
    regions = _resolve_regions(selected_regions)
    year_value = int(selected_year) if selected_year is not None else max_year
    return make_world_map(regions, year_value, selected_democracy)


@app.callback(
    Output("trend_chart", "figure"),
    Output("single_selector_div", "style"),
    Input("mode", "value"),
    Input("ideology_selector", "value"),
    Input("region_selector", "value"),
    Input("democracy_selector", "value"),
)
def update_chart(mode, selected_ideology, selected_regions, selected_democracy):
    dropdown_style = {"display": "block"} if mode == "single" else {"display": "none"}

    filtered = df.copy()
    regions = _resolve_regions(selected_regions)
    if regions:
        filtered = filtered[filtered["region"].isin(regions)]
    if selected_democracy and selected_democracy != "all":
        filtered = filtered[filtered["democracy_flag"] == selected_democracy]

    fig = make_trend_chart(filtered, mode, selected_ideology)
    return fig, dropdown_style


if __name__ == "__main__":
    app.run(debug=True)
