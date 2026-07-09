"""Test configuration for local imports.

Ensures the repository root is on sys.path when pytest is run directly.
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))