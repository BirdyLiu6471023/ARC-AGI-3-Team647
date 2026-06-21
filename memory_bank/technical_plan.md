# Technical Plan

## Problem-Solving Objective
The technical goal is to build an ARC-AGI-3 agent that performs well on unseen interactive environments under the benchmark's scoring model. Success is driven by two linked outcomes, in priority order: first, completing as many levels as possible, because the maximum score of an environment is only unlocked by completing every level (including the final one) and later levels are weighted more heavily; second, doing so with strong action efficiency, because each completed level is scored on `(human_baseline_actions / agent_actions)` squared. The agent must therefore reach deep into environments while remaining sample-efficient at rule discovery and economical when executing a confirmed strategy.

## Scoring Model (design constraints)
- **Action**: a discrete interaction that changes environment state. Internal reasoning, retries, and tool calls are free and uncounted. This is the central lever: trade unlimited internal compute for fewer external actions.
- **Per-level score**: `(human_baseline_actions / agent_actions) ** 2`, capped slightly above parity (~1.15x). The human baseline is the upper-median first-time human by fewest actions, so the target is to match a competent first-time player, not to play optimally.
- **Per-game score**: weighted average of completed-level scores, weighted by the 1-indexed level number; reaching 100% requires finishing the final level.
- **Overall score**: average of per-game scores across the evaluation set.

## Environment Interface (what the agent operates on)
- **Observation**: a 64x64 grid where each cell is one of 16 colors, delivered as one or more stacked frame layers per turn.
- **Actions**: `ACTION1-4` (directional), `ACTION5` (context interaction), `ACTION6` (complex action with X/Y in 0-63), `ACTION7` (undo), and `RESET`. The valid action set is reported in each frame's metadata; the active targets of `ACTION6` are not given and must be discovered. In a terminal state only `RESET` is valid.
- **State**: `NOT_PLAYED`, `NOT_FINISHED`, `WIN`, `GAME_OVER`, plus `levels_completed` and `win_levels` counters.
- **Execution**: local engine play is markedly faster than the online API and needs no network, so it is the default for development and any learning. Evaluation is expected to run offline/self-contained.

## Core Methodology
1. Build a reliable environment harness that can step any ARC-AGI-3 game and expose observations, valid actions, and progress cleanly.
2. Instrument every run so each action can be analyzed against eventual completion and efficiency.
3. Separate the solving loop into observation, exploration, hypothesis/world-modeling, execution, and post-action update.
4. Compare multiple agent architectures on the same game sets rather than iterating blindly on a single model or prompt.
5. Prefer methods that generalize across unseen games over game-specific hand-tuning, and prefer offline-runnable components over network-dependent ones.

## Candidate Solution Approaches
The approaches below stay valid; empirically, informed search with lightweight learned models beats pure language reasoning on this benchmark, so the project's center of gravity is B/C/D rather than E.

- **A. Reactive baseline** — map recent frames directly to an action via heuristics or a constrained random policy. Fast to build, validates the loop, sets a score floor. Weak efficiency and generalization. Necessary baseline only.
- **B. Memory-augmented agent** — track frames, actions, outcomes, and inferred mechanics so the agent can tell "what has been tried" from "what changed". Strong for exploration-heavy games; the first serious general-purpose architecture.
- **C. Hypothesis-driven planner** — treat each game as an unknown system, infer candidate mechanics/goals from transitions, and choose actions that test or exploit them. Directly targets action efficiency; one of the most promising directions.
- **D. Search-based action planner** — rollout/beam/MCTS-style search over candidate futures ranked by information gain or expected progress. Best as a component inside a hybrid, used on high-uncertainty or high-value decisions.
- **E. Local reasoning model** — a small, locally shipped model (not a network API) that interprets frames and proposes hypotheses. Useful as a secondary reasoning layer, never as the backbone, and only if it runs offline.
- **F. Hybrid reasoning + memory + search** — combine a controller, structured memory, learned models, and selective search. Best alignment with the benchmark and the recommended long-term target; highest complexity, so it is approached incrementally.

## Reference Approaches (prior art to build on)
- **Action-effect / change-prediction policy** — a small CNN with light reinforcement that predicts which actions change the frame and biases exploration toward state-changing actions. This is the proven, sandbox-safe core and the basis of Version 1.
- **State-graph + learned value model** — build a directed graph of observed states, prune actions that loop or do nothing, and when score improves, back-label states with distance-to-goal and retrain a small value model (e.g. a compact ResNet) to rank (state, action) pairs toward the next milestone. Strong basis for Versions 2-3.

## Agent Architecture To Build
- **Observation encoder** — convert stacked frame grids into a compact internal representation and a stable state hash for novelty/loop detection.
- **Memory store** — record frames, chosen actions, observed transitions, failures, and partial discoveries.
- **Exploration policy** — choose information-gathering actions when uncertainty is high, biased toward actions/coordinates predicted to change state.
- **Execution policy** — choose efficient task-completing actions once a useful strategy is found, prioritizing progress into higher-weighted levels.
- **Action validator** — read the per-frame available-action set, build valid `ACTION6` coordinates, handle terminal-state resets, and guarantee every emitted action is valid with a safe fallback.
- **Evaluation logger** — record reasoning, actions, outcomes, and replay metadata for later analysis.

