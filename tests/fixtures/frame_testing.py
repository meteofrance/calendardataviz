"""Helpers to snapshot and compare the full renders of a headless TTk app.

These helpers run a `tests.fixtures.TestableTTk` scene against
a set of expected frame snapshots stored under `tests/data/<test_name>/` in
the repository. On the first run, when the expected directory does not exist,
the freshly recorded frames are copied there to serve as a baseline reference.
On later runs the recorded frames are compared byte-for-byte against those
baselines, so any change in rendering is detected.
"""

from multiprocessing import Manager, Pool
from multiprocessing.managers import SyncManager
from multiprocessing.pool import Pool as PoolType
import shutil
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any
from calendardataviz.app import _instantiate_widgets
from calendardataviz.inspector_abc import InspectorABC
from tests.fixtures.testable import TestableTTk

FrameAction = Callable[[], None]


def run_and_check_frames(
    *,
    tmp_path: Path,
    expected_frame_dir: Path,
    inspectors: InspectorABC | Sequence[InspectorABC],
    years: Sequence[int],
    frames_limit: int,
    terminal_size: tuple[int, int],
    scheduled_actions: Mapping[int, FrameAction] | None = None,
    timeout_seconds: float = 10.0,
) -> TestableTTk:
    """Run a scene and compare its recorded frames to the stored baseline.

    Args:
        tmp_path: Pytest-provided temporary directory for this test's frames.
        expected_frame_dir: Path to the expected frames directory.
        inspectors: One or more inspector classes to instantiate a calendar app.
        frames_limit: Maximum number of distinct frames to record.
        terminal_size: Fixed `(width, height)` to render at.
        scheduled_actions: Interactions to run between recorded frames.
        timeout_seconds: Safety limit in case frames plateau before the cap.

    Returns:
        TestableTTk: The run root widget, whose `snapshots` hold the frames.

    Raises:
        AssertionError: If the recorded frames differ from the baseline.
    """
    output_dir = tmp_path / expected_frame_dir.name

    # Temporary to inverse once multiple inspectors are supported in one calendar app.
    inspectors = inspectors[0] if isinstance(inspectors, Sequence) else inspectors
    
    root = TestableTTk(
        output_dir=output_dir,
        frames_limit=frames_limit,
        terminal_size=terminal_size,
        timeout_seconds=timeout_seconds,
        scheduled_actions=scheduled_actions,
    )
    with Manager() as manager, Pool(processes=1) as pool:
        _instantiate_widgets(
            root=root,
            manager=manager,
            pool=pool,
            inspectors=inspectors,
            years=years,
        )
        # mainloop() must run while the Manager and Pool are still alive: the
        # widgets' paintEvent reads results from a shared queue served by the
        # Manager process and fed by the pool workers.
        root.mainloop()

    if not expected_frame_dir.exists():
        shutil.copytree(output_dir, expected_frame_dir)
        return root

    actual_files = sorted(output_dir.glob("frame_*.txt"))
    expected_files = sorted(expected_frame_dir.glob("frame_*.txt"))

    actual_names = [path.name for path in actual_files]
    expected_names = [path.name for path in expected_files]

    assert actual_names == expected_names, (
        f"{expected_frame_dir.name}: frame set differs "
        f"(actual {actual_names}, expected {expected_names}). "
        f"Delete {expected_frame_dir} to regenerate the baseline."
    )

    for actual_path, expected_path in zip(actual_files, expected_files):
        assert actual_path.read_text(encoding="utf-8") == expected_path.read_text(
            encoding="utf-8"
        ), f"{expected_frame_dir.name}: {actual_path.name} differs from baseline"

    return root
