from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate

from .components import build_summary_card
from .data import df, map_df
from .figures import make_trend_chart, make_world_map
from .helpers import (
    apply_multi_filter,
    compute_stage,
    extract_summary_row,
    resolve_ideologies,
    resolve_regions,
)


def register_callbacks(app):
    @app.callback(Output("year_confirmed", "data"), Input("year_slider", "value"))
    def flag_year_confirmation(selected_year):  # pylint: disable=unused-argument
        if ctx.triggered_id is None:
            return False
        return True

    @app.callback(
        Output("info_overlay", "className"),
        Input("info_button", "n_clicks"),
        Input("info_close", "n_clicks"),
        Input("info_backdrop", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_info_modal(info_click, close_click, backdrop_click):  # pylint: disable=unused-argument
        trigger = ctx.triggered_id
        if trigger in {"info_close", "info_backdrop"}:
            return "summary-overlay hidden"
        if trigger == "info_button":
            return "summary-overlay visible"
        raise PreventUpdate

    @app.callback(
        Output("summary_modal_content", "children"),
        Output("summary_overlay", "className"),
        Input("world_map", "clickData"),
        Input("summary_close", "n_clicks"),
        Input("summary_backdrop", "n_clicks"),
        State("year_slider", "value"),
        prevent_initial_call=True,
    )
    def toggle_summary_modal(click_data, close_clicks, backdrop_clicks, selected_year):  # pylint: disable=unused-argument
        trigger = ctx.triggered_id

        if trigger in {"summary_close", "summary_backdrop"}:
            return [], "summary-overlay hidden"

        if trigger == "world_map" and click_data:
            point = (click_data.get("points") or [{}])[0]
            country = point.get("location") or point.get("hovertext")
            year_value = int(selected_year) if selected_year is not None else None
            row = extract_summary_row(map_df, country, year_value)
            content = build_summary_card(country, year_value, row)
            return content, "summary-overlay visible"

        raise PreventUpdate

    @app.callback(
        Output("world_map", "figure"),
        Input("region_selector", "value"),
        Input("democracy_selector", "value"),
        Input("year_slider", "value"),
        Input("ideology_selector", "value"),
        Input("year_confirmed", "data"),
    )
    def update_world_map(selected_regions, selected_democracy, selected_year, selected_ideologies, year_confirmed):
        regions = resolve_regions(selected_regions)
        has_region_selection = bool(selected_regions)
        ideology_filters = resolve_ideologies(selected_ideologies)
        stage = compute_stage(has_region_selection, selected_democracy, ideology_filters, year_confirmed)
        year_value = int(selected_year) if (stage == 4 and selected_year is not None) else None
        return make_world_map(
            stage,
            regions,
            year_value,
            selected_democracy,
            ideology_filters,
            has_region_selection,
        )

    @app.callback(
        Output("trend_chart", "figure"),
        Input("region_selector", "value"),
        Input("democracy_selector", "value"),
        Input("ideology_selector", "value"),
    )
    def update_chart(selected_regions, selected_democracy, selected_ideologies):
        filtered = df
        regions = resolve_regions(selected_regions)
        if regions:
            filtered = filtered[filtered["region"].isin(regions)]
        filtered = apply_multi_filter(filtered, "democracy_flag", selected_democracy)

        fig = make_trend_chart(filtered, selected_ideologies)
        return fig
