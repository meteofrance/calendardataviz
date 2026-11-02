from collections.abc import Callable
import TermTk as ttk
from typing_extensions import Any, override
import datetime as dt
from traceback import format_exception

from calendardataviz.rich_string import RichStringType


class PopupWindowWidget(ttk.TTkWindow):
    """Popup window, with a scroll area."""

    def __init__(
        self,
        text: RichStringType,
        title: RichStringType,
        origin_fnc: Callable[[dt.date], tuple[RichStringType, RichStringType]],
        date: dt.date,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            text: Content of the popup's body.
            distance_to_screen_bottom: Used to compute the
                window's allowed height.
            title: Title of the popup window.
            args: Arguments passed to the ttk.TTkWindow parent class.
            kwargs: Arguments passed to the ttk.TTkWindow parent class.
        """

        self._origin_fnc = origin_fnc
        self._date = date

        width: int = max(len(line) for line in text.split("\n")) + 7
        width = max(width, len(title) + 7)
        height: int = len(text.split("\n")) + 4
        if "title" in kwargs:
            width = max(width, len(kwargs["title"]) + 3)

        super().__init__(
            size=(width, height),
            title=title,
            flags=ttk.TTkK.WindowFlag.WindowCloseButtonHint,
            *args,
            **kwargs,
        )

        self._content = ttk.TTkLabel(
            parent=self,
            text=text,
        )

    def reload(self) -> None:
        """Called after the popup parent calendar's reload method is called."""

        # Get the description for the date, otherwise, format error
        content = f"Reloaded {dt.datetime.now().strftime('%H:%M:%S')}\n\n"
        try:
            title, given_content = self._origin_fnc(self._date)
            if given_content == "":
                content += "No popup content provided."
            else:
                content += given_content
        except Exception as e:
            title = f"ERROR for {self._date}"
            content += "".join(format_exception(e))
        self.setTitle(title)
        self._content.setText(content)

    @override
    def resizeEvent(self, w: int, h: int) -> None:
        """Override to stop resizing."""
        return
