# Roadmap

## Completed
- Reviewed the official ARC-AGI-3 quickstart documentation
- Reviewed the ARC-AGI Toolkit overview documentation
- Created an initial `project_context.md`
- Created an initial `technical_plan.md`
- Refined memory-bank files to align with `memory_instructions.md`
- Revised `technical_plan.md` to focus on solving ARC-AGI-3 rather than only environment setup
- Identified candidate solution architectures: reactive baseline, memory-augmented agent, hypothesis-driven planner, search-based planner, LLM-centered reasoning agent, and a hybrid architecture
- Set up the Python project with `uv`
- Added and verified `pyproject.toml`
- Installed `arc-agi`
- Created a minimal local smoke-test script

## Left To Do
- Validate environment stepping and scorecard output
- Build an instrumented baseline agent loop
- Design structured memory for action/outcome tracking
- Implement hypothesis-driven exploration logic
- Add evaluation scripts for multiple games
- Integrate benchmarking, replay review, and scorecard comparison

## Challenges To Overcome
- Translating frame observations into compact internal state and useful hypotheses
- Balancing exploration for rule discovery against efficient execution for score
- Designing memory that helps generalization instead of bloating context with noise
- Adding planning/search without making the system too slow or too complex
- Getting local ARC environments available in offline mode so smoke tests can step through real games
- Balancing terminal-rendered debugging with fast non-rendered evaluation
- Designing a structure that supports multiple games without coupling logic too tightly to one environment
