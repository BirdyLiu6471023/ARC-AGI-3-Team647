"""Self-contained Team647 agent for the Kaggle ARC-AGI-3 submission notebook.

This is our ``ActionEffectAgent`` (Version 1, StochasticGoose-style action-effect
exploration) flattened into a single file with its numpy frame helpers inlined,
so it has **no dependency on the local ``arc647`` package** — the Kaggle rerun
environment only has the ``arc-agi`` toolkit (installed offline from the provided
wheels) plus numpy. It subclasses the framework ``Agent`` and is registered as
``MyAgent`` (CLI: ``myagent``), matching the official sample-submission recipe.

The notebook writes this file to ``/kaggle/working/my_agent.py`` and copies it
into ``ARC-AGI-3-Agents/agents/templates/my_agent.py`` before running
``main.py --agent myagent``.
"""

from __future__ import annotations

import hashlib
import math
import time
from collections import defaultdict
from typing import Any, Optional, Sequence

import numpy as np
from arcengine import FrameData, GameAction, GameState

from agents.agent import Agent

_GRID = 64


# -- inlined frame helpers (from arc647.utils.frames) ----------------------

def _frames_to_array(frame: Sequence) -> np.ndarray:
    """Stack raw frame layers into a single ``(layers, H, W)`` int array."""
    if frame is None or len(frame) == 0:
        return np.empty((0, 0, 0), dtype=np.int16)
    layers = [np.asarray(layer, dtype=np.int16) for layer in frame]
    return np.stack(layers, axis=0)


def _state_hash(grid: np.ndarray) -> str:
    """Stable hash of a grid array for novelty / loop detection."""
    if grid.size == 0:
        return "empty"
    return hashlib.blake2b(grid.tobytes(), digest_size=16).hexdigest()


def _grid_changed(before: np.ndarray, after: np.ndarray) -> bool:
    """True if the observable grid changed between two steps."""
    if before.shape != after.shape:
        return True
    return not np.array_equal(before, after)


