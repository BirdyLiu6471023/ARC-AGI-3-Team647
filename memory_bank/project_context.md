# Project Context

## Project Goal
This repository supports the development of an agent for **ARC-AGI-3**, the first interactive reasoning benchmark in the ARC-AGI family. Unlike static benchmarks, an ARC-AGI-3 agent is placed into a novel, turn-based grid environment with **no instructions** and must, entirely on its own, explore the environment, infer the goal, model the underlying mechanics, and execute an efficient solution. The objective of this project is to build a system that generalizes to unseen environments rather than one that is hand-tuned to any specific game.

The project optimizes for the benchmark's true success criteria, which combine two factors in a specific order. First, **level completion gates the achievable score**: the maximum score for an environment is only unlocked by completing every level, including the final one, and later levels are weighted more heavily than earlier ones, so reaching deep into an environment is the primary objective. Second, **action efficiency multiplies that score**: each completed level is scored on the ratio of a human baseline action count to the agent's action count, squared, so inefficiency is penalized sharply. The human baseline is the upper-median first-time human by fewest actions, and the per-level score is capped slightly above parity, so the target is to match a competent first-time player rather than to play optimally. The system must consequently prioritize reaching later levels while remaining sample-efficient at discovering rules and economical when executing a confirmed strategy.

## Problem Framing
ARC-AGI-3 is an agent-development problem rather than a classification problem. The agent interacts with each environment through a constrained interface and is judged on how effectively it turns observation into purposeful action.

- **Observations** are 64×64 grids where each cell takes one of 16 colors. The agent receives a frame (or short sequence of frames) on each turn.
- **Actions** consist of five simple actions (four directional, one context-dependent interaction), an Undo action, and a single complex action that targets a specific cell by its X/Y coordinate on the grid, plus a reset. The set of valid actions is reported in each returned frame's metadata, and the active targets of the coordinate action are not given in advance; both must be inferred from interaction. Once an environment reaches a terminal state, only a reset is valid.
- **Internal computation that does not change the environment is not counted as an action.** This is the defining design principle of the project: the agent may spend substantial internal compute if doing so reduces the number of external actions taken.
- **Environments are level-based**, with several levels of increasing complexity and layered mechanics. The first level is an easy tutorial; later levels carry more weight in scoring and demand deeper understanding.
- **Capabilities under test** are exploration, world-modeling, goal-setting, and planning/execution, all grounded in core-knowledge priors (objectness, geometry, basic physics, agentness) without requiring language or domain knowledge.

The core challenge is to translate raw frame observations into a compact internal state, discover the environment's mechanics through efficient exploration, infer the win condition, and plan toward it in near-human action counts — repeatably and across environments the agent has never seen.

## Execution Constraints
The agent is expected to run in a **self-contained, offline setting** with no reliance on external network services at evaluation time. Any neural components must therefore be shipped with the solution and run locally rather than depending on hosted, network-served models. This constraint shapes the technical direction below and rules out architectures whose reasoning core is an external API call. Local engine play is also markedly faster than the online API, which makes offline operation the natural environment for both development and any learning the agent performs.

## Preferred Direction for Models
Empirically, large general-purpose language models perform poorly on this benchmark and cannot be relied upon in an offline setting. The most effective approaches to date are **lightweight, task-specific models that learn during play** — small convolutional or residual networks that adapt to the current environment within an episode. Accordingly, this project favors compact learned models over both a from-scratch foundation model and an externally served large language model. A small local reasoning model may be used as an optional hypothesis-generation layer, but it is secondary to learned search and not the backbone of the system.

## Potential Technical Solutions
The intended solution is a staged, offline-first system built in the following layers:

- **Environment harness** — reliable interaction with any ARC-AGI-3 game, including frame parsing, state-delta tracking, robust handling of the action and coordinate space, frame-driven action validation, terminal-state resets, and safe handling of invalid actions.
- **Exploration policy** — a learned action-effect model that predicts which actions and coordinates cause meaningful state changes, biasing exploration away from wasted moves.
- **Goal-directed planning** — a state-graph representation of observed transitions combined with a learned value model that ranks state–action pairs toward the next milestone, enabling efficient planning to each level's win condition while prioritizing progress into later, higher-weighted levels.
- **Optional reasoning layer** — a small local model that proposes hypotheses about mechanics and goals, validated by search over the learned model and tracked in structured memory.
- **Evaluation and benchmarking** — repeatable measurement across shared game subsets, reporting both level completion depth and action efficiency so that architecture variants can be compared on equal footing.

The detailed methodology, component architecture, frameworks, and version plan for these layers are maintained in `technical_plan.md`.
