# Causal RL Foundations — Bareinboim, Zhang & Lee Monograph

Notes from **"An Introduction to Causal Reinforcement Learning"** (Bareinboim, Zhang, Lee;
Columbia / Seoul National Univ.; ~185pp). The foundational CRL text — broader and more
theoretical than the survey in `causal_rl_research.md`. PDF: https://causalai.net/r65.pdf

Companion to `causal_rl_research.md` (the survey-level note) and
`perception_frontend_design.md` (perception is the prerequisite for everything here). See
`../technical_plan.md` for the version plan.

## The reframing: agent actions ARE interventions

Everything is organized around the **Pearl Causal Hierarchy (PCH)**: L1 observational
("saw X and Y together"), L2 interventional ("*did* X, Y happened"), L3 counterfactual
("had I done X' instead..."). Key realization for us:

> An RL agent's every action is an intervention `do(X=x)`, so it natively generates **L2
> (interventional) data** — strictly more powerful than the L1 data most ML uses.

This is the theoretical license for **experiment-driven play**: our agent can run
experiments, not just observe. The paper models any RL environment as a **Structural Causal
Model (SCM)** = a collection of autonomous mechanisms; standard MDPs are a special case that
assumes no unobserved confounders.

## The two genuinely new, high-value ideas (vs. our prior note)

**1. "Where to Intervene" (CRL Task 2) -> POMIS / action + coordinate pruning. [STANDOUT]**
Given a causal graph, the paper defines the **Minimal Intervention Set (MIS)** and
**Possibly-Optimal MIS (POMIS)**: you only ever need to intervene on variables that are
**ancestors of the goal `Y`** in the graph (`X' ⊆ an(Y)`). Intervening on anything that
cannot causally affect the reward is **provably useless** and explicitly "harmful in terms
of sample efficiency."
- For us: once perception + frame-diff identify *which regions/objects causally affect
  progress*, spend actions — especially **ACTION6's 64×64 coordinates** — only on those.
  Turns the blind coordinate search into a small pruned set of "possibly-optimal" targets.
- Directly attacks **action-efficiency** (our squared score term) and the coordinate
  explosion. Most actionable new idea in the paper.

**2. Counterfactual Decision-Making (CRL Task 3) -> learn from actions you DIDN'T take.**
L3 reasoning ("would I have been better off doing `X'`?") lets the agent evaluate untried
actions **from a single trajectory** given a structural model — i.e. **counterfactual data
augmentation**, multiplying the learning extracted per real action. Directly attacks "few
actions to understand the game." Needs a (partial) structural model -> pairs with the world
model.

## Two more, with caveats

**3. Causal Imitation Learning (CRL Task 4) — plus a warning that matters.**
The competition exposes `baseline_actions` (human action counts per game, in
`EnvironmentInfo`). Tempting to imitate. But the paper's key result: **naive imitation can
FAIL under unobserved confounding** — the human acts on visual understanding the agent can't
see, so copying their action *distribution* is invalid. Causal imitation theory says *when*
imitation is sound and *which* variables to imitate on. Human data is usable, but **not by
blind behavior cloning**.

**4. Causal bandits / regret theory.**
Our UCB agent is literally a multi-armed bandit. The paper's bandit/regret analysis shows
**exploiting causal structure tightens regret bounds** (fewer suboptimal pulls = fewer
wasted actions), giving provable backing to "make exploration causal" and a cleaner
objective than raw UCB.

## Other framings worth remembering

- **Three sources of the causal model:** (1) a template (MAB/MDP), (2) prior knowledge,
  (3) structural learning. We can *seed* structure with priors (objectness, spatial
  adjacency = causal locality) instead of learning from scratch — ties to the perception
  front-end.
- **Offline-to-online (Sec 5):** combine offline data (public games, recordings) with
  online learning — fits our offline-first constraint (pretrain offline, adapt online).
- **Generalized policy learning / transportability:** transfer knowledge across
  environments with different distributions — the principle behind generalizing to the
  private (different-games) test set.

## Honest applicability check

This is a theory monograph: it generally assumes you *have or can learn* a causal graph,
plus identifiability and enough data. For a **single novel game, few actions, no resets,
offline**, the full machinery (do-calculus identification, transportability proofs) is not
runnable online. Value = **inductive biases + the pruning principle**, not the heavy
apparatus. The two lightweight, high-leverage exceptions — **POMIS intervention pruning**
and **counterfactual augmentation** — are implementable on top of the perception layer and
both target action-efficiency.

## Additions vs. `causal_rl_research.md`

| New idea (this monograph) | What it buys us | Effort |
|---|---|---|
| **Where-to-intervene / POMIS** | prune actions + ACTION6 coords to ancestors of progress | medium (needs partial causal graph from perception) |
| **Counterfactual augmentation** | extra learning per real action | high (needs structural model) |
| **Causal imitation + confounding caveat** | safe use of `baseline_actions` / human data | medium |
| **Causal bandit / regret** | principled replacement for raw UCB | low–medium |
| **Agent-as-interventionist (PCH L2)** | theoretical basis for experiment-driven play | framing |
| **Offline-to-online** | pretrain on public games, adapt online | medium |

## Source

- Bareinboim, Zhang & Lee — *An Introduction to Causal Reinforcement Learning* —
  https://causalai.net/r65.pdf
