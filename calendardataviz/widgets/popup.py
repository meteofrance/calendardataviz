from typing import Any, override

import TermTk as ttk


class PopupWindowWidget(ttk.TTkWindow):
    """Popup window, with a scroll area."""

    def __init__(
        self,
        text: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            text: Content of the popup's body.
            distance_to_screen_bottom: Used to compute the
                window's allowed height.
            args: Arguments passed to the ttk.TTkWindow parent class.
            kwargs: Arguments passed to the ttk.TTkWindow parent class.
        """

        self._text = text
        width: int = max(len(line) for line in text.split("\n")) + 3
        height: int = len(text.split("\n")) + 4
        if "title" in kwargs:
            width = max(width, len(kwargs["title"]) + 3)

        super().__init__(
            size=(width, height),
            flags=ttk.TTkK.WindowFlag.WindowCloseButtonHint,
            *args,
            **kwargs,
        )

        # Instantiate the scroll area
        scroll_area = ttk.TTkScrollArea(
            parent=self,
            visible=True,
            pos=(0, 0),
            size=(width + 1, height - 4),
            verticalScrollBarPolicy=ttk.TTkK.ScrollBarAlwaysOn,
        )
        ttk.TTkLabel(
            parent=scroll_area.viewport(),
            text=text,
        )

    @override
    def resizeEvent(self, w: int, h: int) -> None:
        """Override to stop resizing."""
        return
