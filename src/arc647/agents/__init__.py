"""Team647 agents for the ARC-AGI-3-Agents framework.

Each agent subclasses the framework's ``Agent`` base class. Because the framework
builds ``AVAILABLE_AGENTS`` from ``Agent.__subclasses__()`` *inside its own
package*, our external agents must be registered explicitly — call
:func:`register` after importing the framework's ``AVAILABLE_AGENTS``. The entry
point in ``smoke_test.py`` does this before running the swarm.
"""

from __future__ import annotations

from typing import Type

from agents.agent import Agent  # from the ARC-AGI-3-Agents submodule

from .action_effect import ActionEffectAgent
from .random_agent import RandomAgent

TEAM_AGENTS: list[Type[Agent]] = [ActionEffectAgent, RandomAgent]


def register(available: dict[str, Type[Agent]]) -> None:
    """Add Team647 agents to the framework's ``AVAILABLE_AGENTS`` dict.

    Keyed by lowercased class name, matching the framework's CLI convention
    (e.g. ``--agent=actioneffect`` / ``--agent=randomagent``).
    """
    for cls in TEAM_AGENTS:
        available[cls.__name__.lower()] = cls


__all__ = ["ActionEffectAgent", "RandomAgent", "TEAM_AGENTS", "register"]
