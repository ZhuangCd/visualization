from dash import Dash
from flask import send_from_directory

from .callbacks import register_callbacks
from .config import ASSETS_DIR, FONT_DIR
from .figures import default_trend_fig, default_world_map_fig
from .layout import build_layout


def create_app():
    world_map_fig = default_world_map_fig()
    trend_chart_fig = default_trend_fig()

    app = Dash(__name__, assets_folder=str(ASSETS_DIR))
    app.layout = build_layout(world_map_fig, trend_chart_fig)
    register_callbacks(app)

    @app.server.route("/fonts/<path:filename>")
    def serve_font(filename):
        return send_from_directory(FONT_DIR, filename)

    return app
