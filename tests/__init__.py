from typing import override

from calendardataviz import InspectorABC, RichString
import datetime as dt


class DummyInspector(InspectorABC):
    name = "dummy inspector"

    @override
    def color_for_date(self, _: dt.date) -> RichString:
        return RichString("d","#ff00ff", "#0000ff")

    @override
    def as_color_bar(self, size: int) -> list[RichString]:
        return [RichString("c", "#ff00ff", "#0000ff")] * size

    @override
    def popup_content(self, _: dt.date) -> tuple[str, str]:
        return "popup title", "popup content"
