"""Compatibility launcher for the first persistence experiment."""

from __future__ import annotations

from pathlib import Path
import runpy


EXPERIMENT = Path(__file__).parent / "experiments" / "01_signal_persistence.py"


if __name__ == "__main__":
    runpy.run_path(str(EXPERIMENT), run_name="__main__")
