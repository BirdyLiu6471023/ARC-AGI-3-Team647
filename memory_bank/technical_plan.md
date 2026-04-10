# Technical Plan

## Problem-Solving Objective
The technical goal of this project is to build an ARC-AGI-3 agent that performs well on unseen interactive environments under the benchmark's scoring model. Based on the docs, success is determined by two linked outcomes:

- Completing as many levels as possible
- Doing so with strong action efficiency relative to human baselines

This means the project should not optimize only for "can the environment run" or even "can the agent eventually win." It must optimize for sample-efficient exploration, correct rule discovery, and low-action execution after the agent has formed a useful strategy.

## Core Methodology
The project should follow a research-oriented methodology:

1. Build a baseline that can reliably interact with any ARC-AGI-3 game
2. Instrument the agent so every action can be analyzed against eventual score
3. Separate the game-solving loop into observation, hypothesis formation, exploration, execution, and post-action update
4. Compare multiple agent architectures on the same game sets rather than iterate blindly on a single prompt or model
5. Prefer methods that can generalize across unseen games instead of game-specific hand-tuning

The docs strongly imply that internal reasoning does not count as an action, while environment interactions do. This creates a major design principle for the project: spend more computation internally if it reduces external actions.

## Key Technical Insight From The ARC Docs
The benchmark is interactive and action-efficient, not just correctness-based. Therefore, the best agent architecture likely needs all of the following:

- Strong state interpretation from grid/frame observations
- Short-term and medium-term memory across frames
- Exploration policies for discovering game mechanics quickly
- Execution policies that exploit discovered rules efficiently
- Robustness against malformed or invalid action outputs
- Repeatable benchmarking across many games

This makes ARC-AGI-3 closer to a planning-and-adaptation problem than a pure next-action classification task.

## Candidate Solution Approaches
### Solution A: Reactive Baseline Agent
Description:
- A simple baseline that maps recent frames directly to the next action
- May use heuristics, a random policy with constraints, or a lightweight LLM prompt

Strengths:
- Fast to implement
- Good for validating the loop and collecting first recordings
- Provides a benchmark floor for later comparisons

Weaknesses:
- Likely poor action efficiency
- Weak at multi-step reasoning and delayed reward problems
- Limited generalization once tasks require explicit hypothesis tracking

Role in project:
- Necessary as a baseline, but not likely to be a competitive final approach

### Solution B: Memory-Augmented Agent
Description:
- Maintain a structured history of frames, actions, outcomes, and inferred mechanics
- Use memory to distinguish "what has been tried" from "what changed in the environment"

Strengths:
- Better suited for exploration-heavy games
- Can reduce repeated mistakes and wasted actions
- Aligns well with ARC's emphasis on memory and adaptation

Weaknesses:
- Requires careful design of state summarization
- Poor memory structure can create noisy or misleading context

Role in project:
- Strong candidate for the first serious general-purpose architecture

### Solution C: Hypothesis-Driven Planner
Description:
- Treat each game as an unknown system
- Explicitly infer candidate mechanics or goals from observed transitions
- Choose actions that either test a hypothesis or exploit a confirmed one

Strengths:
- Directly targets action efficiency
- Makes exploration purposeful rather than random
- Better fit for unseen games where rule discovery matters

Weaknesses:
- Harder to implement
- Requires good abstractions for game-state changes
- Can become computationally heavy if hypothesis space is too large

Role in project:
- Likely one of the most promising directions for solving ARC-AGI-3 well

### Solution D: Search-Based Action Planner
Description:
- Use local simulation, rollout, beam search, MCTS-like search, or action-sequence search over candidate futures when feasible
- Rank candidate sequences by expected information gain or expected score improvement

Strengths:
- Good for multi-step tasks where immediate rewards are sparse
- Can improve action efficiency by looking ahead before acting

Weaknesses:
- Search quality depends on available transition understanding
- May become expensive without a strong pruning strategy
- Not all games may be easy to search from raw observations alone

Role in project:
- Best used as a component inside a hybrid architecture rather than the only strategy

### Solution E: LLM-Centered Reasoning Agent
Description:
- Use an LLM to interpret frames, summarize state changes, propose hypotheses, and choose actions
- Optionally use structured prompting and reasoning metadata

Strengths:
- Flexible and fast to iterate
- Naturally supports language-based strategy tracking and hypothesis revision
- Compatible with official agent templates and benchmarking tooling

Weaknesses:
- Raw prompting alone may be inconsistent
- Vulnerable to malformed outputs or shallow pattern matching
- Can overfit prompt style without actually improving generalization

Role in project:
- Useful as a reasoning layer, but should likely be combined with memory, validation, and search

