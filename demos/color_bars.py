import datetime as dt
from typing import override

import TermTk as ttk

from calendardataviz.colors import (
    CIVIDIS,
    COOLWARM,
    INFERNO,
    JET,
    MAGMA,
    PLASMA,
    RDYLGN,
    SPECTRAL,
    TURBO,
    VIRIDIS,
    color_from_pct,
)
from calendardataviz.inspector_abc import InspectorABC
from calendardataviz.rich_string import RichString
from calendardataviz.widgets.colorbar import ColorBarWidget


class ColorBarInspector(InspectorABC):
    """Inspector made to visualize a colorbar."""

    def __init__(self, colors: list[RichString], name: str) -> None:
        """
        Args:
            colors: List of colors, can be taken from``calendardataviz.colors`.
            name: Name of the colorbar.
        """
        self._colors = colors
        self.name = name

    @override
    def color_for_date(self, date: dt.date) -> RichString:
        raise NotImplementedError

    @override
    def popup_content(self, date: dt.date) -> tuple[str, str]:
        raise NotImplementedError

    @override
    def as_color_bar(self, size: int) -> list[RichString]:

        colors = [color_from_pct(i / (size - 1), self._colors) for i in range(size)]

        return colors


# Associate colors to their names
colors = {
    "VIRIDIS": VIRIDIS,
    "PLASMA": PLASMA,
    "INFERNO": INFERNO,
    "MAGMA": MAGMA,
    "CIVIDIS": CIVIDIS,
    "TURBO": TURBO,
    "COOLWARM": COOLWARM,
    "RDYLGN": RDYLGN,
    "SPECTRAL": SPECTRAL,
    "JET": JET,
}

# Instantiate an inspector for each color bar
inspectors = [ColorBarInspector(color, name) for name, color in colors.items()]

# Instantiate the app's widgets
root = ttk.TTk(name="root", layout=ttk.TTkLayout())
scroll_area = ttk.TTkScrollArea(
    name="scroll_area",
    parent=root,
    pos=(0, 0),
    size=root.size(),
    visible=True,
    verticalScrollBarPolicy=ttk.TTkK.ScrollBarAlwaysOff,
    horizontalScrollBarPolicy=ttk.TTkK.ScrollBarAsNeeded,
)

# Window title
ttk.TTkLabel(
    name="window_title",
    parent=scroll_area.viewport(),
    pos=(0, 0),
    size=(root.width(), 1),
    alignment=ttk.TTkConstant.Alignment.LEFT_ALIGN,
)

# Color bars
for i, inspector in enumerate(inspectors):
    ttk.TTkLabel(
        text=f"{inspector.name}",
        name=f"color_bar_{i}",
        parent=scroll_area.viewport(),
        pos=(i * 10 + 2, 1),
        size=(10, 1),
        alignment=ttk.TTkConstant.Alignment.LEFT_ALIGN,
    )
    ColorBarWidget(
        name="color_bar",
        inspector=inspector,
        parent=scroll_area.viewport(),
        size=(10, root.height() - 4),
        pos=(i * 10 + 4, 2),
    )

root.mainloop()
