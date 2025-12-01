from dash import dcc, html

from .config import (
    CHOICE_LABEL_STYLE,
    COLOR_MAP,
    DATASET_SOURCE_URL,
    INFO_SECTIONS,
    INSTRUCTION_STEPS,
    SECTION_LABEL_STYLE,
)
from .helpers import format_democracy, pref_value, safe_text, political_leaning


def build_ideology_options(valid_ideologies):
    return [
        {
            "label": html.Span(
                [
                    html.Span(
                        style={
                            "display": "inline-block",
                            "width": "12px",
                            "height": "12px",
                            "borderRadius": "2px",
                            "backgroundColor": COLOR_MAP[ide],
                            "marginRight": "8px",
                        }
                    ),
                    html.Span(ide.capitalize()),
                ],
                style={"display": "flex", "alignItems": "center"},
            ),
            "value": ide,
        }
        for ide in valid_ideologies
    ]


def build_sidebar(regions, ideology_options):
    region_options = [{"label": "All", "value": "all"}] + [
        {"label": region.title(), "value": region} for region in regions
    ]
    democracy_options = [
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
            html.H3("Global Ideologies", style={"margin": "0"}),
            html.Div(
                [
                    html.Label("Region", style=SECTION_LABEL_STYLE),
                    dcc.Checklist(
                        id="region_selector",
                        options=region_options,
                        value=[],
                        labelStyle=CHOICE_LABEL_STYLE,
                        inputStyle={"marginRight": "4px"},
                    ),
                ]
            ),
            html.Div(
                [
                    html.Label("Regime Type", style=SECTION_LABEL_STYLE),
                    dcc.Checklist(
                        id="democracy_selector",
                        options=democracy_options,
                        value=[],
                        labelStyle=CHOICE_LABEL_STYLE,
                        inputStyle={"marginRight": "4px"},
                    ),
                ]
            ),
            html.Div(
                [
                    html.Label("Ideology", style=SECTION_LABEL_STYLE),
                    dcc.Checklist(
                        id="ideology_selector",
                        options=ideology_options,
                        value=[],
                        labelStyle={**CHOICE_LABEL_STYLE, "gap": "12px"},
                        inputStyle={"marginRight": "4px"},
                        className="ideology-checklist",
                    ),
                ]
            ),
        ],
    )


def build_overlay(overlay_id, backdrop_id, close_id, content, modal_id=None):
    return html.Div(
        id=overlay_id,
        className="summary-overlay hidden",
        children=[
            html.Div(id=backdrop_id, className="summary-backdrop", n_clicks=0),
            html.Div(
                id=modal_id,
                className="summary-modal",
                children=[
                    html.Button("×", id=close_id, className="summary-close", n_clicks=0),
                    content,
                ],
            ),
        ],
    )


def build_summary_card(country, year, row):
    if row is None:
        message = f"No political summary available for {country or 'the selected country'} in {year or 'this year'}."
        return html.Div(
            className="summary-card",
            children=[html.Div(message, className="summary-empty")],
        )

    fields = [
        ("Country", safe_text(country)),
        ("Year", safe_text(year)),
        ("Democracy", format_democracy(row)),
        ("Political leaning", political_leaning(row)),
        ("Head of Government", safe_text(row.get("hog"))),
        ("HoG Party", pref_value(row, "hog_party_eng", "hog_party")),
        ("Leader", safe_text(row.get("leader"))),
        ("Leader Party", pref_value(row, "leader_party_eng", "leader_party")),
        ("Region", safe_text(row.get("region"))),
    ]

    return html.Div(
        className="summary-card",
        children=[
            html.H3("Political Snapshot", className="summary-title"),
            html.Div(
                [
                    html.Div(
                        className="summary-field",
                        children=[
                            html.Span(f"{label}:", className="summary-label"),
                            html.Span(value, className="summary-value"),
                        ],
                    )
                    for label, value in fields
                ]
            ),
        ],
    )


def build_info_card():
    info_fields = [
        ("Project name", INFO_SECTIONS["Project name"]),
        ("Research questions", INFO_SECTIONS["Research questions"]),
        (
            "Sources",
            html.Span(
                [
                    html.A(
                        "Identifying Ideologues: A Global Dataset on Political Leaders, 1945-2019, Bastian Herre",
                        href=INFO_SECTIONS["Sources"],
                        target="_blank",
                        className="summary-link",
                    ),
                    html.Span(" — "),
                    html.A(
                        "Dataset (GitHub)",
                        href=DATASET_SOURCE_URL,
                        target="_blank",
                        className="summary-link",
                    ),
                ]
            ),
        ),
        ("Made by", INFO_SECTIONS["Made by"]),
    ]

    return html.Div(
        className="summary-card",
        children=[
            html.H3("Project Information", className="summary-title"),
            html.Div(
                [
                    html.Div(
                        className="summary-field",
                        children=[
                            html.Span(f"{label}:", className="summary-label"),
                            html.Span(value, className="summary-value"),
                        ],
                    )
                    for label, value in info_fields
                ]
            ),
            html.H4("Website instructions", className="summary-subtitle"),
            html.Ul(
                [html.Li(step, className="summary-instruction") for step in INSTRUCTION_STEPS],
                className="summary-list",
            ),
        ],
    )
