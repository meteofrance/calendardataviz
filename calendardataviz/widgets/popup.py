import TermTk as ttk
from typing_extensions import Any, override

from calendardataviz.rich_string import RichStringType


class PopupWindowWidget(ttk.TTkWindow):
    """Popup window, with a scroll area."""

    def __init__(
        self,
        text: RichStringType,
        title: RichStringType,
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

        ttk.TTkLabel(
            parent=self,
            text=text,
        )

    @override
    def resizeEvent(self, w: int, h: int) -> None:
        """Override to stop resizing."""
        return
