# Roadmap

## Completed
- Reviewed the official ARC-AGI-3 quickstart documentation
- Reviewed the ARC-AGI Toolkit overview documentation
- Created an initial `project_context.md`
- Created an initial `technical_plan.md`
- Refined memory-bank files to align with `memory_instructions.md`
- Revised `technical_plan.md` to focus on solving ARC-AGI-3 rather than only environment setup
- Researched the competition and corrected the plan: completion-gating, RHAE scoring with ~1.15x cap and upper-median human baseline, offline execution, and the concrete action interface
- Identified candidate solution architectures: reactive baseline, memory-augmented agent, hypothesis-driven planner, search-based planner, local reasoning model, and a hybrid architecture
- Set up the Python project with `uv`
- Added and verified `pyproject.toml`
- Installed `arc-agi`
- Created a minimal local smoke-test script
- Built an initial in-house `ArcEnv`/runner baseline, then **migrated to the official ARC-AGI-3-Agents framework** (added as a git submodule under `external/ARC-AGI-3-Agents`); dropped the custom env and runner
- Ported `RandomAgent` and the `ActionEffectAgent` exploration policy to subclass the framework's `Agent`; `smoke_test.py` now bootstraps the submodule, registers our agents into `AVAILABLE_AGENTS`, and delegates to the framework `main()`
- Validated the new structure end-to-end online: `actioneffectagent` ran on `ls20` through the framework and produced an online scorecard
- **Submitted the `action_effect` baseline to Kaggle end-to-end and scored 0.1 (10%)** on the public leaderboard (notebook `birdyliu1023647/team647-v1`); the full pipeline (push notebook → attach competition Input in UI → offline rerun against `gateway:8001` → auto-generated `submission.parquet`) is now verified working

## Left To Do
- Improve on the 0.1 baseline (the action-effect agent only completes a fraction of levels; raise completion rate and action-efficiency)
- Establish baseline metrics for the action-effect agent across several games and compare against the random baseline
- Build a **perceptual front-end** (raw grid → objects/sameness/relations/frame-diff causality) as the Version 2 input layer; see `research/perception_frontend_design.md`
- Design structured memory and a state graph for action/outcome tracking (Version 2)
- Add a learned value model to rank (state, action) pairs toward the next milestone (Version 3)
- Implement hypothesis-driven exploration and exploit/explore switching
- Add evaluation scripts for multiple games and version-to-version comparison
- Integrate benchmarking, replay review, and scorecard comparison

## Challenges To Overcome
- Translating frame observations into compact internal state and useful hypotheses
- Balancing exploration for rule discovery against efficient execution for score
- Designing memory that helps generalization instead of bloating context with noise
- Adding planning/search without making the system too slow or too complex
- Getting local ARC environments available in offline mode so smoke tests can step through real games
- Balancing terminal-rendered debugging with fast non-rendered evaluation
- Designing a structure that supports multiple games without coupling logic too tightly to one environment
