# Causal Reinforcement Learning — Research Note

Research on whether **causal reinforcement learning (causal RL)** can help ARC-AGI-3, and
how it maps onto our plan. Companion to `perception_frontend_design.md` (perception is a
prerequisite for the ideas here). See `../technical_plan.md` for the version plan.

## Bottom line

Causal RL is conceptually one of the **best-fitting** research directions for this problem,
and our current `ActionEffectAgent` already stands on its first rung (rewarding
state-changing actions = a crude "action -> effect" heuristic). **But** most causal-RL
machinery assumes a sample budget we do not have (many episodes / millions of steps, with
resets). ARC-AGI-3 gives us *one* game, few scored actions, no convenient resets, and a
*different* game at test. So the value is the **inductive biases**, adopted lightweight —
not a full causal-discovery research stack run online during scoring.

## Why it fits our pain points

Surveys frame causal RL around four challenges; three are exactly ours
([Causal RL survey, arXiv 2307.01452](https://arxiv.org/pdf/2307.01452);
[IEEE TNNLS 2024 survey repo](https://github.com/libo-huang/Awesome-Causal-Reinforcement-Learning)):

1. **Sample efficiency** — learn in *few* interactions by excluding irrelevant factors.
   (Our "hundreds of actions to understand a game" problem.)
2. **Generalization / transfer** — causal structure transfers where surface statistics do
   not. (Our private-test-set-is-different-games problem.)
3. **Spurious correlations** — don't be fooled by changes you didn't cause. (Our "the grid
   flickered, was that me?" problem.)

## The pieces that fit ARC-AGI-3 well

1. **Controlled effects / blame assignment.**
   [*Did I do that?* (arXiv 2106.00266)](https://arxiv.org/pdf/2106.00266) separates changes
   the **agent caused** from ambient environment dynamics. Direct upgrade to the frame-diff
   "causality" step in the perception front-end: not "the grid changed" but "*my* action
   caused *this* object to change." Much cleaner learning signal.

2. **Causal / object-centric exploration instead of raw novelty.**
   [Causal Curiosity (arXiv 2010.03110)](https://arxiv.org/pdf/2010.03110) and
   [Causal Curiosity as intrinsic motivation, NeurIPS 2024](https://openreview.net/pdf?id=LZI8EFLoFD)
   reward changes to the agent's **internal causal model** — explore to discover mechanics,
   not to see new pixels (~2.5x less data than supervised planners in their setting).
   Crucial warning from the literature: **pure state-novelty exploration gets diverted to
   background variation rather than the object that matters** — exactly the failure mode of
   our current UCB/novelty agent on a busy 64x64 grid.

3. **Empowerment / controllable-factor objectives.**
   [Empowerment via causal structure in MBRL (arXiv 2502.10077)](https://arxiv.org/pdf/2502.10077)
   and [causal action empowerment (Sci China Inf Sci 2024)](https://link.springer.com/article/10.1007/s11432-024-4396-3)
   push the agent to maximize *control* over future states and focus its representation on
   **agent-controllable factors**, filtering uncontrollable ones. Good intrinsic objective
   for "find the game's mechanic fast."

4. **Sparse causal world model (vs. dense CNN).**
   [Explainable RL via a Causal World Model (arXiv 2305.02749)](https://arxiv.org/abs/2305.02749)
   learns a **sparse graph** of which action/variable affects which next-state variable,
   instead of StochasticGoose's dense per-level CNN. A sparse, factored transition model is
   cheaper, interpretable, and **transfers better to novel games** — the whole game on the
   private set.

## Honest caveats

- **Causal discovery from pixels/grids is itself hard** (the "causal induction" problem);
  it requires first expressing observations as high-level factors/objects
  ([Causal Discovery in Visual MBRL, arXiv 2107.00848](https://arxiv.org/pdf/2107.00848)).
  => Our **perception front-end is a prerequisite**, not an alternative. They compose.
- **Most methods assume many episodes / millions of samples** to recover the causal graph —
  too sample-hungry to run online during a single scored game.
- Therefore: adopt the **inductive biases** lightweight (controlled-effect attribution,
  causal/controllable-factor exploration, sparse factored transition model), not a
  heavyweight do-calculus pipeline.

## How it maps onto our plan

We are already on the first rung (`ActionEffectAgent` rewards state-changing actions). The
upgrades slot cleanly onto the existing Version 2/3 plan:

| Our planned piece | Causal-RL upgrade |
|---|---|
| Perception front-end (frame-diff) | **controlled-effect attribution** — agent-caused vs ambient change |
| Exploration (UCB / novelty) | **causal-curiosity / controllable-factor** intrinsic reward (avoids chasing background flicker) |
| Version 3 world model | **sparse causal / factored transition model** for planning + transfer |

**Recommendation:** treat causal RL as the **theoretical backbone** for Versions 2–3 —
apply the three biases above on top of the perception layer — but do not import a full
causal-discovery framework that needs a sample budget we will never have in a single offline
game.

## Sources

- Causal RL: A Survey — https://arxiv.org/pdf/2307.01452
- Awesome Causal RL (IEEE TNNLS 2024 survey) — https://github.com/libo-huang/Awesome-Causal-Reinforcement-Learning
- Did I do that? Controlled effects — https://arxiv.org/pdf/2106.00266
- Causal Curiosity — https://arxiv.org/pdf/2010.03110
- Causal Curiosity as Intrinsic Motivation (NeurIPS 2024) — https://openreview.net/pdf?id=LZI8EFLoFD
- Empowerment via Causal Structure Learning in MBRL — https://arxiv.org/pdf/2502.10077
- Causal action empowerment (Sci China Inf Sci 2024) — https://link.springer.com/article/10.1007/s11432-024-4396-3
- Explainable RL via a Causal World Model — https://arxiv.org/abs/2305.02749
- Causal Discovery in Visual MBRL — https://arxiv.org/pdf/2107.00848
- Causal Information Prioritization — https://arxiv.org/pdf/2502.10097
