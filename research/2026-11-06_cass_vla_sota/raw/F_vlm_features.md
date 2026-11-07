# F_vlm_features: frozen VLM / foundation-model representations as inputs to decision heads

All entries below had their arXiv abstract fetched with absfetch.py (verbatim metadata). I did not read full texts, so results
are abstract-level only. WebSearch summaries were wrong at least once (one summary mislabelled 2606.06219 as "CLEAR"; the
fetched record says it is "Vault"), so nothing here comes from a search summary alone.

## Summary
- No paper found that does candidate-conditioned perception-tool selection with VLM features. Closest in spirit: DualDriveVLA (2602.10719), where a learned scorer over a compact candidate trajectory set gates when the VLM is called (15% of scenarios), and ASSCG (2606.25509), which learns Query/Cache/Drop for the slow system under a compute budget. Neither chooses among perception tools, and gating in both is trajectory-set or scene-level, not tool-level.
- The strongest direct support for "read the hidden states, don't prompt": BLUE (2606.08684) trains a 0.11M-parameter gate on frozen VLA hidden states to decide per frame whether to generate language, stating hidden states encode benefit that scene complexity and kinematic features cannot predict. VLAlert (2609.08130) pools Qwen3-VL-4B hidden states for a SILENT/OBSERVE/ALERT policy (an abstain-like OBSERVE action, close to accept/inspect in the future phase). Both justify using the frozen Qwen embedding in the selector and suggest going beyond the pooled image embedding (LLM hidden states at structured token positions).
- Probing evidence is directly relevant to the +0.3 to +0.7 point gain and the "VLM says none" result: 2603.06054 shows presence is linearly encoded while orientation and far-distance concepts are not (perceptual vs cognitive failure); 2601.03464 shows prompting near chance vs linear probes F1 0.61-0.67 on the same model (time series, not driving); 2606.31257 warns that linear decodability can overstate grounding (blank-image control); 2605.20448 localises occlusion failures to the visual-token merger in Qwen3-VL-8B. Implication: probe layers before and after the merger, and add a blank-image control.
- Layer choice: Skean et al. (2502.02013) report mid-depth embeddings beat the last layer (text-centred); 2601.03464 finds class information emerges in early layers. I found no driving-specific middle-vs-last-layer study. Gap and an easy ablation for the thesis.
- Slow-fast designs now cache representations: Think at 5 Hz (2607.15621) exposes a frozen 7B backbone's per-layer KV cache to a fast action expert trained under random staleness; AsyncDriver and DriveVLM-Dual are earlier anchors. For the offline-cached-embedding set-up, staleness randomisation is an idea to borrow.
- Distillation of VLM/LLM latents into small planners (VERDI, Orion-Lite) is mature; relevant mainly as an alternative to feeding frozen features at test time.
- Frozen-encoder planning (FROST-Drive) beats fine-tuned encoders on Waymo E2E; supports keeping Qwen frozen.
- VLM-picks-from-candidates is now used (Slow Brain Fast Planner, SimpleVSF, MindDrive) but as a ranker, not as a tool-query selector. Useful as ranker baselines.

## Papers

### From Representational Complementarity to Dual Systems: Synergizing VLM and Vision-Only Backbones for End-to-End Driving
- id: arXiv:2602.10719 | date: 2026-02 | venue: arXiv preprint
- authors: Ang, Sining et al. | code: https://github.com/WilliamXuanYu/HybridDriveVLA (stated "will be available")
- relevance: HIGH — closest to candidate-set-conditioned gating of an expensive model: a learned trajectory scorer over a cross-model candidate set, with the VLM invoked only in some scenarios.
- what: Compares VLM hidden states (InternVL3, Qwen3VL) with vision-only encoders under a fixed diffusion planner; finds VLMs help in semantically complex long-tail cases, vision encoders in simple geometry scenes. HybridDriveVLA raises NAVSIM PDMS 90.80 to 92.10 via a learned scorer; DualDriveVLA invokes the VLM in 15% of scenarios for 91.00 PDMS with about 1.9x lower latency than the VLM baseline (abstract figures; a search summary said 3.2x throughput, not verified).
- thesis use: competitor/analogue for "VLM call decision at a budget"; oracle best-of-two selector (93.58 PDMS) mirrors the project's oracle selector. Cite as nearest dual-system gate, but it gates a model, not a perception tool.
- verified: abs meta fetched, html read

### ASSCG: Just-Right Gating over Chattering for Fast-Slow LLM Planning in Autonomous Driving
- id: arXiv:2606.25509 | date: 2026-06 | venue: arXiv preprint
- authors: Ang, Sining et al. | code: https://williamxuanyu.github.io/asscg/ (project page)
- relevance: HIGH — learns when to query the slow system under compute cost (Query/Cache/Drop), trained with SFT then GRPO-style compute-aware RL.
- what: Frame-level gate with RWKV backbone for AsyncDriver (nuPlan Hard20 67.28, +2.28, latency -60%) and a RecogDrive-based dual system on NAVSIM (91.4 PDMS, +0.6, speed +25%).
- thesis use: competitor for the "when to query" half; the Cache action maps to reuse of cached VLM embeddings. Not candidate-conditioned as far as the abstract shows (UNVERIFIED beyond abstract).
- verified: abs meta fetched

