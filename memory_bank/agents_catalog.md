# Agents Catalog

A reference for every Team647 agent policy in `src/arc647/agents/`. Each entry lists what
the agent does, how it behaves, and when to use it. Keep this file in sync when agents are
added, removed, or materially changed.

The agents run on the official **ARC-AGI-3-Agents** framework (vendored as a git submodule
under `external/ARC-AGI-3-Agents`). Each subclasses the framework's `Agent` base class and
is launched via `smoke_test.py`, which registers our agents into the framework's
`AVAILABLE_AGENTS` and hands off to its `main()`. Run (through the submodule's env, via
WSL):

```bash
uv run --project external/ARC-AGI-3-Agents python smoke_test.py --agent=actioneffectagent --game=ls20
uv run --project external/ARC-AGI-3-Agents python smoke_test.py --agent=randomagent --game=ls20
```

CLI names are the lowercased class names. Set `OPERATION_MODE=offline` for local play.

## Summary

| Agent | File | CLI (`--agent`) | One-line description | When to use | Learns? |
|---|---|---|---|---|---|
| `RandomAgent` | `random_agent.py` | `randomagent` | Uniform-random pick among valid actions | Score floor; harness sanity-check | No |
| `ActionEffectAgent` | `action_effect.py` | `actioneffectagent` | UCB bandit biased toward state-changing actions, with loop breaking | Default V1 exploration baseline | Yes (online) |

## Framework `Agent` interface (what our agents implement)

Defined in `external/ARC-AGI-3-Agents/agents/agent.py`. Subclasses must implement:

- `is_done(frames, latest_frame)` — typically `latest_frame.state is GameState.WIN`.
- `choose_action(frames, latest_frame)` — return a `GameAction` (use `set_data({"x","y"})`
  for the complex action `ACTION6`, and the `reasoning` attribute for replays).

`MAX_ACTIONS` (class attribute) caps the external-action budget. There is **no** `observe`
hook — adaptive agents learn at the top of `choose_action` by diffing `latest_frame`
against the grid seen when the previous action was chosen.

## `RandomAgent` — `random_agent.py`

- **Name / CLI:** `randomagent` (`--agent=randomagent`)
- **What it does:** Picks uniformly among the actions the environment reports as valid,
  sampling random `x`/`y` (0–63) for the complex action. No learning, no memory.
- **Behaviour:** Pure uniform random over valid actions every step.
- **When to use:**
  - As the **score floor** — the baseline every smarter policy must beat.
  - To sanity-check the harness (env stepping, resets, scorecards) without any agent
    logic in the way.
- **Limitations:** No world model, no goal awareness, no exploration bias. Will only
  ever complete a level by luck. (The framework also ships its own `Random` template;
  ours is kept distinct as `randomagent`.)

## `ActionEffectAgent` — `action_effect.py`

- **Name / CLI:** `actioneffectagent` (`--agent=actioneffectagent`) — the primary Team647
  agent and Version 1 of the research plan.
- **What it does:** Learns online *which actions change the world* and biases exploration
  toward state-changing actions while avoiding loops. numpy-only, fully offline,
  sandbox-safe.
- **Behaviour:**
  - **UCB bandit** over actions: scores each by `change_rate + progress_bonus *
    progress_rate + c * sqrt(ln N / n)`, so untried actions are tried first and
    reliably useful ones are exploited.
  - **Loop breaking:** tracks visited state hashes; the more often the exact state is
    revisited, the higher the probability of taking a random valid action to escape a
    cycle.
  - **`ACTION6` coordinate search:** prefer cells that changed the world before, then an
    untried cell, then the least-tried cell.
  - **Learning:** at the top of each `choose_action`, per-action and per-coordinate
    statistics are updated from whether the grid changed or a level was completed since the
    previous action; level completions are rewarded strongly. numpy-only, no extra deps.
- **Tunable params:** `ucb_c` (exploration weight), `novelty_weight` (loop-escape
  aggressiveness), `progress_bonus` (reward weight for level progress).
- **When to use:**
  - The current **default exploration baseline** — better than random on
    exploration-heavy games where state-changing actions are informative.
  - When establishing Version 1 baseline metrics to compare future agents against.
- **Limitations:** No world model (does not predict action outcomes), no goal inference,
  no multi-step planning/search. On games needing a specific long action sequence toward
  an unknown goal it performs no better than random. The planned upgrades — state-graph
  memory (V2), learned value model (V3), and search-based planning (V4) — are not yet
  built.

## Choosing an agent

- **Validating the harness / score floor:** `randomagent`.
- **Default exploration / V1 baseline:** `actioneffectagent`.
- **Solving non-trivial levels:** not yet available — requires the V2–V4 agents on the
  roadmap.
