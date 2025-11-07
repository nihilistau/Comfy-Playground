from __future__ import annotations

import json
from typing import Dict, List, Optional

import ipywidgets as widgets
from IPython.display import display


def accordion_from_sections(sections: Dict[str, widgets.Widget]) -> widgets.Accordion:
    items = list(sections.items())
    accordion = widgets.Accordion(children=[widget for _, widget in items])
    for idx, (title, _) in enumerate(items):
        accordion.set_title(idx, title)
    return accordion


def control_board(environment: Dict[str, object], downloads: widgets.Widget, flows: widgets.Widget, voice: widgets.Widget, utilities: widgets.Widget) -> widgets.Tab:
    env_details = widgets.HTML(
        value=f"<pre>{json.dumps(environment, indent=2)}</pre>",
        layout=widgets.Layout(max_height="280px", overflow_y="auto"),
    )
    tabs = widgets.Tab(children=[env_details, downloads, flows, voice, utilities])
    for idx, title in enumerate(["Environment", "Downloads", "Flow Studio", "Voice Lab", "Utilities"]):
        tabs.set_title(idx, title)
    return tabs


def checklist(items: List[str]) -> widgets.VBox:
    return widgets.VBox([widgets.HTML(f"<li>{item}</li>") for item in items])


def toast(message: str, level: str = "info") -> None:
    color = {
        "info": "#209cee",
        "success": "#23d160",
        "warning": "#ffdd57",
        "error": "#ff3860",
    }.get(level, "#209cee")
    panel = widgets.HTML(
        value=f"<div style='border-left:4px solid {color};padding:8px;margin:5px 0;background:#1f1f1f;color:#fff;'>{message}</div>"
    )
    display(panel)
