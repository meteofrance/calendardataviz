from pathlib import Path

from calendardataviz.colors import JET
from demos.color_bars import RainbowInspector
from tests.fixtures.frame_testing import run_and_check_frames


def test_rainbow(tmp_path: Path) -> None:
    run_and_check_frames(
        tmp_path=tmp_path,
        expected_frame_dir=Path(__file__).parent / "expected_frames" / "demo_rainbow",
        inspectors=RainbowInspector("Testing", JET),
        years=[2024, 2025],
        frames_limit=2,
        terminal_size=(88, 50),
    )