### BLUE: Toward Better Language Use in Efficient Vision-Language-Action Models for Autonomous Driving
- id: arXiv:2606.08684 | date: 2026-06 | venue: arXiv preprint
- authors: Ling, George et al. | code: github.com/George-Ling3/B... (URL truncated in the abstract record; full URL not recovered)
- relevance: HIGH — a gate on frozen VLA hidden states decides per frame whether the costly step (language) is worth running.
- what: Shows language helps or hurts on a small fraction of routes; scene complexity and kinematics alone struggle to predict benefit, but pretrained hidden states encode it. 0.11M-parameter gate gives 76.2% success on Bench2Drive, 36 DS on Longest6 v2, 2.54x speedup, +8.9% success over backbone.
- thesis use: idea to borrow (train the selector on LLM hidden states, not only image embeddings; benefit labels derived without extra annotation, similar to expected-gain targets). Supports the claim that geometry-only scene features are insufficient for the trigger.
- verified: abs meta fetched, html read

### Observe Before You Alert: Adaptive Driver Alerting with Vision-Language Models (VLAlert)
- id: arXiv:2609.08130 | date: 2026-09 | venue: arXiv preprint
- authors: Wang, Yuhang et al. | code: none seen
- relevance: HIGH — frozen-ish Qwen3-VL-4B hidden states, pooled from structured spans, feed a tri-action policy SILENT/OBSERVE/ALERT; OBSERVE delays and gathers evidence.
- what: Pools hidden states from structured belief spans for danger estimation and policy prediction; VLAlert-Bench from four dashcam datasets. AUROC 0.689 vs 0.610 baseline, AP_tick 0.195 vs 0.176, DAUS 0.4878 vs 0.4752 (abstract). The linear probe AUROC 0.894 is confirmed in the full text (Table 3a).
- thesis use: idea to borrow for the future accept/inspect/replan phase (an OBSERVE action) and for reading hidden states at structured token positions. Full text (see addendum) confirms the backbone is LoRA-adapted in stage 1 and then frozen for all heads.
- verified: abs meta fetched, html read, html read

### Think at 5 Hz, Act at 20 Hz: Asynchronous Fast-Slow Vision-Language-Action Inference for Closed-Loop Driving
- id: arXiv:2607.15621 | date: 2026-07 | venue: arXiv preprint
- authors: Li, Yun et al. | code: none seen
- relevance: MED — frozen 7B VLM exposes its per-layer KV cache as a standing scene representation; a fast action expert attends to it, trained under randomised staleness.
- what: LangAuto-Short in CARLA: route completion 37.0 to 94.0 over a frame-skipping baseline; expert transfers zero-shot to two unseen towns (84-94% RC). Waypoint error about 4x lower than the backbone's own action head in open loop.
- thesis use: idea to borrow (cache and staleness augmentation for cached VLM features); template for a frozen-VLM-plus-small-head design.
- verified: abs meta fetched

### Probing Visual Concepts in Lightweight Vision-Language Models for Automated Driving
- id: arXiv:2603.06054 | date: 2026-03 | venue: arXiv preprint
- authors: Theodoridis, Nikos et al. | code: none seen
- relevance: HIGH — linear probes on activations of five VLMs for driving concepts; separates perceptual failure (not linearly encoded) from cognitive failure (encoded but answered wrong); object distance degrades linear separability quickly.
- what: Counterfactual image sets differing in one concept; probes over vision encoder, projector, LLM layers. Presence is explicitly encoded; orientation is implicit or absent.
- thesis use: motivates why prompting says "none" (cognitive failure) and why a distance tool is needed (distance concept degrades); template for probing Qwen3.5-9B per layer on the project's hazard types.
- verified: abs meta fetched, html read

### Decodable Is Not Grounded: A Vision-Ablation Arbiter for VLM Spatial Reasoning
- id: arXiv:2606.31257 | date: 2026-06 | venue: arXiv preprint
- authors: Liao, Chih-Ting et al. | code: none seen
- relevance: MED — warns linear probes decode 73-97% on spatial axes, but blank-image control shows many are language priors; depth axis is "inverted" in 14 models.
- what: Introduces a vision-ablation arbiter; three regimes (grounded, prior, inverted).
- thesis use: caution/control to add to any probe or embedding-gain claim (replace image with gray blank).
- verified: abs meta fetched

### Do Vision-Language Models Understand 3D Scenes or Just Catalogue Objects?
- id: arXiv:2605.20448 | date: 2026-05 | venue: arXiv preprint
- authors: Maheshwari, Animesh et al. | code: none seen
- relevance: MED — occlusion accuracy 6-45% for six VLMs; on Qwen3-VL-8B-Thinking spatial info present in the vision encoder becomes inaccessible after the token merger and recovers when clean post-merger activations are patched in.
- what: 3,034-sample benchmark, 18,204 responses with human scoring.
- thesis use: evidence that frozen VLMs fail on occlusion, supporting an occlusion/ROI tool; suggests reading embeddings before the merger.
- verified: abs meta fetched

