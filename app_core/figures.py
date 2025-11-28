import plotly.express as px
import plotly.graph_objects as go

from .config import (
    COLOR_MAP,
    FONT_FAMILY,
    GREY_STAGE_COLORS,
    HOVER_LABEL_STYLE,
    HOVER_TEMPLATE,
    VALID_IDEOLOGIES,
)
from .data import df, map_df
from .helpers import apply_multi_filter, prepare_stage_highlight, resolve_ideologies


def make_world_map(
    stage,
    selected_regions=None,
    selected_year=None,
    democracy_filters=None,
    ideology_filters=None,
    has_region_selection=False,
):
    filtered = map_df
    if selected_regions:
        filtered = filtered[filtered["region"].isin(selected_regions)]

    if stage == 4:
        filtered = apply_multi_filter(filtered, "democracy_flag", democracy_filters)
        filtered = apply_multi_filter(filtered, "hog_ideology", ideology_filters)
        if selected_year is not None:
            filtered = filtered[filtered["year"] == selected_year]

    if stage == 4 and selected_year is not None and not filtered.empty:
        fig = px.choropleth(
            filtered,
            locations="country_name",
            locationmode="country names",
            color="hog_ideology",
            color_discrete_map=COLOR_MAP,
        )
    else:
        highlight_df = prepare_stage_highlight(
            stage,
            map_df,
            selected_regions,
            democracy_filters,
            ideology_filters,
            has_region_selection,
        )
        if highlight_df.empty:
            fig = go.Figure()
            fig.add_trace(
                go.Choropleth(locations=[], z=[], showscale=False, hoverinfo="skip")
            )
        else:
            stage_label = f"stage_{stage}"
            highlight_df = highlight_df.assign(stage_label=stage_label)
            fig = px.choropleth(
                highlight_df,
                locations="country_name",
                locationmode="country names",
                color="stage_label",
                color_discrete_map={stage_label: GREY_STAGE_COLORS.get(stage, "#dddddd")},
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
    if fig.data:
        fig.update_traces(hovertemplate=HOVER_TEMPLATE, hoverlabel=HOVER_LABEL_STYLE)
    return fig


def make_trend_chart(filtered_df, selected_ideologies):
    ideologies = resolve_ideologies(selected_ideologies)
    if not ideologies:
        fig = go.Figure()
    elif len(ideologies) == 1:
        ideology = ideologies[0]
        ideology_df = filtered_df[filtered_df["hog_ideology"] == ideology]
        yearly_counts = ideology_df.groupby("year").size().reset_index(name="count")
        fig = px.bar(
            yearly_counts,
            x="year",
            y="count",
            color_discrete_sequence=[COLOR_MAP[ideology]],
        )
    else:
        grouped = filtered_df[filtered_df["hog_ideology"].isin(ideologies)]
        grouped = grouped.groupby(["year", "hog_ideology"]).size().reset_index(name="count")
        fig = px.bar(
            grouped,
            x="year",
            y="count",
            color="hog_ideology",
            barmode="group",
            color_discrete_map=COLOR_MAP,
        )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=30, r=20, t=5, b=5),
        xaxis_title=None,
        yaxis_title=None,
        legend_title_text="Ideology" if len(ideologies) > 1 else None,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY),
        bargap=0,
        bargroupgap=0,
    )
    fig.update_xaxes(showticklabels=False, fixedrange=True, showgrid=False)
    fig.update_yaxes(showticklabels=False, fixedrange=True, showgrid=False, zeroline=False)
    return fig


def default_world_map_fig():
    return make_world_map(stage=0)


def default_trend_fig():
    return make_trend_chart(df, VALID_IDEOLOGIES)
