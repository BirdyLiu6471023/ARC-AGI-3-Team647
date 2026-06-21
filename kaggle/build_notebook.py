"""Build the Kaggle submission notebook for the Team647 action-effect agent.

Generates ``submission.ipynb`` by embedding ``my_agent.py`` into a notebook that
follows the official ARC-AGI-3 sample-submission recipe:

1. Install the ``arc-agi`` toolkit offline from the competition's bundled wheels.
2. Write our self-contained agent to ``/kaggle/working/my_agent.py``.
3. On competition rerun: copy the framework repo, drop in our agent, replace
   ``agents/__init__.py`` with a minimal one (avoids langgraph/smolagents deps),
   point ``.env`` at the local ``gateway:8001`` game server, and run
   ``main.py --agent myagent`` (which auto-produces the submission file).
4. On commit (non-rerun): write a dummy ``submission.parquet`` so Submit activates.

Run:  python kaggle/build_notebook.py   ->   writes kaggle/submission.ipynb
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent
AGENT_SRC = (HERE / "my_agent.py").read_text(encoding="utf-8")

INSTALL = r'''# Install the arc-agi toolkit offline from the competition's bundled wheels.
# The wheels are only mounted during the official scoring rerun, so at commit /
# interactive time they may be absent -- that's expected and not an error.
import glob
import subprocess
import sys

_paths = sorted(glob.glob('/kaggle/input/**/arc_agi_3_wheels', recursive=True))
if _paths:
    subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--no-index',
         '--find-links', _paths[0], 'arc-agi', 'python-dotenv'],
        check=True,
    )
    print(f'Installed arc-agi from {_paths[0]}')
else:
    print('arc_agi_3_wheels not mounted yet (expected at commit; available on rerun)')'''

WRITE_AGENT = "%%writefile /kaggle/working/my_agent.py\n" + AGENT_SRC

RERUN = r'''import os

if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
    # Wait for the local game gateway to be ready
    !curl --fail --retry 999 --retry-all-errors --retry-delay 5 \
          --retry-max-time 600 http://gateway:8001/api/games

    # Copy framework repo to a writable location
    !cp -r /kaggle/input/competitions/arc-prize-2026-arc-agi-3/ARC-AGI-3-Agents \
           /kaggle/working/ARC-AGI-3-Agents

    # Copy our agent into the framework's templates
    !cp /kaggle/working/my_agent.py \
        /kaggle/working/ARC-AGI-3-Agents/agents/templates/my_agent.py

    # Minimal __init__.py: import only what we need (avoids langgraph/smolagents deps)
    with open('/kaggle/working/ARC-AGI-3-Agents/agents/__init__.py', 'w') as f:
        f.write("""from typing import Type, cast
from dotenv import load_dotenv
from .agent import Agent, Playback
from .swarm import Swarm
from .templates.random_agent import Random
from .templates.my_agent import MyAgent

load_dotenv()

AVAILABLE_AGENTS: dict[str, Type[Agent]] = {
    "random": Random,
    "myagent": MyAgent,
}
""")

    # Point the framework at the local gateway (loaded with override=True by main.py)
    with open('/kaggle/working/ARC-AGI-3-Agents/.env', 'w') as f:
        f.write("""SCHEME=http
HOST=gateway
PORT=8001
ARC_API_KEY=test-key-123
ARC_BASE_URL=http://gateway:8001/
OPERATION_MODE=online
ENVIRONMENTS_DIR=
RECORDINGS_DIR=/kaggle/working/server_recording
""")

    # Run our agent across all games (swarm); submission file is auto-produced
    !cd /kaggle/working/ARC-AGI-3-Agents && \
        MPLBACKEND=agg \
        python main.py --agent myagent'''

DUMMY = r'''# Non-rerun (commit) mode: produce a placeholder submission so Submit activates
import os
import pandas as pd

if not os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
    submission = pd.DataFrame(
        data=[['1_0', '1', True, 1]],
        columns=['row_id', 'game_id', 'end_of_game', 'score'])
    submission.to_parquet('/kaggle/working/submission.parquet', index=False)'''


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"trusted": True},
        "outputs": [],
        "source": source,
    }


notebook = {
    "cells": [code_cell(INSTALL), code_cell(WRITE_AGENT), code_cell(RERUN), code_cell(DUMMY)],
    "metadata": {
        "kaggle": {
            "accelerator": "none",
            "dataSources": [
                {
                    "sourceType": "competition",
                    "sourceId": 133468,
                    "databundleVersionId": 16244308,
                    "isSourceIdPinned": False,
                }
            ],
            "isGpuEnabled": False,
            "isInternetEnabled": False,
            "language": "python",
            "sourceType": "notebook",
        },
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.12.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}

out = HERE / "submission.ipynb"
out.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
print(f"Wrote {out} ({out.stat().st_size} bytes, {len(notebook['cells'])} cells)")