class MyAgent(Agent):
    """UCB exploration agent biased toward state-changing actions."""

    # No action cap: external actions are the scored quantity, but completion is
    # gated first, so we spend actions freely chasing wins and stop on a
    # wall-clock budget instead (mirrors StochasticGoose). Internal compute is
    # free under the scoring rules, so the only real limit is the 9h rerun cap.
    MAX_ACTIONS = float("inf")
    TIME_BUDGET_S = 8 * 3600 - 5 * 60  # ~7h55m, just under Kaggle's 9h rerun limit

    def __init__(
        self,
        *args: Any,
        ucb_c: float = 1.4,
        novelty_weight: float = 0.5,
        progress_bonus: float = 5.0,
        time_budget_s: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._start_time = time.time()
        self._time_budget_s = (
            self.TIME_BUDGET_S if time_budget_s is None else time_budget_s
        )
        self._rng = np.random.default_rng()
        self._ucb_c = ucb_c
        self._novelty_weight = novelty_weight
        self._progress_bonus = progress_bonus

        self._tries: dict[GameAction, int] = defaultdict(int)
        self._changes: dict[GameAction, int] = defaultdict(int)
        self._progress: dict[GameAction, int] = defaultdict(int)
        self._total_steps = 0

        self._visits: dict[str, int] = defaultdict(int)

        self._coord_tries = np.zeros((_GRID, _GRID), dtype=np.int32)
        self._coord_changes = np.zeros((_GRID, _GRID), dtype=np.int32)

        self._last_action: Optional[GameAction] = None
        self._last_coord: Optional[tuple[int, int]] = None
        self._last_grid: Optional[np.ndarray] = None
        self._last_levels = 0

    # -- Agent API ---------------------------------------------------------

    def _time_elapsed(self) -> bool:
        return (time.time() - self._start_time) >= self._time_budget_s

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN or self._time_elapsed()

    def choose_action(
        self, frames: list[FrameData], latest_frame: FrameData
    ) -> GameAction:
        grid = _frames_to_array(latest_frame.frame)
        self._learn(grid, latest_frame.levels_completed)

        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            return self._remember(GameAction.RESET, None, grid, latest_frame)

        self._visits[_state_hash(grid)] += 1
        actions = self._available(latest_frame)

        action = self._select(actions, grid)
        coord: Optional[tuple[int, int]] = None
        if action.is_complex():
            coord = self._pick_coord()
            action.set_data({"x": coord[0], "y": coord[1]})
            action.reasoning = {"agent": "action_effect", "x": coord[0], "y": coord[1]}
        else:
            action.reasoning = "action_effect: UCB exploration"

        return self._remember(action, coord, grid, latest_frame)

    # -- learning / selection ---------------------------------------------

    def _learn(self, grid: np.ndarray, levels: int) -> None:
        a = self._last_action
        if a is None or a is GameAction.RESET or self._last_grid is None:
            return

        self._total_steps += 1
        self._visits[_state_hash(grid)] += 1

        changed = _grid_changed(self._last_grid, grid)
        made_progress = levels > self._last_levels

        self._tries[a] += 1
        if changed:
            self._changes[a] += 1
        if made_progress:
            self._progress[a] += 1

        if a.is_complex() and self._last_coord is not None:
            x, y = self._last_coord
            self._coord_tries[y, x] += 1
            if changed or made_progress:
                self._coord_changes[y, x] += 1

    def _select(self, actions: list[GameAction], grid: np.ndarray) -> GameAction:
        revisits = self._visits.get(_state_hash(grid), 0)
        escape_prob = 1.0 - math.exp(-self._novelty_weight * max(0, revisits - 1))
        if revisits > 1 and self._rng.random() < escape_prob:
            return actions[int(self._rng.integers(len(actions)))]

        best_action = actions[0]
        best_score = -math.inf
        for action in actions:
            score = self._score(action)
            if score > best_score or (
                score == best_score and self._rng.random() < 0.5
            ):
                best_score = score
                best_action = action
        return best_action

    def _score(self, action: GameAction) -> float:
        n = self._tries[action]
        if n == 0:
            return math.inf
        change_rate = self._changes[action] / n
        progress_rate = self._progress[action] / n
        exploration = self._ucb_c * math.sqrt(math.log(self._total_steps + 1) / n)
        return change_rate + self._progress_bonus * progress_rate + exploration

    def _pick_coord(self) -> tuple[int, int]:
        if self._coord_changes.max() > 0:
            ys, xs = np.where(self._coord_changes == self._coord_changes.max())
            i = int(self._rng.integers(len(xs)))
            return int(xs[i]), int(ys[i])

        untried = np.argwhere(self._coord_tries == 0)
        if len(untried) > 0:
            y, x = untried[int(self._rng.integers(len(untried)))]
            return int(x), int(y)

        ys, xs = np.where(self._coord_tries == self._coord_tries.min())
        i = int(self._rng.integers(len(xs)))
        return int(xs[i]), int(ys[i])

    # -- helpers -----------------------------------------------------------

    def _available(self, latest_frame: FrameData) -> list[GameAction]:
        raw = latest_frame.available_actions or []
        actions: list[GameAction] = []
        for a in raw:
            action = a if isinstance(a, GameAction) else GameAction.from_id(a)
            if action is not GameAction.RESET:
                actions.append(action)
        if not actions:
            actions = [a for a in GameAction if a is not GameAction.RESET]
        return actions

    def _remember(
        self,
        action: GameAction,
        coord: Optional[tuple[int, int]],
        grid: np.ndarray,
        latest_frame: FrameData,
    ) -> GameAction:
        self._last_action = action
        self._last_coord = coord
        self._last_grid = grid
        self._last_levels = latest_frame.levels_completed
        return action
