# Claude Code Instructions

Guidance for AI assistants (Claude Code) working in this repository. This mirrors the
standards in `.cursor/rules/` and `.github/copilot-instructions.md`. Read those for the
authoritative rules; this file adds practical "do / avoid, and in which file" guidance.

## Before Starting Work
- Review `memory_bank/project_context.md` and `memory_bank/technical_plan.md` for goal
  and technical direction.
- When touching anything under `memory_bank/`, read `memory_bank/memory_instructions.md`
  first, and keep each file aligned with its stated purpose.
- Check what is already built before adding new code or files.

## Python and Environment
- **Do**: use Python as the implementation language; manage dependencies and the
  environment with `uv`; keep all dependencies and configuration in `pyproject.toml`.
- **Do**: follow a standard `uv`-managed project layout.
- **Avoid**: editing `uv.lock` by hand, hand-rolling `pip`/`venv` workflows, or adding
  dependency declarations outside `pyproject.toml`.
- **Avoid**: committing secrets. `.env` holds `ARC_API_KEY` and is gitignored — never
  hardcode the key or move it into tracked files.

## Project-Direction Files (`memory_bank/`)
- `project_context.md` — **only** the project goal and potential technical solutions.
  Keep it formal and prose-based. Do **not** add prizes, deadlines, money, changelogs,
  or Q&A-style content.
- `technical_plan.md` — methodology, key features, frameworks, skills, tools, and the
  version plan for each solution stage.
- `roadmap.md` — what is completed, what is left to do, and challenges to overcome.
- Update `project_context.md` / `technical_plan.md` only when a request causes a major
  project-direction or technical-plan change.

## Logging (`memory_bank/ai_assistant_logging.md`)
- **Do** log here only for **coding work**: code changes, bug fixes, bug investigation,
  implementation, or when the user explicitly asks to log.
- When logging: newest entry at the **top**, include a date/timepoint heading, and use the
  `userRequest` and `summaryAICompletion` fields with bullet points for multiple actions.
- **Avoid** logging unrelated chat, rule-only updates (`.cursor/rules/*`, `CLAUDE.md`),
  documentation-only changes, or memory-bank-only edits.

## Agent Code (when it exists)
- Keep the system **offline-first**: do not architect the reasoning core around external
  network/API calls; neural components must run locally and ship with the solution.
- Respect the benchmark's action-efficiency goal — internal computation is free, external
  actions are scored. Prefer designs that reduce environment actions.
- Always validate model/agent outputs into valid ARC actions with safe fallbacks; never
  let a malformed action crash the loop.
- Keep environment interaction, agent policy, and evaluation logic in separate modules so
  approaches can be swapped and compared without coupling to one game.
- `smoke_test.py` is the minimal local entry point for stepping a game; keep it runnable.

## General
- Make small, reviewable changes; match the style of surrounding code.
- Prefer the offline/local toolkit mode for fast iteration; use online mode only when an
  official run is explicitly needed.