### Solution F: Hybrid Reasoning + Memory + Search Agent
Description:
- Combine an LLM or symbolic controller with structured memory and selective search
- Use memory to track experiments, reasoning to infer likely mechanics, and search to validate or optimize candidate action sequences

Strengths:
- Best alignment with ARC-AGI-3's interactive reasoning demands
- Balances flexibility with action efficiency
- Allows computation-heavy internal planning while minimizing external actions

Weaknesses:
- Highest implementation complexity
- Needs strong instrumentation and evaluation to avoid becoming opaque

Role in project:
- Recommended long-term target architecture for this repo

## Recommended Technical Direction
The preferred direction is a staged hybrid system:

1. Build a reactive baseline for instrumentation and sanity checks
2. Add structured memory so the agent can track experiments and environment changes
3. Introduce hypothesis-driven exploration to reduce wasted actions
4. Add targeted search or rollout for ambiguous high-impact decisions
5. Use benchmarking and scorecards to compare variants on the same game sets

This sequence keeps development practical while still aiming at the real benchmark objective: generalizable, action-efficient performance on unseen games.

## Agent Architecture To Build
The core agent should be organized into these components:

- Observation encoder: converts frame/game data into a compact internal representation
- Memory store: records prior frames, chosen actions, observed transitions, failures, and partial discoveries
- Hypothesis manager: proposes possible mechanics, goals, and interaction rules
- Exploration policy: chooses information-gathering actions when uncertainty is high
- Execution policy: chooses efficient task-completing actions once a useful strategy is found
- Action validator: ensures outputs always map to valid ARC actions and handles malformed model outputs safely
- Evaluation logger: records reasoning, actions, outcomes, and replay metadata for later analysis

## Key Features To Build
- Frame and state-delta tracking across time
- Structured memory of attempted actions and results
- Detection of repeated ineffective actions
- Exploration-versus-exploitation switching logic
- Valid-action parsing and fallback handling
- Support for multi-game experiments and comparisons
- Replay and scorecard analysis for failure review
- Support for both offline high-speed development and online official evaluation

## Frameworks And Libraries
- Python as the implementation language
- `uv` for dependency and environment management
- `pyproject.toml` for reproducible project configuration
- `arc-agi` for local and online ARC-AGI-3 environment interaction
- `arcengine` for game actions and environment control
- Optional LLM provider SDKs if the final architecture uses language models as the reasoning layer

## Technical Skills Needed
- Python software design for modular agents
- Interactive-agent architecture design
- Search and planning methods
- State representation and memory design
- Prompt/system design if LLM reasoning is used
- Experiment design and benchmarking
- Failure analysis using recordings, scorecards, and trajectory logs

## Tools Used
- ARC-AGI Toolkit for local development
- Online ARC scorecards and replays for official evaluation
- Benchmarking tooling for repeatable comparisons
- Swarm execution patterns for multi-game orchestration
- Memory-bank files for project-level context and research tracking

## Evaluation Strategy
Evaluation should reflect the actual ARC scoring philosophy:

- Measure both completion rate and action efficiency
- Start with a small stable subset of games for rapid iteration
- Use offline runs for fast development because local mode is much faster
- Use online runs to generate official scorecards and replays
- Compare agent versions on identical game subsets
- Analyze failed trajectories to determine whether failure came from poor observation, weak memory, incorrect hypotheses, or bad action selection

The docs also suggest that benchmarking, scorecards, recordings, and swarms are first-class parts of the workflow, so they should be integrated into the project rather than treated as optional extras.

## Solution Versions
### Version 0
Documentation and benchmark understanding.

Scope:
- Read the ARC quickstart, toolkit overview, scoring, agent, swarm, and benchmarking docs
- Define the actual project objective around solving ARC-AGI-3 efficiently

Status:
- Completed

### Version 1
Instrumented baseline solver.

Scope:
- Build a minimal agent that can run across sample games
- Add logging for frames, actions, results, and failures
- Establish the first measurable baseline for completion and efficiency

Status:
- Planned

### Version 2
Memory-augmented general agent.

Scope:
- Add structured memory and state-transition tracking
- Reduce repeated mistakes and improve exploration quality
- Compare against Version 1 on a shared benchmark subset

Status:
- Planned

### Version 3
Hypothesis-driven solver.

Scope:
- Add explicit rule/goal inference
- Distinguish exploratory actions from exploitative actions
- Improve action efficiency on unfamiliar games

Status:
- Planned

### Version 4
Hybrid planner.

Scope:
- Integrate selective search or rollout with memory and reasoning
- Use search on high-uncertainty or high-value decisions
- Evaluate tradeoffs between extra compute and fewer environment actions

Status:
- Planned

### Version 5
Benchmark-ready research system.

Scope:
- Scale to larger game subsets
- Add repeatable benchmarking and version-to-version regression checks
- Use online scorecards and replays for external validation

Status:
- Planned