### Seeing Isn't Knowing: Do VLMs Know When Not to Answer Spatial Questions (and Why)?
- id: arXiv:2605.30557 | date: 2026-05 | venue: arXiv preprint
- authors: Zhang, Yue et al. | code: none seen
- relevance: MED — SPATIALUNCERTAIN: VLM behaviour does not track evidence reliability under occlusion; models that can name an informative viewpoint often do not realise they need one; internal analysis shows 2D relations readily decodable, 3D barely.
- what: Eight VLMs; failures not resolved by prompting or fine-tuning; a better viewpoint helps more than adding depth to the same view.
- thesis use: supports the failure of prompted tool choice ("none") and the premise that the selector cannot rely on VLM self-assessment.
- verified: abs meta fetched

### Prompting Underestimates LLM Capability for Time Series Classification
- id: arXiv:2601.03464 | date: 2026-01 | venue: arXiv preprint
- authors: Schumacher, Dan et al. | code: none seen
- relevance: MED — cleanest "probe beats prompt" result: zero-shot prompting near chance, linear probes F1 0.15-0.26 to 0.61-0.67; class information appears in early layers; visual input amplifies it. Includes VLMs. Not driving.
- thesis use: citation for the prompt-vs-probe gap and layer-wise reading.
- verified: abs meta fetched

### Layer by Layer: Uncovering Hidden Representations in Language Models
- id: arXiv:2502.02013 | date: 2025-02 | venue: ICML 2025 (per search result; not in abstract record)
- authors: Skean, Oscar et al. | code: none seen
- relevance: LOW-MED — mid-depth embeddings often beat the last layer across 32 text-embedding tasks. Text-centred, pre-2025-07.
- thesis use: justification for a layer sweep of cached embeddings.
- verified: abs meta fetched

### Self-Aware Safety Augmentation: Leveraging Internal Semantic Understanding to Enhance Safety in Vision-Language Models
- id: arXiv:2507.21637 | date: 2025-07 | venue: arXiv preprint
- authors: Wang, Wanying et al. | code: none seen
- relevance: LOW — linear probe at intermediate layers detects risk before generation in LVLMs (content safety, not driving).
- thesis use: weak support for probing pre-generation hidden states.
- verified: abs meta fetched

### Orion-Lite: Distilling LLM Reasoning into Efficient Vision-Only Driving Models
- id: arXiv:2604.08266 | date: 2026-04 | venue: arXiv preprint
- authors: Gu, Jing et al. | code: none seen
- relevance: MED — latent feature distillation from ORION's LLM plus ground-truth trajectory supervision; student surpasses teacher on Bench2Drive (DS 80.6).
- thesis use: alternative to test-time VLM features (distill into the selector); closed-loop evidence.
- verified: abs meta fetched

### VERDI: VLM-Embedded Reasoning for Autonomous Driving
- id: arXiv:2505.15925 | date: 2025-05 | venue: arXiv preprint (later versions to v4 in 2026)
- authors: Feng, Bowen et al. | code: none seen
- relevance: MED — aligns perception/prediction/planning latents with VLM reasoning text features at training time; up to 11% l2 improvement; nuScenes and HUGSIM.
- thesis use: idea to borrow for distilling VLM knowledge into the MLP selector. Slightly before the 2025-07 window.
- verified: abs meta fetched

### Drive-KD: Multi-Teacher Distillation for VLMs in Autonomous Driving
- id: arXiv:2601.21288 | date: 2026-01 | venue: arXiv preprint
- authors: Lian, Weitong et al. | code: none seen
- relevance: LOW — distilled InternVL3-1B beats pretrained 78B on DriveBench with about 42x less memory; uses layer-specific attention as distillation signal.
- thesis use: shows small students can match large VLM on perception/planning; background.
- verified: abs meta fetched

### On-Policy Distillation of Language Models for Autonomous Vehicle Motion Planning
- id: arXiv:2604.07944 | date: 2026-04 | venue: arXiv preprint
- authors: Afsharrad, Amirhossein et al. | code: none seen
- relevance: LOW — GKD on GPT-Driver, 5x smaller student near teacher on nuScenes.
- verified: abs meta fetched

### FROST-Drive: Scalable and Efficient End-to-End Driving with a Frozen Vision Encoder
- id: arXiv:2601.03460 | date: 2026-01 | venue: arXiv preprint
- authors: Dong, Zeyu et al. | code: none seen
- relevance: MED — frozen VLM vision encoder plus transformer adapter and GRU decoder outperforms full fine-tuning on Waymo Open E2E (abstract claim).
- thesis use: supports keeping the VLM frozen and training only a head.
- verified: abs meta fetched

### Slow Brain, Fast Planner: Latency-Resilient VLM-Augmented Urban Navigation
- id: arXiv:2606.20458 | date: 2026-06 | venue: arXiv preprint
- authors: Peng, Zhenghao "Mark" et al. | code: none seen
- relevance: MED — VLM selects one of the planner's candidate trajectories (index), stale selection fused with exponential decay; 30% ADE reduction vs planner's best selection on about 2,000 real scenarios; >80% success with delays up to 5s in sim.
- thesis use: baseline for the ranker (VLM picks among candidates); "trajectory scoring gap" framing matches the oracle-gap in the project.
- verified: abs meta fetched

### SimpleVSF: VLM-Scoring Fusion for Trajectory Prediction of End-to-End Autonomous Driving
- id: arXiv:2510.17191 | date: 2025-10 | venue: arXiv preprint (ICCV 2025 NAVSIM v2 challenge, per abstract)
- authors: Zheng, Peiru et al. | code: none seen
- relevance: MED — VLM-enhanced scorers plus VLM-based fusioner over candidate trajectories.
- thesis use: ranker baseline with VLM over candidates.
- verified: abs meta fetched

