"""Random baseline agent, ported to the official ARC-AGI-3-Agents framework.

Picks uniformly among the actions the environment reports as valid (sampling
coordinates for the complex action). It establishes the score floor that every
smarter policy must beat. Named ``RandomAgent`` (CLI ``randomagent``) to sit
alongside the framework's own ``Random`` template without clashing.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from arcengine import FrameData, GameAction, GameState

from agents.agent import Agent  # from the ARC-AGI-3-Agents submodule


class RandomAgent(Agent):
    """Uniform-random valid action; the baseline score floor."""

    MAX_ACTIONS = 200

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._rng = np.random.default_rng()

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN

    def choose_action(
        self, frames: list[FrameData], latest_frame: FrameData
    ) -> GameAction:
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            return GameAction.RESET

        raw = latest_frame.available_actions or []
        actions = [
            a if isinstance(a, GameAction) else GameAction.from_id(a) for a in raw
        ]
        actions = [a for a in actions if a is not GameAction.RESET]
        if not actions:
            actions = [a for a in GameAction if a is not GameAction.RESET]

        action = actions[int(self._rng.integers(len(actions)))]
        if action.is_complex():
            action.set_data(
                {"x": int(self._rng.integers(64)), "y": int(self._rng.integers(64))}
            )
            action.reasoning = {"agent": "random"}
        else:
            action.reasoning = "random baseline"
        return action
