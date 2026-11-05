#!/usr/bin/env python3
"""SchemeSathi launcher — run from the slay-hacks folder.

    python3 run.py

Serves the app at http://127.0.0.1:8765 (override with SCHEMESATHI_PORT).
Stdlib only — no install step, no accounts, no network calls.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from server import main  # noqa: E402

if __name__ == "__main__":
    main()
