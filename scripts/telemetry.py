#!/usr/bin/env python3
"""
Minimal opt-in crash telemetry: logs uncaught exceptions to a local file.
Enable with environment variable ROGUE_CITY_TELEMETRY=1
"""
import os
import sys
import traceback
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'telemetry.log')


def install():
    if os.getenv('ROGUE_CITY_TELEMETRY') != '1':
        return

    def excepthook(exc_type, exc, tb):
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(f"\n[{datetime.utcnow().isoformat()}] Uncaught exception:\n")
                traceback.print_exception(exc_type, exc, tb, file=f)
        except Exception:
            pass
        # Chain to default hook
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = excepthook


if __name__ == '__main__':
    install()
    raise RuntimeError('Telemetry test exception')