### MindDrive: An All-in-One Framework Bridging World Models and Vision-Language Model for End-to-End Autonomous Driving
- id: arXiv:2512.04441 | date: 2025-12 | venue: arXiv preprint
- authors: Sun, Bin et al. | code: none seen
- relevance: MED — VLM-oriented Evaluator scores candidate trajectories on safety, comfort, efficiency; NAVSIM v1 and v2.
- thesis use: VLM trajectory critic, comparator for the ranker stage.
- verified: abs meta fetched

### FASIONAD++ (FASIONAD): Fast-Slow Fusion Systems for Enhanced Safety in Autonomous Driving with Adaptive Feedback
- id: arXiv:2503.08162 | date: 2025-03 | venue: arXiv preprint
- authors: Qian, Kangan et al. | code: none seen
- relevance: MED — slow VLM activated by uncertainty estimation, with information bottleneck feedback; 6.7% L2 reduction in open loop (abstract).
- thesis use: the scene-uncertainty trigger analogue (same family as DriveAgent-R1 trigger); pre-window anchor.
- verified: abs meta fetched

### AutoMoT: A Unified Vision-Language-Action Model with Asynchronous Mixture-of-Transformers
- id: arXiv:2603.14851 | date: 2026-03 | venue: arXiv preprint
- authors: Huang, Wenhui et al. | code: none seen
- relevance: LOW-MED — asynchronous fast-slow in one MoT VLA; studies when AD-specific fine-tuning of the VLM is necessary.
- verified: abs meta fetched

### Enhancing End-to-End Autonomous Driving with Risk Semantic Distillation from VLM (RSD)
- id: arXiv:2511.14499 | date: 2025-11 | venue: arXiv preprint
- authors: Qin, Jack et al. | code: none seen
- relevance: LOW-MED — RiskHead distills VLM causal risk estimates into BEV features as risk-attention maps.
- thesis use: VLM-derived risk as a feature/target for the selector.
- verified: abs meta fetched

### Planning in the Backbone: DiffAdapterVLA
- id: arXiv:2609.15322 | date: 2026-09 | venue: arXiv preprint
- authors: Lu, Changxin et al. | code: none seen
- relevance: LOW — adapters inject trajectory tokens into late VLM layers; few trainable parameters, NAVSIM.
- verified: abs meta fetched

### ViLU: Learning Vision-Language Uncertainties for Failure Prediction
- id: arXiv:2507.07620 | date: 2025-07 | venue: ICCV 2025 (per search result; not in abstract record)
- authors: Lafon, Marc et al. | code: https://github.com/ykrmm/ViLU
- relevance: LOW-MED — post-hoc failure predictor on VLM embeddings (visual, predicted text, cross-attention); binary correct/incorrect classifier.
- thesis use: idea for the future calibration phase (embedding-based correctness predictor).
- verified: abs meta fetched

### Perturbation-Based Epistemic Uncertainty for Failure Detection in VLA Models
- id: arXiv:2606.20754 | date: 2026-06 | venue: arXiv preprint
- authors: Lee, Yousung et al. | code: none seen
- relevance: LOW — training-free low-rank weight perturbation; best AUROC on LIBERO-PRO (manipulation).
- thesis use: uncertainty signal for calibration phase.
- verified: abs meta fetched

### Anchors fetched (older, not in known_papers.txt)
- Senna (arXiv:2410.22313, 2024-10, Jiang, Bo et al.): LVLM gives language decisions, E2E model gives trajectories. DriveVLM / DriveVLM-Dual (arXiv:2402.12289, 2024-02, Tian, Xiaoyu et al.). AsyncDriver (arXiv:2406.14556, 2024-06, Chen, Yuan et al.): LLM instruction features guide real-time planner. ORION (arXiv:2503.19755, 2025-03, Fu, Haoyu et al.). VLM-AD (arXiv:2412.14446, 2024-12, Xu, Yi et al.): VLM supervision in training, none at inference. All verified: abs meta fetched; relevance LOW-MED, cite as dual-system / distillation lineage.

