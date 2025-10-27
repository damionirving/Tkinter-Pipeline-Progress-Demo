# pipeline.py
# Worker script that reports progress via a callback.
# It is importable and can also be run directly for CLI testing.

import time
from typing import Callable, Optional
import random

def main(on_progress: Optional[Callable[[int], None]] = None):
    """Run the pipeline and report progress 0..100 via on_progress.

    Args:
        on_progress: a callable taking an int percentage (0..100). If None, no progress is reported.
    Returns:
        str: final result string.
    """
    steps = 101  # simulate 0..100 inclusive
    for i in range(steps):
        # Simulate work
        time.sleep(random.randint(1, 1000)/1000)  # sleep 10-50 ms
        if on_progress is not None:
            try:
                on_progress(i)
            except Exception:
                # Never let UI exceptions kill the worker
                pass
    # final status update to ensure 100%
    if on_progress is not None:
        try:
            on_progress(100)
        except Exception:
            pass
    return "pipeline complete"

if __name__ == "__main__":
    # Simple CLI runner that prints progress to stdout for debugging.
    def printer(pct: int):
        print(f"PROGRESS {pct}", flush=True)
    result = main(printer)
    print(f"RESULT {result}")
