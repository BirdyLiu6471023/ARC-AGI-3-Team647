"""Entry point: run Team647 agents on the official ARC-AGI-3-Agents framework.

This is the minimal local entry point for stepping a game. It does the plumbing
needed to run our agents (which live in ``src/arc647/agents`` and subclass the
framework's ``Agent``) under the framework's own ``main()`` / ``Swarm``:

1. Put the ARC-AGI-3-Agents submodule and our ``src`` on ``sys.path``.
2. Load the framework's ``.env.example`` (server defaults: three.arcprize.org)
   then our repo ``.env`` (ARC_API_KEY), without overriding already-set vars.
3. Register our agents into the framework's ``AVAILABLE_AGENTS`` dict.
4. Delegate to the framework's ``main()`` for arg parsing and the run loop.

Run it through the submodule's environment (which ships every framework
dependency) via WSL, e.g.::

    uv run --project external/ARC-AGI-3-Agents python smoke_test.py \
        --agent=actioneffect --game=ls20
    uv run --project external/ARC-AGI-3-Agents python smoke_test.py \
        --agent=randomagent --game=ls20

Agent names are the lowercased class names: ``actioneffect`` and ``randomagent``.
Set ``OPERATION_MODE=offline`` in the environment for local engine play.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
FRAMEWORK = ROOT / "external" / "ARC-AGI-3-Agents"

if not FRAMEWORK.exists():
    raise SystemExit(
        "ARC-AGI-3-Agents submodule missing. Run:\n"
        "  git submodule update --init --recursive"
    )

# 1. Make the framework package and our agents importable.
sys.path.insert(0, str(FRAMEWORK))
sys.path.insert(0, str(ROOT / "src"))

# 2. Load env: framework defaults first, then our key (no override of set vars).
from dotenv import load_dotenv  # noqa: E402

load_dotenv(dotenv_path=FRAMEWORK / ".env.example")
load_dotenv(dotenv_path=ROOT / ".env", override=True)


def main() -> None:
    # 3. Register our agents into the framework's registry.
    from agents import AVAILABLE_AGENTS  # noqa: E402  (heavy: pulls framework deps)

    from arc647.agents import register  # noqa: E402

    register(AVAILABLE_AGENTS)

    # 4. Hand off to the framework's CLI (arg parsing + swarm run loop).
    import main as framework_main  # noqa: E402  (external/.../main.py)

    framework_main.main()


if __name__ == "__main__":
    main()
