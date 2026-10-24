#!/usr/bin/python3
"""Exec-only exact-image binding for the unchanged single-path wire checker."""
import os
from pathlib import Path

here = Path(__file__).resolve().parent
os.execv('/usr/bin/python3', ['/usr/bin/python3', str(here/'native_launch.py'),
    os.environ['ROOK2_FOCUSED_IMAGE'], '--threads='+os.environ['ROOK2_QUALIFICATION_THREADS'], '--'])
