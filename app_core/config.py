from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "global_leader_ideologies.csv"
FONT_DIR = (BASE_DIR / "fonts" / "monument-grotesk-font-family-1764226824-0").resolve()
ASSETS_DIR = (BASE_DIR / "assets").resolve()

SUMMARY_COLUMNS = [
    "hog",
    "hog_party",
    "hog_party_eng",
    "leader",
    "leader_party",
    "leader_party_eng",
    "hog_left",
    "hog_center",
    "hog_right",
]

VALID_IDEOLOGIES = ["leftist", "centrist", "rightist"]
COLOR_MAP = {
    "leftist": "#1d76db",
    "centrist": "#b094b0",
    "rightist": "#db231d",
}
GREY_STAGE_COLORS = {
    1: "#dcdcdc",
    2: "#b7b6b6",
    3: "#8c8b8b",
}
FONT_FAMILY = "ABCMonumentGrotesk, Arial, sans-serif"
CHOICE_LABEL_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "gap": "8px",
    "padding": "4px 0",
    "lineHeight": "1.3",
}
SECTION_LABEL_STYLE = {"fontSize": 16, "fontWeight": 600}
HOVER_TEMPLATE = "<b>%{location}</b><br>Click for political summary<extra></extra>"
HOVER_LABEL_STYLE = {
    "bgcolor": "#ffffff",
    "bordercolor": "#d7d7d7",
    "font": {"family": FONT_FAMILY, "color": "#111", "size": 12},
}
INFO_SECTIONS = {
    "Project name": "Global Ideology Explorer",
    "Research questions": "How do geography, regime type, and ideology intersect across modern leadership history?",
    "Sources": "https://www.ippapublicpolicy.org/file/paper/60c247759f1df.pdf",
    "Made by": "William Kosse, Márton Berettyán, Nóra Balogh",
}
DATASET_SOURCE_URL = "https://github.com/bastianherre/global-leader-ideologies"
INSTRUCTION_STEPS = [
    "Pick one or more regions to activate the workflow.",
    "Choose a regime type to focus the dataset.",
    "Select at least one ideology to reveal ideological splits.",
    "Lock a specific year on the slider to unlock the full-color map view.",
]
MAP_CONFIG = {
    "displaylogo": False,
    "displayModeBar": False,
    "responsive": True,
    "scrollZoom": False,
}
TREND_CONFIG = {"displayModeBar": False, "staticPlot": True, "responsive": True}
GRAPH_FULL_STYLE = {"width": "100%", "height": "100%"}
