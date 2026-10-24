#!/usr/bin/python3
"""Exec the external native recorder without relaying engine protocol bytes."""
import os
from pathlib import Path
import sys

record = Path(os.environ['ROOK_RELEASE_NATIVE_DIR'])/(str(os.getpid())+'.json')
os.execv(sys.executable, [sys.executable, os.environ['ROOK_RELEASE_ACCOUNT'],
    '--engine', os.environ['ROOK_RELEASE_ENGINE'], '--record', str(record),
    '--known-single-process', *sys.argv[1:]])
