import argparse
import sys

from arc_agi import Arcade, OperationMode
from arcengine import GameAction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a minimal local ARC-AGI-3 smoke test."
    )
    parser.add_argument(
        "--game",
        default="ls20",
        help="Game id to run locally.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=3,
        help="Number of ACTION1 steps to take.",
    )
    parser.add_argument(
        "--render-terminal",
        action="store_true",
        help="Render the game in the terminal for debugging.",
    )
    parser.add_argument(
        "--mode",
        choices=("offline", "online"),
        default="offline",
        help="Toolkit operation mode to use.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    render_mode = "terminal" if args.render_terminal else None
    operation_mode = (
        OperationMode.OFFLINE if args.mode == "offline" else OperationMode.ONLINE
    )

    arc = Arcade(operation_mode=operation_mode)
    env = arc.make(args.game, render_mode=render_mode)

    print(f"Running smoke test for game: {args.game}")
    print(f"Operation mode: {args.mode}")

    if env is None:
        print(
            "Unable to create the environment. In offline mode this usually means "
            "no local ARC game environments are currently available."
        )
        print(
            "Try again once local game sources are available, or use "
            "`--mode online` with a configured `ARC_API_KEY`."
        )
        sys.exit(1)

    print(f"Available actions: {env.action_space}")

    observation = None
    for step in range(args.steps):
        observation = env.step(GameAction.ACTION1)
        print(f"Step {step + 1}: {observation}")

    print("Scorecard:")
    print(arc.get_scorecard())


if __name__ == "__main__":
    main()