## Leads not followed
- "Adaptive Safety Probing for Resource-Efficient VLA Models" (ICML 2026 virtual page https://icml.cc/virtual/2026/75273): per its page, hidden states encode task-relevant 3D intent, lightweight probe as failure monitor, check-then-defend trigger. No arXiv id found. Related: "Your Model Already Knows: Attention-Guided Safety Filter for VLA" arXiv:2606.09749 (not fetched).
- "Triggering Generalist Reasoning via Predictive Uncertainty for Dual-System VLA" (NeurIPS 2026 poster, manipulation): https://neurips.cc/virtual/2026/poster/148902; arXiv id not found.
- LM-X (arXiv:2608.25757), ReconVLA (2604.16677), Hide-and-Seek: VLA failure/uncertainty heads from search snippets only, not fetched.
- CLEAR (cross-attention scorer over candidates, frozen Drive-JEPA plus Qwen 0.8B): search snippet only, id not confirmed.
- Snowballing citations of 2603.06054, BLUE and 2602.10719 via OpenAlex; layer-sweep probing of driving VLMs in OpenReview ICLR 2027 submissions.

---
# Addendum (round 2): full-text checks, lead resolution, snowball, layer/token and "will a visual query help" searches

## Full-text findings for the four priority papers
All quotes are from the arxiv.org/html text of the paper, fetched 2026-11-06. Section labels are the ones the page gave; where I only found a table or appendix I say so.

### 2602.10719 (DualDriveVLA / HybridDriveVLA): details
- Frozen? The VLM encoder is a driving-domain-adapted InternVL3-2B (RecogDrive recipe) and is frozen during imitation learning and RL ("imitation learning on NAVSIM with the VLM backbone frozen and the planner/action head trained; reinforcement learning on NAVSIM with the VLM still frozen", App. A.1). The vision-only encoder is trained jointly.
- Features: "last-layer hidden states" of the VLM, linear adapter to planner width; for analysis the backbone feature is the mean pool of the VLM token sequence (App. A.1.1). App. E reports token-level (non-pooled) analyses give statistics "within" a small margin of the pooled ones (numbers elided in the extracted text).
- What the gate decides (Sec. 6.2): run the ViT branch first and score its trajectory; if the fast-path score passes a threshold, output it, otherwise invoke the VLM branch, build the hybrid candidate set, and apply the scorer. The scorer "encodes the current scene with DINOv2-Small and embeds each candidate trajectory into a query", with trajectory-conditioned heads predicting safety, progress and comfort components supervised by the evaluator (Sec. 6.1). So the gate is conditioned on a candidate trajectory.
- Negative result (Sec. 4.5): "representation-only gating does not reliably outperform the VLM baseline and remains far below the oracle best-of-two"; "reliable selection requires trajectory- and behavior-level signals rather than static representation cues alone". This is direct support for the project's claim that candidate-conditioned selection beats scene-only triggering. (The PDMS values for the best learned gate are elided in the extracted text.)
- Numbers (Sec. 6 / Table 6): InternVL3-2B 90.80; ViT-large 88.88; cross-model oracle best-of-2 93.58; best-of-6 94.00; trajectory mean 91.18; rule-based selection 91.21; adaptive weighting 91.31; scorer (endpoints only) 91.75; HybridDriveVLA 92.10. DualDriveVLA: 91.00 PDMS, VLM invoked in about 15% of scenarios, latency about 280 ms to 150 ms on one A30 (Conclusion).

### 2606.08684 (BLUE): details
- Frozen? Yes: "The visual encoder and LLM backbone remain frozen, while only a lightweight MLP gate is trainable" (Fig. 3 caption). Backbones: SimLingo (InternVL2-1B, App. C.5.1), also CriticVLA, and a NAVSIM check (Table 11).
- Features: "the last-layer hidden state at the final token position" of a prompt-only forward pass including visual tokens and system instructions (Sec. 3 and App. C.5.1). No layer sweep or pooling comparison found. Logistic regression on these states already separates "language helps" frames from the rest (Sec. 3).
- Gate decides: per frame, generate language reasoning then actions, or predict actions directly from the same hidden state. Gate is a single-hidden-layer MLP, 0.11M parameters, dropout 0.5, Adam lr 0.001 (App. C.5.2). Labels come from route-level success comparisons of the two modes, refined at frame level.
- Numbers: 76.2% success on Bench2Drive; 36 DS on Longest6 v2; 2.54x speedup, mean latency 1.40 s to 0.55 s on SimLingo, 4.50x on CriticVLA (Sec. 4, Table 4). The gate is not conditioned on candidate actions.

### 2609.08130 (VLAlert): details and the frozen-backbone answer
- Frozen? Answer: yes for the heads, partly for the VLM. Qwen3-VL-4B: "The visual encoder and original backbone weights are frozen. The language layers are adapted with LoRA" (Sec. on architecture, App. C.2: Stage 1, about 60 GPU-hours). After Stage 1 "the LoRA-adapted VLM is frozen" and hidden states are cached (App. C.3). DangerHead and PolicyHead train on cached features; the VLM is frozen in PolicyHead training (App. C.4). So the earlier UNVERIFIED flag is resolved: LoRA-tuned once, then frozen.
- Features: hidden states are span-pooled between the generated <|BELIEF|> and </|BELIEF|> tokens, concatenating the last four transformer layers, giving a 10,240-dim belief vector per frame; a "decision register" is cached from the closing </|BELIEF|> token (App. C.3, Eq. 5). The features are from generated tokens, so they require a decode pass.
- Pooling ablation (Table 3a, 5-fold linear probe on VLAlert-Bench val): BELIEF range AP 0.459 / AUROC 0.894 / F1 0.442; BELIEF opening token only 0.419 / 0.882 / 0.414; random same-length response span 0.204 / 0.760 / 0.222.
- Gate decides: SILENT, OBSERVE or ALERT per tick. Table 3b (3 seeds): 3-class AP_t 0.184, AUROC_t 0.734, F1_t 0.256; collapsing OBSERVE into SILENT 0.175/0.705/0.255; into ALERT 0.179/0.726/0.254.

### 2603.06054 (probing driving VLMs): details
- Models: abstract says five VLMs with two variants of one (six models in the body): Ovis2.5, InternVL3.5-2B, Qwen3-VL-2B, VST, DriveFusionQA and a variant. Qwen3-VL-2B injects vision-encoder features from layers 6, 12, 18 and 24 into the LLM.
- Frozen: probes are trained on frozen activations. Pooling (Sec. 4.3, Fig. 3): average pooling over all patch vectors, or left/right split average pooling concatenated. Data: CARLA counterfactual images at 5, 10, 20, 30, 40, 50 m.
- Findings (Sec. 1): presence "consistently well encoded from the middle layers of the vision encoder through to the final LLM layer"; orientation "not explicitly encoded ... throughout the entire model across all six models"; distance degrades linear separability. App. D trains an L1-sparse probe on the output logits to see which tokens separate counterfactual inputs.
- Code: github.com/D2ICE-Aut... (truncated in the text; full URL not recovered).

## New papers (verified by absfetch unless stated)

### HALP: Detecting Hallucinations in Vision-Language Models without Generating a Single Token
- id: arXiv:2603.05465 | date: 2026-03 | venue: arXiv preprint
- authors: Kogilathota, Sai Akhil et al. | code: none seen
- relevance: HIGH (method fit) — probes pre-generation hidden states of eight VLMs including Qwen2.5-VL-7B to predict an answer's failure, with abstention and selective routing named as uses. Three token families compared: visual-only features, vision tokens in the decoder, query-token states.
- what: Table 2 AUROC for Qwen2.5-VL-7B: visual-only (VF) 0.7873, vision-token (VT) 0.6683, query-token (QT) 0.9150; averages over models VF 0.6935, VT 0.6852, QT 0.8733. Abstract: "Late query-token states are the most predictive for most models" and the best layer and modality vary by architecture. (Another model's query-token probe peaks at a mid-to-late layer, 0.9365; model name not recovered from the text.)
- thesis use: direct template for "use the frozen VLM's pre-generation hidden state (last query token, mid-to-late layer) to predict whether the VLM will be wrong", i.e. a selector input. Suggests the project's image-token embedding may be the weaker choice (VT lowest on Qwen2.5-VL).
- verified: abs meta fetched, html read

### ProbeAct: Probe-Guided Training-Free Failure Recovery in Vision-Language-Action Models
- id: arXiv:2606.09740 | date: 2026-06 | venue: arXiv preprint
- authors: Zhang, Fan et al. | code: none seen
- relevance: MED — layer by pooling sweep on a frozen OpenVLA-OFT: Table 4 regression score at layer 8 is 0.968 (image-spatial), 0.926 (image-mean), 0.815 (last token), 0.869 (language-mean); layer 12 gives 0.958/0.919/0.856/0.879. "Spatial pooling dominates at every layer"; geometry peaks at shallow-mid layers and decays deeper.
- thesis use: evidence that last-token and mean pooling lose spatial information, and middle layers beat deep ones for geometric facts (object 3D position). Motivates keeping a small spatial grid of image tokens for distance and occlusion cues rather than a single mean vector. Manipulation, not driving, and not a Qwen model.
- verified: abs meta fetched, html read

### The LLM Bottleneck: Why Open-Source Vision LLMs Struggle with Hierarchical Visual Recognition
- id: arXiv:2505.24840 | date: 2025-05 | venue: arXiv preprint
- authors: Tan, Yuwen et al. | code: none seen
- relevance: LOW-MED — only as the Qwen-family pooling data point: on Qwen-2.5VL-7B, "mean pooling consistently outperforms the final-token alternative" over image tokens (from vision encoder output, projector output, and final LLM layer; App. C.2). Pre-window and a taxonomy task.
- thesis use: supports mean-pooled image tokens as the default; contradicts nothing in the project.
- verified: abs meta fetched, html read

### Diagnosing Visual Ignorance in Vision-Language Models
- id: arXiv:2606.06890 | date: 2026-06 | venue: arXiv preprint
- authors: Zhou, Runyu et al. | code: none seen
- relevance: MED — across three VLMs and twelve benchmarks, answer-relevant visual evidence is decodable from intermediate decoder layers but has little effect on the output until the final layers; late states are needed to shift the answer; many predictions survive progressive blur.
- thesis use: explains why a probe on mid layers can beat prompting, and why "VLM says none" is not evidence the VLM lacks the cue.
- verified: abs meta fetched

### Look Where It Matters: High-Resolution Crops Retrieval for Efficient VLMs (AwaRes)
- id: arXiv:2603.16932 | date: 2026-03 | venue: arXiv preprint
- authors: Shabtay, Nimrod et al. | code: https://nimrodshabtay.github.io/AwaRes (project page)
- relevance: HIGH — a VLM decides whether and where to fetch high-resolution crops by tool call, trained with SFT then multi-turn GRPO with a crop-cost penalty. Labels for "needs crop" come from a judge comparing low- vs high-resolution answers. The 80.3% vs 80.46% and 36% pixel figures came from a search summary and are UNVERIFIED (abstract has no numbers).
- thesis use: closest non-driving analogue of learning "will an extra visual query help" from answer-change labels (same idea as expected-gain targets). Not a hidden-state probe; policy learned end to end.
- verified: abs meta fetched

### AdaThinkDrive: Adaptive Thinking via Reinforcement Learning for Autonomous Driving
- id: arXiv:2509.13769 | date: 2025-09 | venue: arXiv preprint
- authors: Luo, Yuechen et al. | code: none seen
- relevance: MED — VLA with fast (no CoT) and slow (CoT) modes, adaptive think reward comparing trajectory quality across modes; NAVSIM PDMS 90.3, beats never-think by 2.0 and always-think by 1.4, inference time down 14% (abstract; baseline for the 14% truncated).
- thesis use: competitor in the "think vs look/no-think" family (same family as DriveAgent-R1); scene-level, not candidate-conditioned.
- verified: abs meta fetched

### CLEAR (arXiv v1 title; v2 retitled Vault): Cognition and Latent Evaluation for Adaptive Routing in End-to-End Autonomous Driving
- id: arXiv:2606.06219 | date: 2026-06 | venue: arXiv preprint
- authors: Xing, Yining et al. | code: none seen
- relevance: MED — v1 fully fine-tunes Qwen 3.5 0.8B on driving QA and uses its hidden states for (a) an Adaptive Scheduler that picks the conditioning coefficient and number of samples from a discrete set (a compute budget per scene) and (b) a cross-attention scorer over candidate trajectories. PDMS 93.7 on NAVSIM v1 (v1 abstract). The earlier "mislabel" in my first report was wrong: the id is right, the record changed between v1 and v2; the absfetch record shows v2 (Vault).
- thesis use: hidden-state-driven budget choice plus candidate scoring; Qwen3.5-family in the loop, though fine-tuned and not frozen.
- verified: abs meta fetched (v2), v1 title and abstract read in html

### Hide-and-Seek in Trajectories: Discovering Failure Signals for VLA Runtime Monitoring
- id: arXiv:2605.30834 | date: 2026-05 | venue: arXiv preprint (ICML 2026 page seen in search)
- authors: Park, Seongheon et al. | code: none seen
- relevance: LOW-MED — coarsely supervised (trajectory-level labels) failure detector for OpenVLA, pi0, pi0.5 on LIBERO and VLABench.
- thesis use: label-efficient monitor idea for the calibration phase.
- verified: abs meta fetched

### SentryVLA: Uncertainty-Guided Action Selection and State Monitoring for VLA Robotic Control
- id: arXiv:2604.16677 | date: 2026-04 | venue: arXiv preprint
- authors: Lyu, Zongyao et al. | code: none seen
- relevance: MED — wrapper for frozen VLA: conformalized quantile regression bounds deviation to rank stochastic candidate actions; a Mahalanobis anomaly score on the latent state before action prediction monitors execution. (The search-summary claim that this is "ReconVLA" was wrong; the record is SentryVLA.)
- thesis use: candidate ranking with conformal bounds plus a latent-state anomaly signal; feeds the future conformal phase.
- verified: abs meta fetched

### LM-X: Explainable Vision-Language-Action Modeling via Progress, Event, and Uncertainty Prediction
- id: arXiv:2608.25757 | date: 2026-08 | venue: arXiv preprint
- authors: Lou, Jin et al. | code: none seen
- relevance: LOW — VLA jointly pretrained with progress, next-event and action-flow variance heads; manipulation. The AUPRC 0.49 to 0.59 and lead-time numbers from a search snippet are UNVERIFIED (not in the abstract text I saw).
- verified: abs meta fetched

### Your Model Already Knows: Attention-Guided Safety Filter for VLA Models
- id: arXiv:2606.09749 | date: 2026-06 | venue: arXiv preprint
- authors: Park, Seongbin et al. | code: none seen
- relevance: LOW — a few attention heads in a VLA localise the object the policy is about to approach; used in a CBF filter. Manipulation.
- verified: abs meta fetched

### HiDe: Rethinking The Zoom-IN method in High Resolution MLLMs via Hierarchical Decoupling
- id: arXiv:2510.00054 | date: 2025-09 | venue: arXiv preprint (ICML 2026 poster page seen in search)
- authors: Liu, Xianjie et al. | code: https://tennine2077.github.io/HiDe.github.io/
- relevance: LOW-MED — argues failure on high-resolution images is background interference, not object size; training-free attention-based region selection; Qwen2.5-VL 7B 92.1% on V*Bench.
- thesis use: relevant to the ROI tool: crop value depends on removing distractors. Uses attention, not a "will it help" predictor.
- verified: abs meta fetched

### CropVLM: Learning to Zoom for Fine-Grained Vision-Language Perception
- id: arXiv:2511.19820 | date: 2025-11 | venue: arXiv preprint (CVPR 2026 workshop per search result)
- authors: Carvalho, Miguel et al. | code: none seen
- relevance: LOW — separate RL-trained cropper paired with any VLM; no decision about whether to crop.
- verified: abs meta fetched

### Reinforcing VLMs to Use Tools for Detailed Visual Reasoning Under Resource Constraints
- id: arXiv:2506.14821 | date: 2025-06 | venue: arXiv preprint
- authors: Kumar, Sunil et al. | code: none seen
- relevance: LOW — GRPO trains small VLMs to use zoom as a tool. Pre-window.
- verified: abs meta fetched

## Leads resolved or dropped
- "Adaptive Safety Probing for Resource-Efficient VLA Models" (ICML 2026, https://icml.cc/virtual/2026/75273): no arXiv id found in two searches; DROPPED as a paper entry (page only, unverified).
- TUD "Triggering Generalist Reasoning via Predictive Uncertainty for Dual-System VLA": NeurIPS 2026 poster page https://neurips.cc/virtual/2026/poster/148902 and a deeplearn.org listing; no arXiv id found. Signal per listing: cross-step dispersion of action re-predictions from cached generalist context; manipulation (VLA-Arena). Reported as UNVERIFIED, not a full entry.
- CLEAR, LM-X, SentryVLA (the snippet "ReconVLA"), Hide-and-Seek: verified above. AdaDiff-VLA (cited DriveVLM in OpenAlex, DOI 10.1007/978-3-032-38410-2_11): no arXiv record found, DROPPED.
- "Improving Proactive Risk-Awareness of Autonomous Driving via Trajectory Monitoring" (ICPR 2026, researchr.org/publication/ZhaoLPY26): bibliographic listing only, no abstract; UNVERIFIED, not read.

## OpenAlex cited-by snowball
- 2602.10719, 2606.08684 and 2603.06054 each had 0 citing works in OpenAlex (too new). Nothing to add from them.
- DriveVLM (W4391988276, 114 citing works): scanned the 50 most recent. Relevant titles to look at (none fetched on arXiv, no arXiv ids in OpenAlex): AdaDiff-VLA (hybrid reasoning mode policy, dropped above), "Teaching Vision-Language-Action Models What to See and Where to Look" (Springer chapter 2026, DOI 10.1007/978-3-032-37356-4_18), "CritiqueDriveVLM ... Latent Thought Distillation" (10.1007/978-3-032-37010-5_34), "Enhancing Trajectory Planning with VLA Models and Perception Guidance" (10.3103/s1060992x26603854). These are listed as leads only; not verified.

## Layer/token findings (item 4) in one place
- Qwen-family evidence: Qwen2.5-VL-7B image tokens: mean pooling beats final-token (2505.24840); hallucination probes: query-token 0.9150 vs vision-token 0.6683 vs visual-only 0.7873 AUROC (2603.05465); Qwen3-VL-8B occlusion information lost at the visual-token merger (2605.20448, from round 1). Qwen3-VL-4B span-pooled last-four-layer concatenation gives AP 0.459 vs 0.204 for a random span (2609.08130).
- Last-token states from the last layer are what BLUE uses; no paper I found sweeps layers for BLUE-style gates. ProbeAct shows image-spatial pooling at layer 8 beats mean and last token (0.968 vs 0.926 vs 0.815) on OpenVLA-OFT.
- A VLM-hidden-state predictor of "will an extra visual query help" in the zoom/crop/tool sense: not found. Nearest: AwaRes (labels from low- vs high-resolution answer change, policy learned end to end), HALP (pre-generation correctness probe), BLUE (benefit-of-language gate). This is a gap the project can claim, with the caveat that my search was limited to the queries above.

## Updated Summary (supersedes the first Summary where they differ)
- Still no paper that picks among perception tools conditioned on a candidate set using VLM features. The nearest design is DualDriveVLA (2602.10719): its gate scores the fast-path trajectory with a trajectory-conditioned scorer (DINOv2-Small scene encoding plus a trajectory query) before deciding to call the VLM. Its own negative result says representation-only gating "does not reliably outperform the VLM baseline" and "reliable selection requires trajectory- and behavior-level signals". That supports the project's central claim, and is the most useful citation found.
- BLUE (2606.08684) and VLAlert (2609.08130) show frozen-backbone hidden states can predict benefit of an extra step. BLUE: last layer, final prompt token, 0.11M MLP, scene complexity and kinematics alone weak. VLAlert: LoRA-tuned once then frozen, last four layers span-pooled over a generated belief span; 0.459 AP vs 0.204 for a random span. Neither conditions on candidate actions, and both read states from a tuned or generating model, unlike the project's cached image embeddings from a frozen Qwen3.5-9B.
- For the embedding choice: HALP shows on Qwen2.5-VL-7B that query-token states (0.9150 AUROC) beat vision-token states (0.6683) and visual-only features (0.7873) for predicting VLM failure before generation. The project's cached image embeddings are closest to the weaker families; an experiment with the last prompt-token state at mid-to-late layers is worth running. ProbeAct supports keeping a small spatial grid of image tokens rather than one mean vector when the target is geometric.
- Probing and "VLMs know more than they say": 2603.06054 (driving; presence encoded, orientation not, distance degrades), 2601.03464 (probe vs prompt on time series), 2606.06890 (decodable at mid layers, effective only late), 2606.31257 and 2605.30557 (decodable is not grounded; VLMs do not notice missing evidence). Add a blank-image control to any embedding-gain claim.
- The tool-use side: AwaRes (2603.16932) learns whether to crop from low- vs high-resolution answer-change labels, which is the same idea as the expected-gain targets, in a non-driving setting. AdaThinkDrive (2509.13769) and ASSCG (2606.25509) are scene-level think/slow-system gates.
- Dual-system caching: Think at 5 Hz (2607.15621) exposes a frozen 7B backbone's per-layer KV cache and trains under random staleness. Distillation (VERDI, Orion-Lite) is the alternative to test-time features.
- Candidate-set VLM scorers (Slow Brain Fast Planner, SimpleVSF, MindDrive, CLEAR's cross-attention scorer) are ranker baselines, not query selectors. CLEAR also uses LLM hidden states to choose a per-scene sample count (a budget decision).
- Limits of this scan: abstracts and selected full texts only; three OpenAlex cited-by lists were empty; several papers (TUD, ICML safety probing) have no arXiv id and were not read.
