# Counterfactual VoI Selector and On-Device VLM Analysis: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Eshan's contribution: a training-free counterfactual value-of-information (VoI) tool selector, compared head to head with Max's learned `signed` selector, and an on-device VLM study (Qwen2.5-VL-3B through mlx) that diagnoses the prompted VLM's failure and tests the VLM as a prior for VoI. Everything runs on an Apple Silicon Mac.

**Architecture:** For each decision, VoI builds weighted "world hypotheses" from the base observation only, simulates what each tool would report in each world, reruns the existing ranker, and scores a tool by the expected gain in ranker utility over not calling it. Decision rule: call `argmax_t VoI(t)` only if it is above λ. It plugs into Max's final-run harness as a method returning `(score, tool, allow)`, so both selectors are compared on the same rows, budgets and bootstrap. The VLM side fixes the float16 NaN bug, makes the failure diagnosis reproducible, adds yes/no questions scored by log-probability, and feeds `P(hidden road user)` into the VoI priors.

**Tech Stack:** Python 3, numpy, MetaDrive (existing), scikit-learn (AUROC), mlx and mlx-vlm 0.8.0 with `mlx-community/Qwen2.5-VL-3B-Instruct-4bit` (`requirements-vlm.txt`), pytest.

**Spec:** No separate spec doc. The plan argues from:
- `../work_plan.md` (ownership, ground rules)
- `research/2026-11-19_learned_selector/run2/PREREG2.md` (the `signed` baseline and its evaluation)
- `.agents/skills/doc/references/SEEDS.md` (seed rules)
- `scripts/flip_features.py` (Max's base-observation hypotheses, reused here)
- the agreed split: "contribution 1: max (learned selector); contribution 2: eshan (counterfactual value-of-information selector)", plus the VLM analysis

## Design decisions (fixed here, before any VoI evaluation)

- **No privileged information.** VoI reads only:
  - `base_observation(rec)`, the ego state, `rec["candidates"]`, `rec["signals"]["ego_stop_points"]`;
  - polygons of *visible* actors (as `features.py` already does).

  It never reads non-visible actors, `c_star`, `metrics`, `oracle_order`, `safe` or `signals["ego_status"]`.
- **Hypothesis classes.** These reuse `flip_features.py`:
  - `depth`: 8 redraws of visible actors with `BASE_NOISE`;
  - `occl_static`: a stopped vehicle at up to 6 occluded points on candidate paths;
  - `occl_ped`: a pedestrian at the same points;
  - `light`: an unread light set to red and to green;
  - `rear`: a fast vehicle 12 m behind in each adjacent lane;
  - `null`: the base observation itself.
- **Weights.** Each non-empty class gets prior weight π_class, normalized over the non-empty classes. Within a class, the weight is split evenly across its worlds.
  - `uniform` priors: every class 1.0. This is the primary, training-free variant.
  - `fitted` priors: per-class event rates on the train-split records (Task 4).
- **Utility.** `U(c, world) = score − UNSAFE_MARGIN_OFFSET·[not safe]`, computed with `ranker.predicted_metrics` on the world's belief. This is the ranker's own objective, so no new weights are introduced.
- **Tool response in a world.** Build a pseudo-record whose actors are the world's actors and whose light is the world's light. Run `TOOL_FNS[t](pseudo, level)` on it. The pseudo-record's `seed` is `f"{seed}|voi{k}"`, so each world gets its own noise stream through `rng_for` without touching `tools.LEVELS`.
- **VoI.** `VoI(t) = Σ_k w_k U(c_t,k, world_k) − Σ_k w_k U(c_now, world_k)`, where:
  - `c_now = rank(rec, base).top1`;
  - `c_t,k = rank(rec, merge(base, [response_t,k])).top1`.

  VoI can be negative, which is a predicted harmful call.
- **Selection.** `score = max_t VoI`, `tool = argmax_t VoI`, `allow = score > λ`.
  - `voi`: λ = 0, abstains naturally.
  - `voi_budget`: `allow = None`, budget only.
  - The tool noise level is known, so VoI simulates responses at that level.
- **VLM prior.** In `voi_vlm`, the combined weight of `occl_static` and `occl_ped` is `p_hidden`, the VLM's yes-probability for the `hidden` question, split evenly between the two classes. The other priors stay as they are. Each decision is charged one extra VLM call (`cost_offset = 1`).

## Global Constraints

- Branch `eshan/voi-selector`. Commit under Eshan's own name. Never push to `max`; this branch has no upstream until you run `git push -u origin eshan/voi-selector`.
- Seeds:
  - Tuning uses only the `val` split of `out/v2_dataset`.
  - The fresh final test is seeds **1160–1259**, opened exactly once, after `PREREG3.md` is committed.
  - Never use 400–459, 760–859 or 1060–1159 to choose anything.
- Paper numbers come from scripts reading `out/voi_eval/*.json` or `out/vlm_*/*.json`. Nothing is copied by hand.
- A new test counts only if it fails on the old code first.
- Every figure is a vector PDF (`pdfimages -list` shows no raster image).
- Multiprocess runs set `OMP_NUM_THREADS=1`. The Mac has 8 performance cores, so use `--procs 8`.
- mlx code imports lazily, so the non-VLM tests pass on machines without mlx.

## Review Focus

1. **A record with no visible actors, no occluded points and no stop line** has only the `null` world. Every VoI must be exactly 0.0 (not NaN), and the decision abstains. Test: Task 3, `test_voi_is_zero_when_only_null_world`.
2. **Hidden ground truth leaking in.** Changing non-visible actors, `c_star`, `metrics` or `signals["ego_status"]` must leave VoI unchanged. Test: Task 3, `test_voi_ignores_privileged_fields`.
3. **Determinism across processes.** The same record and level give identical VoI in two calls. Test: Task 3, `test_voi_is_deterministic`.
4. **Key-join drift** (`t_dec` floats such as 2.5000000000000004). `eval_voi.py` must align on `(family, int(seed), round(t_dec, 1))` and abort with the missing count, never silently drop rows. Test: Task 5, `test_align_aborts_on_missing_rows`.
5. **A non-finite VLM output** (NaN embedding or probability) must raise. It must never become `none`/0.0 in the cache. Test: Task 7, `test_cache_rejects_non_finite_embedding`; Task 9, `test_yes_prob_rejects_nan`.

---

### Task 1: Data on device

**Files:**
- Create: `research/2026-11-20_voi_selector/DATA.md` (provenance and the counts checked)

**Interfaces:**
- Produces, under `out/` (gitignored):
  - the datasets `v2_dataset/{train,val,test}.jsonl`, `v2_extra_ds`, `v3_extra_ds`;
  - the expected-gain labels `v2_expgain.jsonl`, `v2_extra_expgain.jsonl`, `v3_extra_expgain.jsonl`;
  - the sweep records `v2_sweep/*.jsonl`, which VoI needs because dataset rows lack actors and candidates.

- [ ] **Step 1: Ask Max for the `out/` bundle.** You need the files listed above plus `out/vlm_main/` (optional, for comparison with the 9B model). Unpack it into `out/`.
- [ ] **Step 2 (fallback if the bundle is unavailable): regenerate on the Mac.** About 40 min for the main seeds and about 1.5 h for the extra seeds at 8 processes:

```bash
OMP_NUM_THREADS=1 .venv/bin/python scripts/run_sweep.py --out out/v2_sweep --start-seed 100 --seeds 300 --chunk 5 --procs 8
.venv/bin/python scripts/build_dataset.py --sweep out/v2_sweep --out out/v2_dataset --procs 8
.venv/bin/python scripts/label_expected_gain.py --sweep out/v2_sweep --out out/v2_expgain.jsonl --draws 8 --procs 8
# repeat for 460-759 -> v2_extra_* and 860-1059 -> v3_extra_* with build_dataset.py --as-split train
```

- [ ] **Step 3: Verify the counts against Max's records.**
  - Train rows in `v2_dataset` must equal the `n_train` source counts in `research/2026-11-19_learned_selector/run2/experiments/log_final_geom.txt`.
  - Validation and test row counts must match `docs/baseline_results.md`.

  Run: `wc -l out/v2_dataset/*.jsonl` and compare. Record both sets of numbers in `DATA.md`. If any count differs, stop and resolve it with Max before going on.
- [ ] **Step 4: Check that the harness runs `signed` locally.**

```bash
OMP_NUM_THREADS=1 .venv/bin/python research/2026-11-19_learned_selector/run2/experiments/final.py \
  --methods signed uncertainty_margin always_on --test-dir v2_dataset --test-expgain v2_expgain.jsonl --splits val --out voi_eval/signed_val.json
```

  Expected: it writes `out/voi_eval/signed_val.json`. Compare the val `signed` mean_acc with the matching row in `research/2026-11-19_learned_selector/experiments/tables.md`, and record both numbers and any difference in `DATA.md`.
- [ ] **Step 5: Commit.** `git add research/2026-11-20_voi_selector/DATA.md && git commit -m "record data provenance for the VoI selector work"`

### Task 2: Shared hypothesis generator (refactor of Max's flip code)

**Files:**
- Create: `cassvla/planning/hypotheses.py`
- Modify: `scripts/flip_features.py` (so that `flip_row` calls `hypotheses()`)
- Create: `tests/fixtures/records_small.jsonl` (1 retained record per family, copied from `out/sweep_dev`), `tests/fixtures/flip_expected.json`
- Test: `tests/test_hypotheses.py`

**Interfaces:**
- Produces: `hypotheses(rec: dict, base: dict, draws: int = 8, max_points: int = 6) -> dict[str, list[dict]]`.
  - Keys: `depth`, `occl_static`, `occl_ped`, `light`, `rear`. Each value is a list of full beliefs (`dict(actors=[...], light=..., collision=None)`).
  - Classes that don't apply return an empty list.
  - The random stream is `tools.rng_for(rec, "flip")`, consumed in exactly the current `flip_row` order.
- Produces: `hypothetical_actor(name: str, kind: str, pos, vel, heading: float) -> dict`, the current `_actor`, moved here.

- [ ] **Step 1: Freeze the golden output.** With the *current* `scripts/flip_features.py`, write `flip_row(r)["flip"]` for every fixture record into `tests/fixtures/flip_expected.json` (a small one-off snippet; don't commit the snippet).
- [ ] **Step 2: Write the failing tests.**

```python
def test_flip_features_unchanged_by_refactor(): # every fixture: flip_row(rec)["flip"] == expected (exact list equality)
def test_hypotheses_use_only_visible_actors():  # names of base actors ⊆ every belief's actor names; no actor named like a non-visible rec actor
def test_light_hypotheses_only_when_unread():   # light == [] when base["light"] is not None or no stop line; else 2 beliefs, lights {RED, GREEN}
```

- [ ] **Step 3: Run the tests.** Run: `.venv/bin/python -m pytest tests/test_hypotheses.py -v`. Expected: FAIL, because `cassvla.planning.hypotheses` doesn't exist yet.
- [ ] **Step 4: Move the hypothesis code.** Move the world construction from `flip_row` into `hypotheses()`. `flip_row` keeps only the flip counting.
- [ ] **Step 5: Run the tests again.** Run: `.venv/bin/python -m pytest tests/test_hypotheses.py tests/ -q`. Expected: all pass.
- [ ] **Step 6: Commit.** Message: `move flip hypotheses into cassvla/planning/hypotheses.py for reuse by the VoI selector`. Tell Max the file moved; the outputs are identical.

### Task 3: VoI core

**Files:**
- Create: `cassvla/planning/voi.py`
- Test: `tests/test_voi.py` (the module fixture builds records with `Oracle`, as `tests/test_tools.py::recs` does: `occluded_pedestrian` 0 @1.5, `ambiguous_light` 0 @2.0, `merge_closing_speed` 0 @3.0)

**Interfaces:**
- Consumes: `hypotheses()` from Task 2; `rank`, `predicted_metrics`, `UNSAFE_MARGIN_OFFSET` from `ranker.py`; `TOOLS`, `TOOL_FNS`, `base_observation`, `merge` from `tools.py`.
- Produces:
  - `CLASSES = ("null", "depth", "occl_static", "occl_ped", "light", "rear")`
  - `UNIFORM = {c: 1.0 for c in CLASSES}`
  - `weighted_worlds(rec, base, priors: dict, draws: int = 8, classes=CLASSES) -> list[tuple[float, dict]]`: weights sum to 1.
  - `pseudo_record(rec, world: dict, k: int) -> dict`: actors carry `position`, `measured_velocity`, `poly` (box corners from position, heading, length and width), `length`, `width`, `heading`, `name`, `type`; `seed = f"{rec['seed']}|voi{k}"`; `signals["ego_status"]` is set to the world's light.
  - `utility(cand: dict, belief: dict, stops: list) -> float`
  - `voi(rec, level: str, priors: dict = UNIFORM, draws: int = 8, classes=CLASSES) -> dict`: returns `{"voi": {tool: float}, "top_now": str, "n_worlds": int, "seconds": float}`.
  - `select(voi_by_tool: dict, lam: float = 0.0) -> tuple[float, int, bool]`: returns `(score, tool_index into TOOLS, allow)`.

- [ ] **Step 1: Write the failing tests.**

```python
def test_weights_sum_to_one_and_skip_empty_classes(recs)       # abs(sum(w)-1) < 1e-9; no world from a class whose hypotheses() list is empty
def test_voi_is_zero_when_only_null_world(recs)                # classes=("null",) -> every voi == 0.0 exactly; select(...)[2] is False
def test_voi_ignores_privileged_fields(recs)                   # copy rec; change c_star, metrics, oracle_order, signals["ego_status"],
                                                               # and move every non-visible actor by 5 m -> voi(...) identical
def test_voi_is_deterministic(recs)                            # two calls equal (dict equality)
def test_perfect_roi_has_highest_voi_behind_occluder(recs)     # occluded_pedestrian rec, level "perfect", classes=("null","occl_ped"):
                                                               # voi["roi"] > voi["depth"] and voi["roi"] > 0
def test_light_world_values_roi_on_unread_light()              # Oracle("ambiguous_light", 0): first t in (1.0, 1.5, 2.0, 2.5) whose base["light"] is None
                                                               # and light_stop_distance is not None (pytest.skip if none);
                                                               # classes=("null","light"), level "perfect" -> argmax tool is "roi"
def test_select_abstains_below_lambda()                        # select({"roi":-1,"depth":0.0,"collision":-2}, 0.0) == (0.0, 1, False)
```

- [ ] **Step 2: Run the tests.** Run: `.venv/bin/python -m pytest tests/test_voi.py -v`. Expected: FAIL, because `cassvla.planning.voi` doesn't exist yet.
- [ ] **Step 3: Implement `voi.py`.** The core loop:

```python
base = base_observation(rec); ranked = rank(rec, base); now = ranked["top1"]
cands = {c["name"]: c for c in rec["candidates"]}; stops = [p[:2] for p in (rec["signals"].get("ego_stop_points") or {}).values()]
worlds = weighted_worlds(rec, base, priors, draws, classes)
v_now = sum(w * utility(cands[now], wd, stops) for w, wd in worlds)
for t in TOOLS:
    v_t = 0.0
    for k, (w, wd) in enumerate(worlds):
        resp = TOOL_FNS[t](pseudo_record(rec, wd, k), level)
        pick = rank(rec, merge(base, [resp]))["top1"]
        v_t += w * utility(cands[pick], wd, stops)
    out[t] = v_t - v_now
```

- [ ] **Step 4: Run the tests again.** Run: `.venv/bin/python -m pytest tests/test_voi.py -v`. Expected: PASS.
- [ ] **Step 5: Commit.** Message: `add training-free counterfactual VoI selector`.

### Task 4: VoI scores and priors over a sweep, with profiling

**Files:**
- Create: `scripts/voi_scores.py`, `scripts/voi_priors.py`
- Test: `tests/test_voi_scripts.py`

**Interfaces:**
- `voi_priors.py --sweep DIR --manifest out/v2_dataset/manifest.json --out out/voi/priors_fitted.json`
  - Uses only the manifest's `train` seeds.
  - Output: `{"null": 1.0, "depth": 1.0, "occl_static": r_s, "occl_ped": r_p, "light": r_l, "rear": r_r}`, where each `r_*` is the fraction of train decisions with that class's world non-empty in which the event is real.
    - `occl_static`/`occl_ped`: a non-visible vehicle or pedestrian lies within `ROI_MARGIN` of any occluded point.
    - `light`: the true light ≠ green.
    - `rear`: a real vehicle within 20 m behind in an adjacent lane.
  - Privileged fields are allowed here only, because this is the training-time calibration.
- `voi_scores.py --sweep DIR [DIR...] --out FILE.jsonl --levels low mid high --priors uniform|PATH --draws 8 --classes ... [--vlm-yesno FILE] --procs 8`
  - First line: `{"config": {...priors, draws, classes, git_sha}}`.
  - Then one line per retained record: `{"family", "seed", "t_dec", "levels": {lv: {"voi": {...}, "top_now": ...}}, "seconds": float}`.
- `--vlm-yesno` (used in Task 10) sets per-record `priors["occl_static"] = priors["occl_ped"] = p_hidden / 2`.

- [ ] **Step 1: Write the failing tests.**

```python
def test_voi_scores_writes_config_then_one_row_per_retained_record(tmp_path)  # run main() on tests/fixtures/records_small.jsonl; rows == retained count
def test_priors_use_train_seeds_only(tmp_path)                                 # fixture manifest with all fixture seeds in val -> SystemExit("no train records")
```

- [ ] **Step 2: Run the tests.** Run: `.venv/bin/python -m pytest tests/test_voi_scripts.py -v`. Expected: FAIL (the scripts don't exist yet).
- [ ] **Step 3: Implement both scripts.** Follow the `imap_unordered` pattern from `flip_features.py`.
- [ ] **Step 4: Run the tests again.** Expected: PASS.
- [ ] **Step 5: Run on val and test, and profile.**

```bash
OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_scores.py --sweep out/v2_sweep --out out/voi/v2_uniform.jsonl --priors uniform --procs 8
.venv/bin/python scripts/voi_priors.py --sweep out/v2_sweep --manifest out/v2_dataset/manifest.json --out out/voi/priors_fitted.json
OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_scores.py --sweep out/v2_sweep --out out/voi/v2_fitted.jsonl --priors out/voi/priors_fitted.json --procs 8
```

  Expected: one row per retained record, and the mean `seconds` per decision is printed (it is the latency entry for the paper).
- [ ] **Step 6: Commit.** Commit the scripts and tests only; `out/` is ignored. Message: `add VoI score and prior scripts`.

### Task 5: VoI in the final-run harness

**Files:**
- Create: `scripts/eval_voi.py`
- Test: `tests/test_eval_voi.py`

**Interfaces:**
- Consumes:
  - `research/2026-11-19_learned_selector/run2/experiments/final.py`, imported by path: `run_method`, `at_budget`, `ci`, `M.Ctx`, `X.evaluate`, `M.summarize`, `BUD06`;
  - the VoI rows from Task 4;
  - `select()` from Task 3.
- Produces:
  - `align(voi_rows: list[dict], split_rows: list[dict], level: str, lam: float | None) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]`, i.e. `(score, tool, allow)` in `split_rows` order. `lam=None` gives `allow=None`.
  - The CLI `eval_voi.py --methods voi voi_budget voi_fitted voi_vlm signed uncertainty_margin always_on --voi NAME=FILE ... --test-dir ... --splits ... --out out/voi_eval/<name>.json`.
  - The output JSON has the same layout as `final.py`'s, plus `cost_offset` (`voi_vlm`: 1.0) and `hypotheses` (V1–V4, once `PREREG3.md` exists; before that, `"status": "not run"`).

- [ ] **Step 1: Write the failing tests.**

```python
def test_align_orders_by_split_rows()            # shuffled voi rows -> score follows split row order; tool == TOOLS.index(argmax)
def test_align_aborts_on_missing_rows()          # drop one voi row -> SystemExit whose message contains "1 of"
def test_align_matches_t_dec_float_noise()       # split row t_dec 2.5000000000000004 matches voi row 2.5
def test_lambda_none_gives_budget_only()         # align(..., lam=None)[2] is None
```

- [ ] **Step 2: Run the tests.** Run: `.venv/bin/python -m pytest tests/test_eval_voi.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement `eval_voi.py`.** VoI methods feed `align()` output straight into `X.evaluate` and `at_budget`. `signed`, `uncertainty_margin` and `always_on` go through `final.run_method` unchanged.
- [ ] **Step 4: Run the tests again.** Expected: PASS.
- [ ] **Step 5: Run the validation comparison.**

```bash
OMP_NUM_THREADS=1 .venv/bin/python scripts/eval_voi.py --methods voi voi_budget voi_fitted signed uncertainty_margin always_on \
  --voi voi=out/voi/v2_uniform.jsonl voi_fitted=out/voi/v2_fitted.jsonl --test-dir v2_dataset --test-expgain v2_expgain.jsonl --splits val --out out/voi_eval/val.json
```

  Expected: it writes `val.json` with mean_acc, unsafe and at_budget_0.6 for every method at all three levels.
- [ ] **Step 6: Commit.** Message: `evaluate the VoI selector against the learned selector in the final-run harness`.

### Task 6: VoI ablations on validation, then freeze the settings

**Files:**
- Modify: `scripts/eval_voi.py` (add `--ablations`)
- Create: `research/2026-11-20_voi_selector/VAL_RESULTS.md` (generated by `scripts/eval_voi.py --report`)

**Interfaces:**
- `--ablations` runs these variants on `--splits val`:
  - `draws ∈ {4, 8, 16}`;
  - each class dropped in turn;
  - `uniform` vs `fitted` priors;
  - noise-aware (simulate at the true level) vs noise-unaware (always simulate at `mid`);
  - λ ∈ {0, budget-only}.

  Each variant needs its own `voi_scores.py` file, `out/voi/abl_<name>.jsonl`; the command list is in the script docstring.
- Output: `out/voi_eval/val_ablations.json`, with mean accuracy over budgets, a seed-bootstrap CI, and the delta against the frozen reference.

- [ ] **Step 1: Write a failing test.** `test_ablation_names_are_unique_and_reference_first` (on the variant list constant).
- [ ] **Step 2: Implement the variants. Run the test** and check that it passes.
- [ ] **Step 3: Run the ablations and generate the report.** Run them on val, then write `VAL_RESULTS.md` with `--report`.
- [ ] **Step 4: Freeze the settings.** Write the chosen `draws`, `classes`, `priors` and `λ` into `research/2026-11-20_voi_selector/FROZEN.json`. After this, nothing about VoI changes.
- [ ] **Step 5: Commit.** Message: `add VoI ablations on validation and freeze the settings`.

### Task 7: VLM float16 NaN fix and guard

**Files:**
- Modify: `cassvla/perception/vlm.py` (`MLXBackend.__init__`, `MLXBackend.embed`, `cache_frames`)
- Test: `tests/test_vlm.py`

**Interfaces:**
- `MLXBackend.__init__` runs `self.model.vision_tower.set_dtype(mx.float32)`; `embed()` casts `pixel_values` to `mx.float32`.
- `cache_frames` raises `ValueError(f"non-finite embedding for {key}")` before writing anything for that frame.
- `meta.json` gains `"vision_dtype": "float32"`. A cache made with a different value is refused, by the same rule as `model`/`revision`/`prompt_hash`.

- [ ] **Step 1: Write the failing tests.**

```python
def test_cache_rejects_non_finite_embedding(tmp_path)   # fake backend whose embed returns np.full(8, np.nan) -> ValueError; no emb_*.npz written
def test_cache_refuses_mixed_vision_dtype(tmp_path)     # meta.json with vision_dtype "float16" -> ValueError mentioning vision_dtype
```

- [ ] **Step 2: Run the tests.** Run: `.venv/bin/python -m pytest tests/test_vlm.py -v`. Expected: the 2 new tests FAIL.
- [ ] **Step 3: Implement the fix and the guard.**
- [ ] **Step 4: Run the tests again.** Expected: PASS.
- [ ] **Step 5: Check on the real frame.**

  Run: `.venv/bin/python -c "..."` (embed and ask on `out/frames_dev/occluded_cross_traffic/108_8.0.png`).

  Expected: the embedding is finite, and `ask` returns parseable JSON instead of `!!!!`. Also time `embed` on 20 frames and record the float32 latency next to the old 0.33 s.
- [ ] **Step 6: Rebuild the dev cache and rerun the dev evaluation.** Rebuild into a new directory, `out/vlm_dev_fp32`, then rerun the dev VLM evaluation. The old `out/eval_dev_vlm` used a partial cache and is invalid.
- [ ] **Step 7: Commit.** Message: `run the VLM vision tower in float32 and reject non-finite embeddings`.

### Task 8: Reproducible prompted-VLM failure diagnosis

**Files:**
- Create: `scripts/vlm_probe.py` (the repo version of the scratchpad probe), `docs/vlm_failure_analysis.md`
- Test: `tests/test_vlm_probe.py`

**Interfaces:**
- `vlm_probe.py --cache out/vlm_dev_fp32 --frames out/frames_dev --sweep out/sweep_dev --variants orig describe ped occl noschema forced --keys K1 K2 ... --out out/vlm_probe/report.json`
- `report.json` holds:
  - `distinct_replies` (count and top 8);
  - `template_copies` (replies containing `roi|depth|collision|none`);
  - `light_confusion` (true `ego_status` × VLM light on `ambiguous_light`);
  - `light_on_no_light_families` (share answered green);
  - `query_counts`, `nan_frames`;
  - `variants` (`{key: {variant: reply}}`);
  - the model, revision and prompt hash.
- Pure analysis functions are importable for the tests: `summarize_replies(rows) -> dict` and `light_confusion(rows, records) -> dict`.

- [ ] **Step 1: Write the failing tests.**

```python
def test_summarize_counts_template_copies()     # rows with one '"query": "roi|depth|collision|none"' -> template_copies == 1
def test_light_confusion_uses_ego_status()      # 2 fake rows + records -> {("TRAFFIC_LIGHT_RED","green"): 1, ...}
```

- [ ] **Step 2: Run them, implement the functions, run them again.** Expected: FAIL, then PASS.
- [ ] **Step 3: Run the probe.** Run it on the fp32 cache, with variants on 8 frames (2 each from `occluded_pedestrian`, `lane_blockage`, `lead_brake_cutin`, `ambiguous_light`).
- [ ] **Step 4: Write `docs/vlm_failure_analysis.md`.** Every number comes from `report.json`, and the doc keeps the four findings separate:
  1. template copying;
  2. the model perceives the pedestrian but ignores it in the answer;
  3. the tool choice stays constant even when `none` is removed;
  4. float16 NaNs, now fixed.

  Add the 3B vs 9B comparison (Max's `docs/phase5_vlm.md`: prompted 8% call rate) and the on-device cost table.
- [ ] **Step 5: Commit.** Message: `add a reproducible prompted-VLM failure analysis`.

### Task 9: Yes/no visual questions scored by log-probability

**Files:**
- Modify: `cassvla/perception/vlm.py` (add `QUESTIONS`, `MLXBackend.yes_prob`, `cache_yesno`), `scripts/cache_vlm.py` (add `--mode yesno`)
- Create: `scripts/eval_vlm_yesno.py`
- Test: `tests/test_vlm.py`, `tests/test_vlm_yesno.py`

**Interfaces:**
- `QUESTIONS`:
  - `pedestrian`: "Is there a pedestrian in this image? Answer Yes or No."
  - `hidden`: "Is part of the road ahead hidden behind a parked or stopped vehicle, so that a pedestrian or a car could be behind it? Answer Yes or No."
  - `red_light`: "Is the traffic light facing the car red or yellow? Answer Yes or No."
- `MLXBackend.yes_prob(image_path: str, question: str) -> float`: softmax over the first-token logits of "Yes" and "No" only. Raises `ValueError` if the result is non-finite.
- `cache_yesno(frames, frames_dir, backend, out_path) -> list[dict]`: resumable. Writes rows `{key, p: {q: float}, seconds}` to `out_path`. Its header records `questions_hash`.
- `eval_vlm_yesno.py --yesno FILE --sweep DIR --out out/vlm_yesno/eval.json` scores each question with AUROC and a 95% seed-bootstrap CI against truth taken from the records:
  - `pedestrian`: a `Pedestrian` actor within `CAMERA_RANGE` and `CAMERA_HALF_FOV`, visible or not, with visible and hidden cases also reported separately;
  - `hidden`: some actor within camera range and FOV fails `line_of_sight`;
  - `red_light`: `ego_status ∈ {RED, YELLOW}` and `light_stop_distance` is not None.

- [ ] **Step 1: Write the failing tests.**

```python
def test_yes_prob_rejects_nan()                      # backend stub whose logits are NaN -> ValueError
def test_cache_yesno_resumes(tmp_path)               # second call with same frames calls the backend 0 times
def test_truth_hidden_uses_line_of_sight()           # fixture record: an actor behind the parked car -> hidden truth True
def test_auroc_perfect_scores()                      # p == truth -> AUROC 1.0
```

- [ ] **Step 2: Run them, implement, run them again.** Expected: FAIL, then PASS.
- [ ] **Step 3: Render frames and score the questions.** Render frames for the v2 val and test rows on the Mac, then score them:

  `scripts/render_frames.py --records out/v2_dataset/val.jsonl out/v2_dataset/test.jsonl --out out/frames_v2`, then `scripts/cache_vlm.py --mode yesno`.

  Record seconds per frame and peak memory in `out/vlm_yesno/profile.json`.
- [ ] **Step 4: Evaluate.** Run `eval_vlm_yesno.py`; it writes `out/vlm_yesno/eval.json`.
- [ ] **Step 5: Commit.** Message: `add log-probability yes/no VLM questions and their AUROC evaluation`.

### Task 10: VLM as the prior for VoI (`voi_vlm`)

**Files:**
- Modify: `scripts/voi_scores.py` (`--vlm-yesno` from Task 4 interface), `scripts/eval_voi.py` (`voi_vlm`, `cost_offset`)
- Test: `tests/test_voi_scripts.py`

**Interfaces:**
- Consumes: `out/vlm_yesno/*.jsonl` (Task 9); the Task 4 `--vlm-yesno` behavior.

- [ ] **Step 1: Write the failing tests.**

```python
def test_vlm_prior_sets_occlusion_weights()   # p_hidden 0.0 -> occl worlds carry zero weight; total occl weight strictly increases over p_hidden 0.25, 0.5, 1.0
def test_vlm_prior_requires_every_row()       # a row without a yes/no entry -> SystemExit with the missing count
```

- [ ] **Step 2: Run them, implement, run them again.** Expected: FAIL, then PASS.
- [ ] **Step 3: Run on val.** Generate `out/voi/v2_vlm.jsonl` and add `voi_vlm` to the val run from Task 5. If `voi_vlm` is used in the final run, add its choice to `FROZEN.json`.
- [ ] **Step 4: Commit.** Message: `use the VLM's hidden-road-user probability as the VoI occlusion prior`.

### Task 11: Pre-registered final test on fresh seeds 1160–1259

**Files:**
- Create: `research/2026-11-20_voi_selector/PREREG3.md`
- Modify: `.agents/skills/doc/references/SEEDS.md` (add the row for 1160–1259)

**Interfaces:**
- Consumes: `FROZEN.json` (Tasks 6 and 10), `eval_voi.py`.
- Hypotheses. These must be written verbatim in `PREREG3.md` and committed *before* the sweep:
  - **V1 (primary):** `voi` is non-inferior to `signed` on mean accuracy over budgets 0–1. The lower bound of the paired seed-bootstrap 95% CI of `voi − signed` is above −0.01 at low, mid and high.
  - **V2:** `voi` beats `uncertainty_margin` at all three levels, with the CI above 0.
  - **V3:** at its own λ=0 call rate, `voi` is non-inferior to `always_on` in accuracy (CI lower bound > −0.01) and no less safe (unsafe-rate diff CI upper bound < +0.01), at all three levels.
  - **V4 (secondary, only if Task 10 ran):** `voi_vlm` beats `voi` at all three levels with the CI above 0. Both methods are compared at equal tool budget, and `voi_vlm`'s extra VLM call is reported as `cost_offset`.

- [ ] **Step 1: Commit the pre-registration.** Commit `PREREG3.md` and the `SEEDS.md` row with the message `pre-register the VoI final test on seeds 1160-1259`.
- [ ] **Step 2: Sweep, build, label and score the fresh seeds.** (About 2 h of compute with 8 processes, plus about 1.5 h of rendering and VLM if V4 runs.)

```bash
OMP_NUM_THREADS=1 .venv/bin/python scripts/run_sweep.py --out out/v5_sweep --start-seed 1160 --seeds 100 --chunk 5 --procs 8
.venv/bin/python scripts/build_dataset.py --sweep out/v5_sweep --out out/v5_final_ds --as-split final --procs 8
.venv/bin/python scripts/label_expected_gain.py --sweep out/v5_sweep --out out/v5_final_expgain.jsonl --draws 8 --procs 8
OMP_NUM_THREADS=1 .venv/bin/python scripts/voi_scores.py --sweep out/v5_sweep --out out/voi/v5_final.jsonl <FROZEN settings> --procs 8
```

- [ ] **Step 3: Run the final evaluation once.** Run `eval_voi.py` with the frozen methods: `--test-dir v5_final_ds --test-expgain v5_final_expgain.jsonl --splits final --out out/voi_eval/final.json`. Expected: each of V1–V4 shows pass or fail. Whatever the outcome, report it as is.
- [ ] **Step 4: Commit.** Commit `research/2026-11-20_voi_selector/FINAL.md`, generated from `final.json` by `eval_voi.py --report`, with the message `report the pre-registered VoI final test`.

### Task 12: Figures, results page and presentation numbers

**Files:**
- Modify: `scripts/make_figures.py` (add `voi`, `voi_vlm` and `signed` series; read `eval_voi.py` JSON)
- Test: `tests/test_figures.py` (extend `test_all_figures_are_vector` with a VoI report)
- Create: `docs/voi_selector.md`

**Interfaces:**
- `make_figures.py --voi-eval out/voi_eval/final.json --ablations out/voi_eval/val_ablations.json --yesno out/vlm_yesno/eval.json --out paper/figures` writes:
  - `voi_pareto_acc.pdf`, `voi_pareto_unsafe.pdf`;
  - `voi_ablations.pdf`;
  - `vlm_yesno_auroc.pdf`;
  - `latency.pdf` (VoI s/decision; MLP forward pass; VLM embed, ask and yes/no on the Mac).

- [ ] **Step 1: Extend the figure test.** It must fail until the VoI series exist.
- [ ] **Step 2: Implement the new figures. Run** `pytest tests/test_figures.py` and check that it passes.
- [ ] **Step 3: Generate the figures and write `docs/voi_selector.md`.** Every number in the doc comes from the JSON files.
- [ ] **Step 4: Commit.** Message: `add VoI and VLM figures and the results page`.

## Timeline

| Date | Done | Tasks |
|---|---|---|
| Nov 22 | Data on device, harness reproduces `signed` | 1 |
| Nov 25 | VoI core and val scores | 2, 3, 4 |
| Nov 27 | VoI vs `signed` on val; NaN fix | 5, 7 |
| Nov 30 | Ablations frozen; VLM failure analysis written. **Slides for Dec 1/3** (experiments, ablations, negative results) | 6, 8 |
| Dec 5 | Yes/no AUROC; `voi_vlm` on val | 9, 10 |
| Dec 8 | PREREG3 committed; final test run once | 11 |
| Dec 11 | Figures and results page; paper sections | 12 |
| Dec 15 | Submission | — |
