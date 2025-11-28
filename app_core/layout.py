from dash import dcc, html

from .components import (
    build_ideology_options,
    build_info_card,
    build_overlay,
    build_sidebar,
)
from .config import FONT_FAMILY, GRAPH_FULL_STYLE, MAP_CONFIG, TREND_CONFIG, VALID_IDEOLOGIES
from .data import map_df, max_year, min_year, year_marks


def build_layout(default_world_map, default_trend_chart):
    regions = sorted(map_df["region"].dropna().unique())
    ideology_options = build_ideology_options(VALID_IDEOLOGIES)

    return html.Div(
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
            dcc.Store(id="year_confirmed", data=False),
            build_overlay(
                overlay_id="summary_overlay",
                backdrop_id="summary_backdrop",
                close_id="summary_close",
                content=html.Div(id="summary_modal_content", className="summary-modal-content"),
                modal_id="summary_modal",
            ),
            build_overlay(
                overlay_id="info_overlay",
                backdrop_id="info_backdrop",
                close_id="info_close",
                content=build_info_card(),
                modal_id="info_modal",
            ),
            build_sidebar(regions, ideology_options),
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
                    html.Div(
                        id="map_container",
                        style={
                            "flex": "1 1 85%",
                            "width": "100%",
                            "height": "100%",
                            "position": "relative",
                        },
                        children=[
                            dcc.Graph(
                                id="world_map",
                                figure=default_world_map,
                                config=MAP_CONFIG,
                                style=GRAPH_FULL_STYLE,
                            ),
                            html.Button("info", id="info_button", className="info-button", n_clicks=0),
                        ],
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
                                figure=default_trend_chart,
                                config=TREND_CONFIG,
                                style={"flex": "1 1 auto", **GRAPH_FULL_STYLE},
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
