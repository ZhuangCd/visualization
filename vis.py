import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# --------------------------------------
# Load data
# --------------------------------------
df = pd.read_csv("global_leader_ideologies.csv")

df = df[["year", "hog_ideology"]]
df["hog_ideology"] = df["hog_ideology"].str.lower()

valid_ideologies = ["leftist", "centrist", "rightist"]

# Color map
color_map = {
    "leftist": "#2067CA",    # blue
    "centrist": "#F1C40F",   # yellow
    "rightist": "#C00C1B"    # red
}

# --------------------------------------
# Build Dash app
# --------------------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Political Ideology Trends Over Time", style={"textAlign": "center"}),

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

    dcc.Graph(id="trend_chart")
])


# --------------------------------------
# Callbacks
# --------------------------------------
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
            labels={"count": "Number of Countries"},
            color_discrete_sequence=[color_map[selected_ideology]],
            opacity=0.75
        )

        # Add trend line
        fig.add_traces(px.line(yearly_counts, x="year", y="count").update_traces(
            line=dict(color=color_map[selected_ideology])
        ).data)

        fig.update_layout(template="plotly_white")
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
            labels={"count": "Number of Countries", "hog_ideology": "Ideology"},
            color_discrete_map=color_map
        )

        fig.update_layout(template="plotly_white")
        return fig, dropdown_style


# --------------------------------------
# Run app
# --------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
