# Kaggle Submission Guide (ARC-AGI-3)

How to submit a Team647 agent to the **ARC Prize 2026 - ARC-AGI-3** Kaggle competition.
This captures the working procedure (and the dead ends) discovered while submitting the
`action_effect` baseline, so a future session can repeat it without re-deriving everything.

## Status: VERIFIED WORKING (2026-06)

The `action_effect` baseline was submitted end-to-end via this workflow and **scored 0.1
(10%)** on the public leaderboard. Notebook used: `birdyliu1023647/team647-v1`
(https://www.kaggle.com/code/birdyliu1023647/team647-v1). Note this slug differs from the
`team647-arc-agi-3-action-effect` slug referenced in older steps below — use `team647-v1`
(or whatever the current notebook slug is) when re-submitting.

## TL;DR — the working workflow

A **code competition**: submissions are notebooks that Kaggle reruns offline; the agent
plays the games and the submission file is auto-generated. The split that works:

1. **Claude (via Kaggle MCP):** build the notebook locally and `save_notebook` (push) it.
2. **User (Kaggle UI):** open the pushed notebook → **Add Input** → add the competition
   **"ARC Prize 2026 - ARC-AGI-3"** → **Save & Run All** (commit).
   *(This step is mandatory and can ONLY be done in the UI — see "What does not work".)*
3. **Claude (via Kaggle MCP):** once the input is attached, run
   `create_code_competition_submission` to submit. (Or the user clicks **Submit** in the UI.)

## Why this split — what does NOT work (verified)

| Attempt | Result |
|---|---|
| `create_code_competition_submission` on a notebook **without** the competition input | ❌ "Your Notebook must include this competition as a data source." |
| `save_notebook` with `competitionDataSources` (plain) | Pushes code, but **does not attach** the competition data bundle. |
| `save_notebook` with `competitionDataSourcesSetter` too | Still **not attached**. |
| `save_notebook` with `databundleVersionId` embedded in notebook `metadata.kaggle.dataSources` | Still **not attached**. |
| File-upload flow: `start_competition_submission_upload` → PUT file → `submit_to_competition` | ❌ "This competition only accepts Submissions from Notebooks." |

**Conclusion:** the Kaggle MCP `save_notebook` can push notebook *code* but cannot attach a
competition *data bundle*. Attaching the competition as an input must be done in the Kaggle
UI. Everything else (push, commit-run, final submit) can be done by Claude via MCP.

## Competition facts (as of 2026-06)

- Competition: `arc-prize-2026-arc-agi-3`, id **133468**, data bundle (`databundleVersionId`)
  **16244308**.
- **Kernels-only** (`is_kernels_submissions_only: true`); **1 submission/day**; runtime ≤ 9h;
  **internet disabled**; up to 2 final submissions; team size ≤ 8.
- Scoring: `level_score = (human_baseline_actions / agent_actions) ** 2`, **capped at 1.15
  per level** (NOT 1.0 — beating the human baseline scores above 1.0, up to +15%). Game
  score = weighted average of level scores (weight = level index, so later/harder levels
  count more); total = average of game scores. Human baseline = upper-median first-time
  human actions per level. Uncompleted levels score 0.
- **Leaderboard units are PERCENT, not a 0–1 fraction.** The theoretical max total is
  ~115% (the 1.15/level cap), so a value like `1.21` means **1.21%**, not 121%. Our
  `action_effect` baseline scored `0.1` = **0.1%**; current LB leaders are ~1.2% — the whole
  field is in the low single digits because ARC-AGI-3 is extremely hard for AI agents.
- Evaluation is on a **private 110-game set** (half public LB, half private LB); 25 public
  games ship in `environment_files/`.
- Competition data attached to a notebook mounts at
  `/kaggle/input/competitions/arc-prize-2026-arc-agi-3/` and contains:
  `arc_agi_3_wheels/` (offline pip wheels), `ARC-AGI-3-Agents/` (framework repo),
  `environment_files/` (public games).

## How the notebook works (the official recipe)

Based on the official samples (`inversion/arc3-sample-submission-random-agent` and
`...-stochastic-goose`). Our generated notebook lives at `kaggle/submission.ipynb`
(built by `kaggle/build_notebook.py`, which embeds `kaggle/my_agent.py`). Four cells:

1. **Install offline** from the bundled wheels:
   `pip install --no-index --find-links /kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels arc-agi python-dotenv`
   *(At commit/interactive time the wheels may not be mounted yet — that warning is
   expected; they ARE mounted during the scoring rerun.)*
2. **`%%writefile /kaggle/working/my_agent.py`** — the self-contained agent (subclasses the
   framework `Agent`, numpy-only, no `arc647`/internet deps), class `MyAgent` (CLI `myagent`).
3. **Rerun block**, guarded by `if os.getenv('KAGGLE_IS_COMPETITION_RERUN')`:
   - wait for the local game server: `curl http://gateway:8001/api/games`
   - copy `ARC-AGI-3-Agents` to `/kaggle/working/`, drop `my_agent.py` into
     `agents/templates/`
   - overwrite `agents/__init__.py` with a **minimal** one importing only
     `Agent, Playback, Swarm, Random, MyAgent` (avoids langgraph/smolagents deps that aren't
     installed)
   - write `.env` pointing at the local gateway: `SCHEME=http HOST=gateway PORT=8001
     OPERATION_MODE=online ARC_BASE_URL=http://gateway:8001/`
   - run `python main.py --agent myagent` (submission file is auto-produced by the gateway)
4. **Commit fallback**, guarded by `if not RERUN`: write a dummy `submission.parquet`
   (`row_id, game_id, end_of_game, score`) so the Submit button activates after a commit.

Key insight: "internet disabled" still works because the rerun provides a **local** game
server at `gateway:8001`; the framework runs in `OPERATION_MODE=online` but points at it.

## Step-by-step (commands / tools)

1. **Build** (local): `python kaggle/build_notebook.py` → writes `kaggle/submission.ipynb`.
   Run via WSL (this project's terminal convention) using the submodule env when needed.
2. **Push** (Claude, MCP `save_notebook`): `slug="<USER>/team647-arc-agi-3-action-effect"`,
   `kernelType="notebook"`, `language="python"`, `kernelExecutionType="SaveAndRunAll"`,
   `enableInternet=false`, `isPrivate=true`, `text=<contents of submission.ipynb>`.
   The slug MUST be `username/kernel-slug` (a bare slug errors "Invalid slug").
   User `BirdyLiu1023647` → kernel ref `birdyliu1023647/team647-arc-agi-3-action-effect`.
3. **Wait** for commit: MCP `get_notebook_session_status` until `COMPLETE`.
4. **User attaches input (UI):** open
   `https://www.kaggle.com/code/<user>/team647-arc-agi-3-action-effect/edit` → Add Input →
   "ARC Prize 2026 - ARC-AGI-3" → Save & Run All.
5. **Submit** (Claude, MCP `create_code_competition_submission`):
   `competitionName="arc-prize-2026-arc-agi-3"`, `kernelOwner="birdyliu1023647"`,
   `kernelSlug="team647-arc-agi-3-action-effect"`, `kernelVersion=<n>`,
   `fileName="submission.parquet"`, plus a description.
6. **Check** results: MCP `get_competition_submission` / `search_competition_submissions`,
   or the competition leaderboard. Mind the **1/day** limit — don't waste it on an untested
   commit.

## Kaggle MCP setup (so a new session has the tools)

- `.mcp.json` (repo root) runs the remote MCP via **`cmd /c npx`** (Windows can't spawn
  `npx` directly): `command: "cmd"`, args `["/c","npx","-y","mcp-remote",
  "https://www.kaggle.com/mcp","--header","Authorization: Bearer ${KAGGLE_API_TOKEN}"]`.
- Requires **Node.js** on Windows PATH (installed via `winget install OpenJS.NodeJS.LTS`) and
  the **`KAGGLE_API_TOKEN`** (a `KGAT_...` token from kaggle.com → Settings → API) set as a
  Windows **User** env var. After changing either, **fully restart Claude Code** (a `/mcp`
  reconnect is not enough) so it inherits the new PATH/env.
- Verify with a read-only call, e.g. MCP `get_competition` for `arc-prize-2026-arc-agi-3`.

## References

- Create-agent guide: https://docs.arcprize.org/create-agent
- Scoring methodology: https://docs.arcprize.org/methodology
- Competition (Kaggle): https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3
- Competition (ARC Prize): https://arcprize.org/competitions/2026/arc-agi-3
- Framework: https://github.com/arcprize/ARC-AGI-3-Agents (vendored at
  `external/ARC-AGI-3-Agents`)
- Official sample notebooks: `inversion/arc3-sample-submission-random-agent`,
  `inversion/arc3-sample-submission-stochastic-goose`
- Repo artifacts: `kaggle/my_agent.py`, `kaggle/build_notebook.py`, `kaggle/submission.ipynb`
- Related: `agents_catalog.md` (the agents), `technical_plan.md` (architecture/versions)