## Repository Structure
The project builds on the **official ARC-AGI-3-Agents framework** (vendored as a git
submodule) rather than a hand-rolled environment: the framework owns environment
interaction, the run loop (`Swarm`/`main`), scorecards, and recordings, while we contribute
agent policies that subclass its `Agent` base class. This mirrors how the leading preview
solutions (e.g. StochasticGoose) are built and keeps us aligned with the competition harness.

```
external/ARC-AGI-3-Agents/   # git submodule: official framework (Agent, Swarm, main.py,
                             #   structs, scorecards, recordings) + its own uv environment
src/arc647/
  agents/         # Team647 agents subclassing the framework Agent:
                  #   action_effect.py (ActionEffectAgent), random_agent.py (RandomAgent),
                  #   __init__.py exposes register() to add them to AVAILABLE_AGENTS
  utils/          # frame stacking, hashing, delta detection (numpy helpers)
smoke_test.py     # entry point: bootstraps sys.path + env, registers our agents,
                  #   delegates to the framework's main()
```

Run through the submodule's environment (which ships every framework dependency):

```bash
uv run --project external/ARC-AGI-3-Agents python smoke_test.py --agent=actioneffectagent --game=ls20
```

CLI agent names are the lowercased class names (`actioneffectagent`, `randomagent`). The
framework's `Agent` interface is `is_done(frames, latest_frame)` and
`choose_action(frames, latest_frame) -> GameAction`; there is no `observe` hook, so adaptive
agents learn at the top of `choose_action` by diffing against the previous frame.

## Key Features To Build
- Frame and state-delta tracking across time, with stable state hashing.
- Structured memory of attempted actions, coordinates, and results.
- Detection of repeated ineffective actions and loops.
- Exploration-versus-exploitation switching driven by uncertainty and progress.
- Frame-driven valid-action parsing, `ACTION6` coordinate search, and terminal resets.
- Support for multi-game experiments and version-to-version comparisons.
- Replay and scorecard analysis for failure review.
- Offline high-speed development with optional online runs for official validation.

## Frameworks And Libraries
- Python as the implementation language; `uv` for environment and dependency management; `pyproject.toml` for configuration.
- The **ARC-AGI-3-Agents** framework (git submodule at `external/ARC-AGI-3-Agents`) provides the `Agent` base class, `Swarm`/`main` run loop, environment wiring, scorecards, and recordings. Agents are run through the submodule's own uv environment, which ships every framework dependency.
- `arc-agi` (`Arcade`, `EnvironmentWrapper`, scorecards) and `arcengine` (`GameAction`, `FrameData`, `GameState`) for environment interaction, used via the framework.
- `numpy` for frame arrays, hashing, and the online statistics used by the exploration policy.
- A local deep-learning runtime (e.g. PyTorch) is an optional later addition for the CNN action-effect and value models; it is not required for Version 1 and must run offline if adopted.

## Evaluation Strategy
- Measure both completion depth (levels reached, with the final-level requirement in mind) and action efficiency relative to the human baseline.
- Start with a small stable subset of games for rapid iteration; use offline runs for speed and online runs only for official scorecards and replays.
- Compare agent versions on identical game subsets; analyze failed trajectories to attribute failure to observation, memory, hypotheses, or action selection.
- Treat scorecards, recordings, and benchmarking as first-class parts of the workflow.

## Solution Versions
### Version 0 — Documentation and benchmark understanding
Read the quickstart, toolkit, scoring, agent, and benchmarking docs; define the objective around completion-first, action-efficient performance. Status: completed.

### Version 1 — Instrumented baseline with action-effect exploration
Adopt the official ARC-AGI-3-Agents framework (git submodule) for environment interaction, run loop, and scorecards; contribute a random baseline and an action-effect exploration agent (UCB over actions biased toward state-changing moves and untried `ACTION6` coordinates) as framework `Agent` subclasses. Status: in progress. (Earlier iteration built an in-house `ArcEnv`/runner; this was replaced by the official framework to stay aligned with the competition harness.)

### Version 2 — Memory-augmented general agent
Add a state graph and structured transition memory; reduce repeated mistakes and improve exploration quality; compare against Version 1 on a shared subset. Status: planned.

### Version 3 — Hypothesis-driven solver with learned value model
Add explicit rule/goal inference and a learned value model that ranks (state, action) pairs toward the next milestone; distinguish exploratory from exploitative actions. Status: planned.

### Version 4 — Hybrid planner
Integrate selective search/rollout with memory and the value model on high-uncertainty or high-value decisions; evaluate the compute-versus-actions trade-off. Status: planned.

### Version 5 — Benchmark-ready research system
Scale to larger game subsets, add repeatable benchmarking and regression checks, and use online scorecards and replays for external validation. Status: planned.
