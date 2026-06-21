# Perceptual Front-End — Design Note

A design for giving the agent **human-like perception** of frames before any policy
runs. Captured as a planned Version 2 building block. See `../technical_plan.md` for where
it sits in the version plan and `../agents_catalog.md` for the current agents.

## Motivation

Humans win ARC-AGI-3 games in few actions because they bring **priors**: they see the
rendered grid and instantly perceive objects, sameness, containment, walls, counts, and
cause/effect. Our agent receives a raw `64×64` array of integers (color indices 0–15)
with **no built-in notion of objects, space, or causality**, so it burns hundreds of
actions per game just rediscovering what an object is and what each action does.

Important constraint: ARC-AGI-3 is **designed to defeat memorized semantics** — colors and
rules differ per game, and the private test set is *different games* from the public ones.
So we cannot ship a model that "knows what frames mean." What we can ship are **general,
structural priors that make the agent learn fast** — which is what the human advantage
actually is (skill-acquisition efficiency, not knowledge).

## What it is

One pure function per step: `grid (64×64 ints) -> Scene`. Stateless (the agent keeps
history); the front-end just turns one frame into structure. It runs on **every** action
for up to ~8h, so it must be cheap and **numpy/stdlib-only** — the Kaggle wheels bundle
only `arc-agi` + `python-dotenv` (no scipy), so connected-components must be hand-written,
not `scipy.ndimage.label`.

### Data model

```python
@dataclass
class Obj:
    color: int
    cells: np.ndarray              # (k,2) row,col coords
    bbox: tuple[int,int,int,int]   # r0,c0,r1,c1
    centroid: tuple[float,float]
    size: int
    mask: np.ndarray               # normalized HxW bool — position-free shape
    shape_id: int                  # hash(normalized mask + color) -> "sameness" key

@dataclass
class Scene:
    grid: np.ndarray               # (64,64) chosen layer
    background: int
    objects: list[Obj]
    color_hist: dict[int,int]
    symmetry: dict                 # {'h':bool,'v':bool,'transpose':bool,...}
    changed_mask: np.ndarray       # bool where this frame differs from previous
    changed_objects: list[int]     # indices of objects that changed (causality)
```

## Extraction pipeline

1. **Normalize input.** `frame` is `[layers][64][64]`; take the last layer (matches
   StochasticGoose's `frame[-1]`) -> single `(64,64)` int array.
2. **Find background.** Most-frequent color (data-driven; usually 0 but not always). Keep
   it on the Scene rather than deleting — sometimes the background color is meaningful.
3. **Connected components = objects (core).** Decisions:
   - **Connectivity:** default **4-neighbour** (diagonal touch usually isn't the same
     object), flag for 8.
   - **Same-color vs multi-color:** start with **same-color** components (unambiguous,
     fast); add multi-color composites later as a second pass kept *alongside* primitives.
   - Pure-numpy/stdlib BFS flood fill over foreground cells; ~ms for 64×64. Union-find /
     `np.roll` vectorization is the fallback if profiling flags it.
4. **Per-object features.** From cells: bbox, centroid, size, and the **normalized mask**
   (crop to bbox -> position-independent shape). `shape_id = hash(mask.tobytes()+color)`
   gives: **sameness** (equal shape_id = same thing -> group/count) and a stable identity
   to **track objects across frames** (match by shape_id + nearest centroid).
5. **Relations (cheap, high-value, compute lazily):** adjacency (dilate bbox by 1, test
   overlap), containment (bbox-inside + hole), alignment (shared centroid row/col).
6. **Symmetry (global priors):** `np.array_equal(grid, grid[:, ::-1])` etc. for v/h mirror,
   transpose, 180°. One-liners; strong puzzle-structure prior.
7. **Causality via frame-diff (the big one):** compare previous vs current grid ->
   `changed_mask`, attribute changed cells to objects -> `changed_objects`. The agent ties
   this to the **last action** (and last ACTION6 coordinate), turning "did anything
   change?" (current scalar signal) into "**action X moved object Y from here to there**" —
   raw material for a world model and goal inference.

## How it plugs in

Replaces the **input representation**, not the policy:

- **Now (tabular UCB `ActionEffectAgent`):** hash the **object set** (counts, shape_ids,
  positions) for novelty/loop-detection instead of the raw grid (object-aware novelty);
  target **ACTION6 at object centroids/edges** instead of a blind 64×64 heatmap — a large
  cut to the coordinate search space. These two are the cheap, measurable first wins.
- **Later (world model / planner):** objects + change-attribution are exactly the features
  a transition model and planner consume.

## Where it lives / verification

- `src/arc647/perception/scene.py`; mirror an inlined copy into `kaggle/my_agent.py` at
  build time (same offline constraint as the agent).
- Unit tests with tiny hand-built grids: 2-object grid, contained object, symmetric grid,
  before/after pair for change-attribution. Cheap, deterministic, no API.
- Sanity-check on a real live-dumped frame to confirm it parses an actual game sensibly.

## Honest risk

Perception makes the agent **see** objects; it does **not** tell it **which** objects to
pursue. Score gain comes only when the policy/planner *uses* these features to choose
goals. Reference point: StochasticGoose already learns a per-level CNN and still scores
~1% — so priors are necessary but not sufficient; **planning on top is where score comes
from**. Therefore: build perception as the input layer **and** immediately wire the cheap
wins (object-aware novelty + ACTION6-on-centroids) so we can A/B against the 0.1% baseline,
rather than building perception in a vacuum.

## Related context

- Frame format & action submission: frames are `[layers][64][64]` int grids (color indices
  0–15), symbolic not pixel-based; actions are HTTP POSTs to `/api/cmd/ACTIONn` returning a
  new `FrameData` (`arcengine.enums`).
- Scoring: completion-gated, then squared action-efficiency vs upper-median human baseline
  (capped 1.15/level). Completion is the dominant gate at our stage — see
  `../kaggle_submission_guide.md`.
- Alternatives considered: offline-pretrained world model, meta-learning (learn-to-learn
  for fast per-game adaptation), and a local VLM over rendered frames (off-table for the
  scored rerun: needs internet or a heavy bundled model; conflicts with offline-first).
