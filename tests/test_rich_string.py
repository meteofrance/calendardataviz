from calendardataviz import RichString
import TermTk as ttk
import pytest


def test_RichString() -> None:
    rs = RichString(
        text="test",
        bg_color="#ff00ff",
        fg_color="#00ffff",
    )

    assert rs.colorAt(0) == (ttk.TTkColor.fg("#00ffff") + ttk.TTkColor.bg("#ff00ff"))
    assert str(rs) == "test"

    # test that giving a bad color value raises the right exception
    with pytest.raises(ValueError):
        RichString("", "", "")
    with pytest.raises(ValueError):
        RichString("", (400, 400, 400), (400, 400, 400))
    with pytest.raises(ValueError):
        RichString("", (-1, -1, -1), (-1, -1, -1))
    with pytest.raises(ValueError):
        RichString("", (-1.0, -1.0, -1.0), (-1.0, -1.0, -1.0))
    with pytest.raises(ValueError):
        RichString("", (2.0, 2.0, 2.0), (2.0, 2.0, 2.0))
