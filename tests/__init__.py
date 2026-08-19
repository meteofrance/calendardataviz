"""Helper classes and function for the test suite."""

import datetime as dt

from calendardataviz import InspectorABC, RichString
from typing_extensions import override


class DummyInspector(InspectorABC):
    """Dummy inspector, returns only one color"""

    name = "dummy inspector"

    @override
    def color_for_date(self, date: dt.date) -> RichString:
        return RichString("d", "#ff00ff", "#0000ff")

    @override
    def as_color_bar(self, size: int) -> list[RichString]:
        return [RichString("c", "#ff00ff", "#0000ff")] * size

    @override
    def popup_content(self, date: dt.date) -> tuple[str, str]:
        return "popup title", "popup content"
