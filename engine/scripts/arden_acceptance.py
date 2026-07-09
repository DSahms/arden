"""CLI wrapper — see modules.arden_acceptance."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.arden_acceptance import run_acceptance  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(run_acceptance())
