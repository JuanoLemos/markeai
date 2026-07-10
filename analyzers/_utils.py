"""
analyzers/_utils.py — Shared utilities for all analyzers.
B-23: extracted _silent_import() from adx_regime.py and ict_smc.py.
"""
import sys
import io


def silent_import():
    """Import a module while silencing its stdout/stderr (e.g. smartmoneyconcepts noise)."""
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = io.StringIO()
    try:
        from smartmoneyconcepts import smc
        return smc
    finally:
        sys.stdout, sys.stderr = old_out, old_err
