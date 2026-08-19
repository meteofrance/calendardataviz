from multiprocessing import Manager, Pool
from pathlib import Path

from calendardataviz.app import _instantiate_widgets  # type: ignore[reportPrivateUsage]

from tests import DummyInspector


def test_layout() -> None:
    with Manager() as manager, Pool(processes=1) as pool:
        root = _instantiate_widgets(
            manager=manager,
            pool=pool,
            inspector=DummyInspector(),
            years=[2026],
            target_nb_files=10,
            root_dir=Path("."),
        )

        assert root.getWidgetByName("root") is not None
        assert root.getWidgetByName("scroll_area") is not None
        assert root.getWidgetByName("color_bar") is not None
        assert root.getWidgetByName("calendar_2026") is not None
        assert root.getWidgetByName("file_count") is not None
        assert root.getWidgetByName("quit_button") is not None
