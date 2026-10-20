"""Testable TermTk root widget that records rendered frames to disk.

This module allows to test the global behavior of a TermTk application:
run a real :py:class:`~TermTk.TTkCore.ttk.TTk` main loop for a bounded
number of frames and dump each distinct composed frame to a human-readable
file.

The rendering seam used here is the ``paintExecuted`` signal of the root
widget. It is emitted on the draw thread right after
:py:func:`TTkHelper.paintAll` has composed every widget into the root canvas,
so :py:attr:`TTkHelper._rootCanvas` holds the full screen for that frame.

To run headless (e.g. under pytest, where there is no real terminal) the class
monkeypatches a small set of TermTk terminal entry points before entering the
main loop: the terminal size is fixed, terminal writes are silenced, and the
input thread is replaced by a blocking wait that releases on quit.
"""

import threading
import warnings
from collections.abc import Callable, Mapping
from pathlib import Path
from time import monotonic
import re
import TermTk as ttk
from TermTk.TTkCore.TTkTerm.term_base import TTkTermBase


_ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from a rendered string.

    Args:
        text: A string that may contain ANSI escape sequences.

    Returns:
        str: The input with every escape sequence removed.
    """
    return _ANSI_ESCAPE_PATTERN.sub("", text)


class TestableTTk(ttk.TTk):
    """A root widget that snapshots each distinct rendered frame to a file.

    Args:
        output_dir: Directory where the distinct frames are written as
            numbered ANSI text files ``frame_000.txt``, ``frame_001.txt``...,
            each prefixed with a header describing the source.
        frames_limit: Maximum number of distinct frames to record.
        terminal_size: Fixed ``(width, height)`` used in place of the real
            terminal size, for deterministic rendering.
        timeout_seconds: Hard wall-clock limit after which the loop quits even
            if the frame cap was not reached. Guards against scenes whose
            animated frames plateau before ``frames_limit`` is met.
        scheduled_actions: Mapping from a 1-based distinct-frame index to a
            callable. The callable is invoked right after that frame is
            recorded, on the draw thread, letting a test drive interactions
            (e.g. clicking a button) between recorded snapshots.
        **kwargs: Keyword arguments forwarded to the base ``TTk`` widget.

    Attributes:
        snapshots: The distinct full-frame ANSI strings recorded, in order.
    """

    __test__ = False

    _POLL_INTERVAL = 0.1

    def __init__(
        self,
        *,
        output_dir: Path,
        frames_limit: int,
        terminal_size: tuple[int, int],
        timeout_seconds: float = 10.0,
        scheduled_actions: Mapping[int, Callable[[], None]] | None = None,
        **kwargs,
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        self._patch_terminal(terminal_size)

        super().__init__(**kwargs)

        self._output_dir = output_dir
        self._frames_limit = frames_limit
        self._deadline = monotonic() + timeout_seconds
        self._scheduled_actions: Mapping[int, Callable[[], None]] = (
            scheduled_actions or {}
        )
        self.snapshots: list[str] = []
        self._seen_frames: set[str] = set()
        self._quitting = False

        # Distinct frames are deduplicated by their serialized content so that
        # the number of recorded snapshots does not depend on draw timing.
        self._quit_event = threading.Event()

        self._setup_loop()

    def _setup_loop(self) -> None:
        """Wire the paint signal and quit timer that drive the frame loop."""
        # Emitted on the draw thread right after paintAll() composed the root
        # canvas, so it is the natural place to grab a full-frame snapshot.
        self.paintExecuted.connect(self._on_frame_painted)

        # A plain timer drives the loop bookkeeping: once we have seen enough
        # distinct frames we quit. The draw loop runs on its own thread while
        # mainloop() blocks, so this bookkeeping must happen on a
        # timer/deviation, not inline code in mainloop().
        self._loop_timer = ttk.TTkTimer(name="TestableTTk (quit)")
        self._loop_timer.timeout.connect(self._on_loop_tick)
        self._loop_timer.start(self._POLL_INTERVAL)

    @staticmethod
    def _patch_terminal(terminal_size: tuple[int, int]) -> None:
        """Route TermTk terminal I/O into a fixed, silent headless setup.

        The patched callables are stored on the class so a later
        :meth:`_restore_terminal` can put them back, keeping the global
        TermTk state free of leftovers between tests.

        Args:
            terminal_size: The fixed ``(width, height)`` to report.
        """
        width, height = terminal_size

        TestableTTk._saved_terminal = {
            "getTerminalSize": ttk.TTkTerm.getTerminalSize,
            "width": ttk.TTkTerm.width,
            "height": ttk.TTkTerm.height,
            "push": TTkTermBase.push,
            "flush": TTkTermBase.flush,
            "init": ttk.TTkInput.init,
            "close": ttk.TTkInput.close,
            "start": ttk.TTkInput.start,
        }

        ttk.TTkTerm.getTerminalSize = lambda: (width, height)
        ttk.TTkTerm.width = width
        ttk.TTkTerm.height = height

        # TermTk writes to the terminal through TTkTermBase.push, so silence
        # that, not the TTkTerm subclass alias.
        TTkTermBase.push = lambda *args: None
        TTkTermBase.flush = lambda: None

        # Do not touch the real console: input is handled by our own blocking
        # loop in mainloop().
        ttk.TTkInput.init = lambda *a, **k: None
        ttk.TTkInput.close = lambda: None

    @staticmethod
    def _restore_terminal() -> None:
        """Restore the TermTk terminal entry points that were patched."""
        saved = getattr(TestableTTk, "_saved_terminal", None)
        if saved is None:
            return

        ttk.TTkTerm.getTerminalSize = saved["getTerminalSize"]
        ttk.TTkTerm.width = saved["width"]
        ttk.TTkTerm.height = saved["height"]
        TTkTermBase.push = saved["push"]
        TTkTermBase.flush = saved["flush"]
        ttk.TTkInput.init = saved["init"]
        ttk.TTkInput.close = saved["close"]
        ttk.TTkInput.start = saved["start"]

        try:
            del TestableTTk._saved_terminal
        except AttributeError:
            pass

    def _run_headless_input_(self) -> None:
        """Block in place of the real input loop until a quit is requested.

        The real TTkInput.start() reads from the terminal until the app quits.
        Here we wait on an event that is set whenever TTkHelper.quit() is
        emitted, keeping mainloop() alive exactly like a real input loop.
        """
        ttk.TTkHelper.quitEvent.connect(self._quit_event.set)
        self._quit_event.wait()
        ttk.TTkHelper.quitEvent.disconnect(self._quit_event.set)

    def mainloop(self) -> None:
        """Enter the main loop with a headless input loop.

        The draw thread and frame snapshot logic are identical to a real
        run; only the terminal input backend is replaced.
        """
        ttk.TTkInput.start = self._run_headless_input_
        try:
            super().mainloop()
        finally:
            # Undo the mainloop() input override and the constructor patching
            # so the global TermTk state is clean for later tests.
            self._restore_terminal()

    def _maybe_quit(self) -> None:
        """Quit the loop once the frame cap or the timeout is reached."""
        if self._quitting:
            return
        if len(self.snapshots) >= self._frames_limit or monotonic() >= self._deadline:
            self._quitting = True
            pending = [
                index
                for index in self._scheduled_actions
                if index > len(self.snapshots)
            ]
            if pending:
                warnings.warn(
                    f"TestableTTk quit with {len(pending)} pending scheduled "
                    f"action(s) at frame indices {sorted(pending)}",
                    stacklevel=2,
                )
            ttk.TTkHelper.quit()

    def _on_loop_tick(self) -> None:
        """Force full repaints and exit once the cap or timeout is reached.

        TermTk does not repaint a freshly built headless scene on its own, so
        the first painted frames can stay blank until a widget is marked for
        update. Re-requesting a full repaint on every tick makes sure content
        is eventually composed even if an individual update is lost to a race
        with the draw thread. Once the cap or timeout is reached, quit.
        """
        if self._quitting:
            return
        ttk.TTkHelper.updateAll()
        if len(self.snapshots) < self._frames_limit and monotonic() < self._deadline:
            self._loop_timer.start(self._POLL_INTERVAL)
        else:
            self._maybe_quit()

    def _on_frame_painted(self) -> None:
        """Snapshot the current composed frame if it is new."""
        canvas = ttk.TTkHelper._rootCanvas
        if canvas is None:
            return

        frame_text = strip_ansi(canvas.toAnsi())
        if not frame_text.strip():
            # Drop the blank canvas emitted before the first real repaint;
            # it carries no scene content and is an artifact of headless boot.
            return
        if frame_text in self._seen_frames:
            return
        self._seen_frames.add(frame_text)
        self.snapshots.append(frame_text)

        self._write_frame(frame_text, len(self.snapshots) - 1)

        # Drive a scheduled interaction right after this frame was recorded, so
        # the next distinct snapshot reflects the resulting state change.
        action = self._scheduled_actions.get(len(self.snapshots))
        if action is not None:
            action()

        self._maybe_quit()

    def _write_frame(self, frame_text: str, index: int) -> None:
        """Write one recorded frame to disk with a human-readable header.

        Args:
            frame_text: The plain-text (ANSI-stripped) full screen for the
                frame.
            index: Zero-based sequence number of this distinct snapshot.
        """
        header = (
            f"# TestableTTk snapshot {index + 1:03d}\n"
            f"# size: {self.width()}x{self.height()}\n"
            f"# {'-' * 60}\n"
        )
        path = self._output_dir / f"frame_{index + 1:03d}.txt"
        path.write_text(header + frame_text, encoding="utf-8")
