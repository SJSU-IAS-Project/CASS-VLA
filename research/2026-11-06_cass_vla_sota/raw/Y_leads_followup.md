# Y_leads_followup: UNVERIFIED items and leads, followed up

Started 2026-11-06 ~23:00 PST. Rows are appended as checks finish. OpenReview checks used the public search API (the `notes?id=` endpoint is behind a bot challenge); its records carry cdate, number and venue but no authors for ICLR 2027 submissions.

## Summary
- UNVERIFIED sweep: about 50 flagged or implicit-unverified items checked. Nearly all claims held. Corrections that matter: ICLR 2027 OpenReview items now have dates (all 2026-08 to 2026-09); StreamSelect was withdrawn from ICLR 2027; DiVeR default N is 16; DriveReferee draws exactly 1 extra candidate (K=2) after an alarm; the 35% decision-uncertainty figure in Bhatt et al. is the simulated-data number (real driving scenes: 10%); HazardForge builds its images from 200 DriveBench and 200 SA-Bench inputs; RIV-CoT's EACL 2026 Findings title is "DRIVINGVQA: A Dataset for Interleaved Visual Chain-of-Thought in Real-World Driving Scenarios".
- Anchor facts now verified from primary pages: DriveAgent-R1 is an ICLR 2026 poster (OpenReview r2g8TV4nJy); its latency numbers (8.50 / 7.91 / 6.74 s) are in the paper; its README releases training code only, while evaluation scripts, data and weights are "pending company approval", and 2609.08217 states a faithful comparison is not possible. Plan to re-implement its trigger, not to run it.
- Venue upgrades: Value of Information for human-agent communication is an ACL 2026 main-conference paper; AdaTooler-V is Findings of ACL 2026; AutoTool is an ICML 2026 poster; Illusion of Visual Tool-Use is EMNLP 2026 Findings; WOD-E2E, ActiveVLA, CF-VLA and ELF-VLA are CVPR 2026; DriveSuprim and ScenGE are AAAI 2026; AgentThink is Findings of EMNLP 2025 per its arXiv journal-ref (typo "Fundings").
- Still unverified: SafeVL venue (project page numbers 76% Nexar and 8% NeuroNCAP are confirmed, authors anonymous, no arXiv id), Context-Aware CP arXiv id (workshop and authors now known: ICML 2026 Efficient Multimodal QA workshop, Yang-Jun Joo et al.), a handful of LOW-relevance "per search summary" numbers.
- Closest conceptual overlaps found in the leads sweep, all outside driving: Best-of-Evidence (budget over evidence actions that can change the choice among a fixed candidate pool), Calibrate-Then-Delegate (regress the gain of the costlier option, not uncertainty), Support Before Sign (deferral gain = disagreement support x signed margin). None conditions a perception tool on candidate trajectories. No driving paper doing so turned up in 20+ ICLR 2027 queries.
- Useful method notes: UPS builds its conformal set over K sampled action options scored by a VLM verifier (set size picks execute / clarify / intervene); ASSCG's gate has no candidate input but states the VoI rule in driving; Bench2Drive-Robust gives a severity-table precedent (two levels per noise type, three delay levels).
- Evaluation caveats: open-loop scores track closed-loop driving only loosely (2605.00066, n=8, rho 0.90 for PDMS but ranking inversions; BridgeSim names the OL-CL gap). DriveReward shows oracle best-of-N headroom 3.0% against 0.22% for a learned reward model, a reminder that oracle ceilings are far above what learned scorers reach.

## Part 1. UNVERIFIED table

| file | paper | what was unverified | my check (source fetched) | result |
|---|---|---|---|---|
| A | DriveAgent-R1 (2507.20879) | latency 7.91 s vs 6.74 s | arxiv.org/html/2507.20879, Table 8 text: "from 7.91s to 6.74s", tokens 314.45 to 265.57, Passive-SV 8.50 s | CONFIRMED (A already resolved it in its own file) |
| A | RIV-CoT / DrivingVQA (2501.04671) | EACL 2026 Findings venue | aclanthology.org/2026.findings-eacl.173 fetched: exists, same five authors | CONFIRMED, but CORRECTED title: the Findings version is titled "DRIVINGVQA: A Dataset for Interleaved Visual Chain-of-Thought in Real-World Driving Scenarios"; "Retrieval-Based Interleaved..." is the arXiv title |
| B | MosaicDrive (OR 9I96DzTfHb) | date | OpenReview search record: cdate 2026-09-16, submission #24529 | CORRECTED to 2026-09 (ICLR 2027 submission, under review) |
| B | DEEP / Decision Value of Perception Compute (OR l9QJO8BIoE) | date | OR record: cdate 2026-09-14, #16850 | CORRECTED to 2026-09 |
| B | ETM (OR oa4EWvJlLC) | date | OR record: cdate 2026-09-15, #20915 | CORRECTED to 2026-09 |
| B | DriveScout (OR rXDM54aQdX) | date | OR record: cdate 2026-09-14, #17757 | CORRECTED to 2026-09 |
| B | StreamSelect (OR KQwcH95tnN) | date, status | OR record: cdate 2026-08-31, #7030, venue string "ICLR 2027 Conference Withdrawn Submission" | CORRECTED: 2026-08, and the submission was WITHDRAWN (the arXiv copy B read still stands) |
| B | Certifying the Information Value of Adaptive Tool Use (OR JUWtWs4Tgb) | date | OR record: cdate 2026-09-19, #57996 | CORRECTED to 2026-09 |
| B | ProActiveDrive (OR Y6Pvaxv729) | date | OR record: cdate 2026-09-10, #13140 | CORRECTED to 2026-09 |
| B | VarioDrive (OR nxKu7c8r73) | date | OR record: cdate 2026-09-18, #39133 | CORRECTED to 2026-09 |
| B | MindDrive map-informed (OR EHiH6oQNZ8) | date | OR record: cdate 2026-09-18, #37391 | CORRECTED to 2026-09 |
| B | Scene-Adaptive Readout and Decoding (OR 3CHvYAsfDh) | date | OR record: cdate 2026-09-10, #12896 | CORRECTED to 2026-09 |
| B | AdaThinkDrive (2509.13769) | 96% CoT in hard / 84% direct in simple scenarios | arxiv.org/html/2509.13769 text: "selectively employing CoT in 96% of challenging scenarios, while defaulting to direct trajectory prediction in 84% of simple scenarios"; also "reduces inference time by 14% compared to an always-think baseline" | CONFIRMED (in the paper intro; B was right that it is not a PDMS figure) |
| B | AgentThink (2505.15298) | venue | arXiv abs page journal-ref field: "EMNLP2025 Fundings" (author typo for Findings) | CONFIRMED as Findings of EMNLP 2025 per the authors' journal-ref field only; not checked on aclanthology |
| B | Safe Occlusion-aware Driving via Game-Theoretic Active Perception (2105.08169) | venue | arXiv abs page DOI 10.15607/RSS.2021.XVII.066 | CONFIRMED: RSS 2021 |
| G | Explore until Confident (2403.15941) | RSS 2024 | OpenAlex: DOI 10.15607/rss.2024.xx.089, source Robotics: Science and Systems, 2024 | CONFIRMED |
| C | DriveReward (2606.08525) | test-time selection gain 0.22%, "UNVERIFIED in text" | arxiv.org/html/2606.08525: "the Best-of-N oracle outperforms the vanilla baseline by 3.0%. Our DriveReward model ... delivering a 0.22% improvement over the baseline. Admittedly, the performance gain ... is relatively marginal" | CONFIRMED. Useful for us: oracle headroom 3.0 vs learned scorer 0.22 |
| C | AutoVLA (2506.13757) | column header of 92.12 / 89.11 / 80.54 | html Table 1 caption "Testing Results on the NAVSIM ... Benchmark", column "PDMS" first; rows AutoVLA One-shot 80.54, Post-RFT 89.11, Best-of-N 92.12; text: "oracle scorer to select the optimal trajectory from six generated candidates" | CONFIRMED: first column is PDMS (hence oracle best-of-6 = +3.01 PDMS over Post-RFT) |
| C | SafeVL (no arXiv id) | 76% Nexar, 8% NeuroNCAP collision reduction, venue | safevl.github.io fetched verbatim: "76% accuracy in the zero-shot setting, representing a 20% improvement"; "integrate SafeVL into ... UniAD as a planning trajectory filter, reducing closed-loop collision rates by 8% on the NeuroNCAP benchmark". BibTeX there is `@inproceedings{vpd_lm_neurips2025 ... author = Anonymous` | numbers CONFIRMED (project page, not a paper); venue STILL UNVERIFIED (BibTeX key suggests a NeurIPS 2025 submission, authors anonymous); no arXiv id found |
| C | DiVeR (2610.04933) | default candidate count N | html (math alttext kept): "We use N=16 as the default inference setting"; results at N=32 pi0: +5.8% over N=1 | CORRECTED: default N = 16 |
| C | DriveReferee (2609.22762) | number of extra candidates | html: "the policy draws K-1 additional candidates"; "We use Delta=0.4 m ... and K=2"; referee median 30 ms per candidate on CPU | CORRECTED: K=2, i.e. 1 extra candidate, only after an alarm |
| E | BeyondSight (2607.09138) | detection of unobservable actors 0 to 0.249, metric | html: "increasing detection performance for unobservable actors from 0 to 0.249 mAP" (mAP_unobs, SparseDrive 0 vs BeyondSight 0.249); planning L2avg 0.61 to 0.54 on nuScenes | CONFIRMED: metric is mAP_unobs on the new nuScenes-Permanence benchmark |
| E | Know Where You're Uncertain (2411.01639) | 35% decision-uncertainty reduction | html: "On the simulated data, we observe a 35% reduction in decision uncertainty. Across ... 50 driving scenes ... active sensing reduces perception uncertainty by over 10% and subsequently reduces decision uncertainty by 10%". Abstract: variability down by up to 40%, task success up 5% | CONFIRMED with qualifier: 35% is the simulated-data figure; real driving scenes give 10% |
| E | HazardForge / MovSafeBench (2601.08470) | "built on DriveBench and SA-Bench"; four scenario types | html: "We select DriveBench for scenes of autonomous driving and SA-Bench for scenes of mobile robots to be transformed using HazardForge. We use 200 images from DriveBench and 200 images from SA-Bench"; scenarios: moving hazard (motion), off-screen intrusion into ego lane, far-field hazard object, plus default static | CONFIRMED: 400 source images, four scenarios motion / intrusion / distance / static. Largest accuracy drop is in motion questions. Note it is MCQ over edited images, not driving decisions |
| E | ESI-Bench (2605.18746) | step budget sweep 5 to 50 | html: "Gemini 3.1 Active with step budgets from 5 to 50 ... in intervals of 5 steps ... improves rapidly from 5 to 15 steps, begins to saturate around 15-20 steps, nearly flat after 30 ... beyond 40 slightly decreases" | CONFIRMED. Nice precedent for a saturating accuracy-vs-budget curve |
| F | ASSCG (2606.25509) | not candidate-conditioned beyond abstract | html Sec. 4.4: gate input is [Pool(x_t), cosine similarity to the buffered slow embedding, log time since last query]; no candidate input. Sec. 3 frames the problem as value of information: "query ... only when the expected improvement in J exceeds the query cost and the risk of FI". It also says planner confidence among shortlisted candidates is "less discriminative" in its setting | CONFIRMED not candidate-conditioned. Worth citing as an explicit VoI framing in driving |
| F | AwaRes (2603.16932) | 80.3% vs 80.46%, 36% tokens | html abstract: "matches full-resolution accuracy while retaining only 36% of visual tokens"; intro: "(80.3% vs. 80.46%)"; Table row Qwen2.5-VL-7B 80.46 at RTR 1.00; also "latency reduction over reasoning-based methods ... 4.4x reduction over the resolution-escalation method" | CONFIRMED (36% of tokens is in the abstract; B/F said abstract had no numbers) |
| F | LM-X (2608.25757) | AUPRC 0.49 to 0.59, lead time | html intro: "raises action-error AUPRC from 0.49 to 0.59; extends mean failure-warning lead time from 0.93 to 1.54 seconds"; RTG Spearman 0.71 to 0.91 | CONFIRMED |
| G | Context-Aware CP (ICML 2026 workshop) | workshop, authors | icml.cc/virtual/2026/80373 fetched: "Poster in Workshop: Efficient Multimodal Question Answering"; authors Yang-Jun Joo, Younggun Kim, Sung-Yeon Park, Mohamed Abdel-Aty; 16,655 WaymoQA pairs, six VLMs. Still no arXiv id | CONFIRMED / filled in: workshop and authors known; arXiv id STILL UNVERIFIED (none found) |
| G | OCP, IROS 2025 (DOI 10.1109/iros60139.2025.11245999) | first author, content | OpenAlex: authors Jiayi Chen, Shuai Wang, Guoliang Li, Wei Xu, Guangxu Zhu, Derrick Wing Kwan Ng, Chengzhong Xu; 2025-10-19; abstract: "the key challenge is deciding when and how to engage the large model"; collaboration timing optimization = detection-confidence thresholding + cloud forward simulation; outperforms on navigation time and success rate (no numbers in abstract) | CONFIRMED first author Jiayi Chen; content now read from the abstract. It is a scene/confidence-threshold trigger (same family as DriveAgent-R1), not candidate-conditioned |
| M4 | Co-GLANCE (2606.09919) | rest of abstract | abs page fetched in full: outperforms cloud VLM baselines in occlusion segmentation and robot allocation accuracy by 25% and 36%, per-frame latency cut 350x; releases an air-ground dataset | CONFIRMED / completed |
| X2 | "When to Ask for Help" (2610.21160) | success numbers for the router | html abstract: "synthetic testbed with matched budgets it Pareto-dominates all three baseline families (0.825 +/- 0.002 vs. 0.762 +/- 0.002 success at a 0.25 query rate)"; advantage vanishes under homogeneous collapse | CONFIRMED: 0.825 vs 0.762 success at 0.25 query rate (synthetic testbed only) |
| B | Beyond Tool-Call Count (NeurIPS 2026 workshops) | venue status, 14.7% | neurips.cc/virtual/2026/poster/170712 and /173045 fetched: two workshop posters ("Workshop on Resource-Aware Agentic AI"; "Who Verifies the Agents?"), authors Zhichang Chen, Autumn Mapes, Jialin Yu, Josefa Stoisser, Marc Boubnovski Martell; abstract: "improves the accuracy-cost Pareto frontier over Probe & Prefill by 14.7% in hypervolume" on When2Tool | CONFIRMED: workshop posters, not main track; still no arXiv id |
| F | VLAlert (2609.08130) frozen backbone | already resolved by F | F's own text quotes the paper (LoRA once, then frozen) | not re-checked (resolved in-file) |
| A | DriveAgent-R1 (2507.20879) | venue ICLR 2026 "per search results" | OpenReview search record r2g8TV4nJy, group ICLR.cc/2026/Conference, venue string "ICLR 2026 Poster", cdate 2025-09-18. The OpenReview title orders the words differently: "...with Active Perception and Hybrid Thinking" (arXiv v1: "Hybrid Thinking and Active Perception") | CONFIRMED: ICLR 2026 poster |
| D | AutoTool (2605.19852) | ICML 2026 "from a search listing only" | icml.cc/virtual/2026/poster/66174 fetched: ICML 2026 poster | CONFIRMED |
| D | AdaTooler-V (2512.16918) | ACL Findings 2026 "from a search listing" | aclanthology.org/2026.findings-acl.898 fetched: "Findings of the Association for Computational Linguistics: ACL 2026", pages 18058-18072 | CONFIRMED |
| B | Value of Information: Human-Agent Communication (2601.06407) | ACL 2026 "per search result listing" | aclanthology.org/2026.acl-long.1987 fetched: Proceedings of the 64th Annual Meeting of the ACL, Volume 1 Long Papers | CONFIRMED, and stronger than recorded: main-conference long paper, not Findings |
| D | Illusion of Visual Tool-Use (2608.06270) | EMNLP 2026 Findings "from a search listing" | 2026.emnlp.org/program/find_papers fetched: title and authors Zhiheng Wang, Bo Peng, Lai Wei, Chaochao Lu are on the accepted Findings list | CONFIRMED |
| D | ActiveVLA (2601.08325) | CVPR 2026 "from a search listing" | openaccess.thecvf.com CVPR2026 html page fetched: authors Zhenyang Liu, Yongchong Gu, Yikai Wang, Xiangyang Xue, Yanwei Fu; Proceedings of CVPR | CONFIRMED |
| E | WOD-E2E (2510.26125) | CVPR 2026 (appears as "Rare-E2E" on the poster page) | openaccess.thecvf.com CVPR2026 html page fetched, authors incl. Ben Sapp, Mingxing Tan, Jyh-Jing Hwang, Dragomir Anguelov; Proceedings of CVPR | CONFIRMED as CVPR 2026 (open access title is WOD-E2E; "Rare-E2E" is only the poster-page label) |
| C | DriveSuprim (2506.06659) | AAAI 2026 "per search result" | ojs.aaai.org/index.php/AAAI/article/view/38178 meta: Proceedings of the AAAI Conference on AI, vol. 40, first page 11910 | CONFIRMED |
| E | ScenGE (2508.14527) | AAAI 2026 "per search result" | ojs.aaai.org citation endpoint (submission 41238): Liu, J. et al. (2026), AAAI 40(45), 38926-38934, doi 10.1609/aaai.v40i45.41238 | CONFIRMED |
| A | Counterfactual VLA (2512.24426) and ELF-VLA (2603.01063) | CVPR 2026 "per search results" | openaccess.thecvf.com/content/CVPR2026/papers/ files exist (HTTP 200, PDF) for "Peng_Counterfactual_VLA..." and "Luo_Unleashing_VLA_Potentials_in_Autonomous_Driving_via_Explicit_Learning_from_..."; the arXiv title of 2603.01063 is exactly "Unleashing VLA Potentials in Autonomous Driving via Explicit Learning from Failures" (so "ELF-VLA" is the method name) | CONFIRMED (PDF existence plus title match; author list not read) |
| D | KnowNo (2307.01928) | CoRL 2023 | proceedings.mlr.press/v229/ren23a.html meta: Conference on Robot Learning | CONFIRMED |
| F | Layer by Layer (2502.02013) | ICML 2025 | proceedings.mlr.press/v267/skean25a.html: International Conference on Machine Learning | CONFIRMED |
| F | ViLU (2507.07620) | ICCV 2025 | openaccess.thecvf.com ICCV2025 page meta: Proceedings of the IEEE/CVF ICCV | CONFIRMED |
| D | MeCo (2502.12961) | ACL 2025 | OpenAlex source: "Proceedings of the conference - Association for Computational Linguistics. Meeting" 2025 | CONFIRMED only as an ACL-family 2025 proceedings entry (main vs Findings not resolved) |
| B | Active Information Gathering for Long-Horizon Navigation (2403.03269) | IROS 2024 | OpenAlex source: IEEE/RSJ IROS, 2024 | CONFIRMED |

Not re-checked, still carrying the earlier agent's "per search" label: CropVLM (CVPR 2026 workshop), EnDfuser (PMLR v307), KITScenes, BCOD numbers (B:100-104), MVPruner/SToRM efficiency numbers (B:213), HybridDriveVLA / DualDriveVLA numbers (B:133), traffic-light weak point claim for the 16,185-QA benchmark (E:119). All LOW relevance except none. Treat them as STILL UNVERIFIED.

## Part 2. Leads followed

Leads that other agents had already resolved were skipped: DEEP / MosaicDrive / ETM / DriveScout (X1 did the deep read), BeyondSight, UPS, CORA, ToolChain-CRC (D), CTD, LNE and PoP entries (M4 has blocks), 2610.02765 and 2608.26533 (G has blocks), the BCEA line, 2609.34440 and 2610.21741 (L4 addendum has them).

### Lead 1. CTD (2604.14251) and LNE (2605.00737): how the benefit target is built (M4 lead, "check how the delegation value or need target is built")
- CTD, html read: delegation value DV(x,y) = P_expert(y|x) - P_probe(y|x), the margin in the probability of the true label. A "DV probe" regresses it with squared loss on continuous targets from the same latent features as the safety probe (Llama-3.2-1B activations; strong expert Gemma-3-27B-IT; weak expert is the probe's own model). The threshold on predicted DV is calibrated on held-out data by multiple hypothesis testing for a guarantee on delegation rate or on safety performance.
- This is the same recipe as our expected-gain target (gain of the costlier option over the cheap one, regressed from features), with a conformal-style calibrated threshold on top. The CTD authors state the motivation directly: "uncertainty is a poor proxy for the utility of an expert call, as it ignores whether the expert would actually improve the prediction". No candidate-set input; the input is one latent vector.
- LNE (abstract): trained from hidden states to predict true need; "LNEs generally predict true need more accurately than model self-reports and improve budgeted tool allocation". Code: github.com/QinyuanWu0710/ToCall_or_NotToCall (named in the abstract).
- Thesis use: cite both as direct precedent for expected-gain targets over uncertainty, and CTD's threshold calibration as the route for the later conformal phase.

### Lead 2. DriveReferee (2609.22762): alarm-triggered extra candidates (C lead on the unknown extra-candidate count)
- Resolved above: K=2, one extra candidate drawn only after the clearance alarm, referee 30 ms per candidate on CPU. This is a selective-sampling trigger conditioned on the default plan's own clearance, i.e. plan-conditioned (not scene-uncertainty) triggering, but it decides whether to sample another plan, not which perception query to make. Worth citing as the nearest plan-conditioned trigger in driving.

### Lead 3. DriveAgent-R1 code and reproducibility (A wrote "code: none seen"; B/A lead on its cited-by)
- Project page tsinghua-mars-lab.github.io/DriveAgent-R1 links github.com/Zwc2003/DriveAgent-R1. README (raw.githubusercontent.com .../main/README.md, fetched): "Accepted to ICLR 2026". Released: training code for SFT and cascaded RL with the multi-round tool-calling framework. NOT yet released (README checklist, unticked): evaluation scripts, the Drive-Internal dataset and nuScenes test split with meta-action labels ("pending company approval"), and trained model weights ("pending company approval").
- 2609.08217 (Drive by Hindsight and Foresight), html Sec. on baselines: "DriveAgent-R1 is the closest concurrent method in active perception. However, its checkpoints and evaluation assets have not been fully released, preventing a faithful comparison under the same protocol."
- Consequence for the thesis: DriveAgent-R1 cannot be run as a baseline off the shelf. Reproduce its trigger idea (scene-complexity gating of one tool call) in MetaDrive rather than its weights. The README also confirms that its output is a high-level meta-action, not a candidate set.
- OpenAlex cited-by for DriveAgent-R1 (W7077045906, 4 works): a survey (3 versions on TechRxiv) and PixelPilot. Nothing new. Cited-by for Active Probing (2507.09822, W4416748933, 2 works): two planner papers, nothing on information gathering.

### Lead 4. UPS (2602.22474): how the candidate set and conformal set are built (D lead)
- html read. K action samples are drawn from a frozen base policy; a VLM verifier gives a probability per option. Multi-option nonconformity score s(x, Y*) = 1 - min over correct options of P_VLM(y|x); sequence level kappa = max over query points; threshold q-hat = the ceil((N+1)(1-eps))/N empirical quantile of calibration scores; prediction set C(x) = all options with 1 - p(y|x) <= q-hat. Set size then selects execute (singleton), clarify (several plausible options) or intervene (policy cannot do the task). Residual policy learned from interventions, then the verifier is recalibrated.
- So the "candidates" are policy samples scored by a verifier, and conformal set size decides the action. It is candidate-conditioned in the sense that the set is over candidates, but the decision is execute/ask/intervene, not which perception tool. Manipulation only. Fits the later accept/inspect/replan/fallback phase.

### Lead 5. Was there an arXiv version of the OpenReview-only competitors? (H and X1 lead)
- DEEP / Decision Value of Perception Compute: YES, arXiv:2609.35910 (Cong, Hoang Pham et al., 2026-09-28, abs fetched). X1 and B already carry it; the "no arXiv found" note in H is out of date. Abstract adds: 34-54% of escalations that change loss make it worse; PDM-Closed open-loop on nuPlan shows harmful escalations too; learned allocators "select nearly as much harm as random"; at a 20% latency budget only routers at about 3.5% of a detector pass beat random.
- MosaicDrive, ETM, DriveScout: two web searches by exact title found no arXiv or other page. Still OpenReview-only (cdate 2026-09; see table).
- StreamSelect was withdrawn from ICLR 2027 (OpenReview venue string), so cite its arXiv version, not an ICLR submission.

### Lead 6. ICLR 2027 OpenReview queries that earlier agents did not run (B, C, H leads)
Queries run (search API, 5 s apart): traffic light state tool driving; conformal deferral driving; occupancy query budget driving; trajectory verifier best-of-N driving; active perception driving planner; value of information driving perception; decision-relevant query candidate actions; which sensor to query planning budget; tool selection embodied occlusion budget; abstain driving VLA uncertainty; selective verification candidate plans; perception on demand robot policy; driving agent zoom crop tool RL; when to think driving VLA; occluded hazard driving benchmark VLM; conformal risk control driving planner fallback; expected gain label tool selector router embodied.
- No new driving submission that picks a perception tool conditioned on candidate trajectories. The closest new items are non-driving and listed as paper blocks below (Best-of-Evidence, Support Before Sign, BCRC, StopTheDream, AEWM).
- Driving titles seen, judged from title/abstract only, LOW: TrajWAM (8v37ZgaCMW, trajectory-conditioned BEV world model; Bench2Drive DS 91.53), More Camera Frames, Better Driving? (clDpaFHaep, within-scene frame-rate scaling), TRACE traffic regulation agent (LygwzyXEoj, evidence acquisition with tools for compliance checking, 96.67% strict accuracy on 751 cases), KnUT OoD benchmark (X06N9Uuw7m), ASR-VLA (manipulation safety, not driving), HiDrive / PlanContext / STRIDE / UBD-Bench (benchmarks, not read).

### Lead 7. Bench2Drive-Robust (2605.18059) and Safe2Drive (2606.00191): scenario and severity definitions (M7 lead)
- Bench2Drive-Robust Table 2 (html): burst frame drop k in {1, 3} s; partial observation mask ratio r in {0.5, 0.8}; GPS noise sigma in {5, 15} m; speed noise N(mu, 0.2^2) with mu in {0.2, 0.5}; inference delay in {100, 200, 500} ms. "Each perturbation type is evaluated at representative severity levels chosen to cover moderate and severe." Two severities per input perturbation and three delay levels: a precedent for our three tool-noise levels.
- Safe2Drive: 100 scenarios, three families (work zones, pedestrian jaywalking, occluded vulnerable road users), SafeDriving Score; LEAD 94.70 DS on Bench2Drive to 39.95; SimLingo 85.07 to 41.00; SDS 11.85 / 15.27. Numbers from the abstract and Sec. 4 text reconfirmed. Closed-loop CARLA, so not usable as-is for MetaDrive, but the occluded-VRU family is the definition to mirror.

### Lead 8. Open-loop evaluation validity (M6 lead: BridgeSim, What Matters..., plus a paper found while checking)
Written as paper blocks below (2605.00066, 2604.10856). 2603.15185 (BevAD) is closed-loop architecture work: Bench2Drive success rate 72.7% with pure imitation; not needed for our question.

## Part 3. Papers (not in any other raw/*.md as of this check; most relevant first)

### Best-of-Evidence: Best-of-N Selection under Partial Verification
- id: OpenReview U1JptdfbDT (ICLR 2027 submission, OpenReview cdate 2026-08-20) | date: 2026-08 | venue: ICLR 2027 submission
- authors: not shown in the search record | code: none seen
- relevance: MED-HIGH (as a concept; medical VQA, not driving) — fixes a pool of N candidate answers and spends a limited budget on "evidence actions that can change the final choice". That is candidate-conditioned query selection under a budget, with the zero-budget case recovering plain Best-of-N.
- what: Represents reusable claims with a signed candidate-factor graph, uses a score-based controller to pick which factor to verify, and proves a O(log K) versus Theta(K) query separation for shared factor queries in a factor-code model. Experiments on four medical VQA settings: improves fixed-pool selection and rescues some Best-of-N failures "when evidence is reliable, contrastive, and decision-relevant", with channel-quality and candidate-generation limits that prevent universal gains (abstract; no numbers in it).
- thesis use: closest conceptual match found outside driving to "which query changes the choice among K candidates". Cite as related work for the candidate-conditioned framing; its "decision-relevant evidence" criterion is the same idea as our oracle gain. Not a driving competitor.
- verified: OpenReview search record (abstract) read; no arXiv version found; not read in full.

### Support Before Sign: Identifying Deferral Gain in LLM Cascades
- id: OpenReview NJsRndgACN (ICLR 2027 submission) | date: 2026-09 | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: MED — signed deferral gain (does replacing the small model's answer improve the outcome?) factorizes into disagreement support and a signed margin; routes on their product. Same logic as an expected-gain label for calling a costlier option.
- what: Under answer-factored grading, gain = P(disagree) x E[benefit | disagree]. Support is identifiable from unlabeled paired outputs; the signed margin needs labeled disagreements. Evaluated as integrated accuracy over call rate on a fixed model pair; benefit "depends on the mixture" and direct estimators win at some low-deferral points (abstract; no numbers).
- thesis use: idea to borrow: decompose the expected-gain target into "would the tool change the ranker's choice" (support) times "is the changed choice better" (sign). In our setup the first factor can be computed without labels from the ranker with and without the tool. Evaluation as accuracy vs call rate matches our Pareto curve.
- verified: OpenReview search record (abstract) read.

### Budget-First Conformal Robustness Control under Hard Deployment Budgets (BCRC)
- id: OpenReview 12NxQTIgFU (ICLR 2027 submission) | date: 2026-09 | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: MED — for the future calibration phase: builds the maximal budget-feasible set of decisions for each input from a hard per-decision cost or set-size budget, then certifies the failure probability of the deployed rule on an independent certification set.
- what: Inverts the usual risk-first order of conformal risk control: start from the budget, construct the feasible candidate set, then bound failure. Reports (abstract) that it "consistently satisfies the deployment budget and achieves lower failure risk than several baseline methods under the same budget"; no numbers, not driving.
- thesis use: template for putting a conformal guarantee on a selector that must respect a query budget.
- verified: OpenReview search record (abstract) read.

### How Much Best-of-N Regret Can Reranking a Shortlist Recover?
- id: OpenReview bi0W5GwrZq (ICLR 2027 submission) | date: 2026-09 | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: LOW-MED — decomposes regret against the gold-best candidate and bounds the oracle ceiling for reranking a proxy-score shortlist, then allocates exact-verification calls to runner-up candidates.
- what: At N=64 across 45 generator-proxy-gold-task configurations, the median recoverable share of regret rises from 10.4% to 52.0% to 87.7% at expected shortlist sizes 1, 4, 16. Checking ranks 2 through k+1 reaches top-(k+1) coverage with k calls, with a positive median paired accuracy difference in all 54 benchmark-budget-call settings (abstract). LLM text tasks.
- thesis use: evaluation idea: report how much of the gap to the oracle-best candidate a selector recovers as a function of verification calls. Complements the "oracle best-of-K headroom" notes in C.
- verified: OpenReview search record (abstract) read.

### StopTheDream: Outcome-Grounded Candidate Comparison for Adaptive Search in World-Model Planning
- id: OpenReview 3N6YHQlPlv (ICLR 2027 submission) | date: 2026-09 | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: LOW-MED — a world-model planner compares candidate actions by their predicted consequences and decides whether to act or search more (value of computation).
- what: On 120 hierarchical-world-model maze tasks it solves 117 versus 113 for CoVO-MPC with 48.58% fewer latent transitions and 24.38% less planning time; on 1,000 CAST visual trajectories it has 1.3629 absolute trajectory error, 4.18% below a PiJEPA baseline, using 54.11% fewer predictor calls (abstract).
- thesis use: related work for "decide from the candidate set whether more computation is worth it"; not perception tools, not driving.
- verified: OpenReview search record (abstract) read.

### What Should I Try Next? Decision-Relevant Counterfactual Information Gain for Active World Models (AEWM)
- id: OpenReview 4TbO57oz3P (ICLR 2027 submission) | date: 2026-09 | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: LOW-MED — chooses which real interaction to perform by the reduction in uncertainty over decision-relevant counterfactual predictions rather than generic information gain.
- what: Counterfactual Disagreement Reduction (CDR) score. On 60 held-out hidden-physics worlds CDR lowers one-step prediction RMSE at 32 interactions by 19.7% relative to local disagreement, but only "modestly improves budget-curve area relative to random", matches random at the endpoint and costs about 3.2x more scoring time; an all-candidate audit finds weak fidelity of the cheap rankings (abstract). Authors say planner-generated queries and downstream control remain untested.
- thesis use: honest negative-leaning evidence that decision-relevant acquisition scores can barely beat random at an endpoint budget; reminds us to report budget-curve area and scoring cost, as we plan to.
- verified: OpenReview search record (abstract) read.

### When Does Input Adaptation Need a Selector? The Role of Routing-Capable Baselines
- id: OpenReview VyKY79Nn2W (ICLR 2027 submission) | date: 2026-09 | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: LOW-MED (methodology) — shows that a learned selector's headroom shrinks once the baseline can already route among the same candidates.
- what: With 200 development examples the original selector gains 9.6 accuracy points over the frozen predictor, but a routed candidate built from the same maps gains 12.4; across 36 datasets cross-fitted selectors "add little to enlarged libraries" (abstract). Tabular.
- thesis use: evaluation hygiene: our "always-on" and "scene-uncertainty" baselines should be given the same geometry features the MLP selector sees, otherwise the selector gain is overstated.
- verified: OpenReview search record (abstract) read.

### From Information Value to Intervention Value in Language Models
- id: OpenReview XGHBWUciVF (ICLR 2027 submission) | date: 2026-09 | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: LOW-MED — separates "oracle information would help" from "this intervention realizes the gain"; the latter must be measured on held-out outcomes.
- what: Across eight benchmarks oracle information value is the most robust quantity; on FEVER and QASPER frozen interventions chosen from stable diagnostics reduced held-out utility by 0.078 verdict accuracy and 0.048 QASPER score, and another declared action did better (abstract).
- thesis use: caution that an oracle-gain label does not guarantee that a learned tool call realizes it; supports reporting the selector against the oracle and against always-on on held-out scenarios.
- verified: OpenReview search record (abstract) read.

### Do Open-Loop Metrics Predict Closed-Loop Driving? A Cross-Benchmark Correlation Study of NAVSIM and Bench2Drive
- id: arXiv:2605.00066 | date: 2026-04 | venue: arXiv preprint
- authors: Wang, Yiru et al. | code: none seen
- relevance: MED — direct evidence on how far an open-loop score like ours can be trusted.
- what: Pairs published results of 15 methods across NAVSIM (open-loop) and Bench2Drive (closed-loop), 8 with complete paired data. Aggregate PDM Score correlates strongly but non-monotonically with Driving Score with ranking inversions; Ego Progress is the best single predictor; methods that maximize safety at the expense of progress rank high open-loop and underperform closed-loop; a 3-metric formula matches the 5-metric PDMS at Spearman rho=0.90 on n=8 (abstract).
- thesis use: limitation paragraph: open-loop decision accuracy is a proxy; n=8 is small. Also a reason to report a progress-like term (not only collision avoidance) in the oracle.
- verified: abs meta fetched.

### BridgeSim: Unveiling the OL-CL Gap in End-to-End Autonomous Driving
- id: arXiv:2604.10856 | date: 2026-04 | venue: arXiv preprint
- authors: Zhao, Seth Z. et al. | code: none seen
- relevance: MED-LOW — explains why open-loop policies fail in closed loop: observational domain shift and objective mismatch (a biased Q-value that ignores reactive behaviour and temporal awareness); proposes test-time adaptation.
- what: "our analysis highlights the existence of blind spots in standard OL evaluation protocols that fail to capture the realities of closed-loop deployment" (abstract; no numbers in it).
- thesis use: cite with 2605.00066 for the open-loop limitation; supports keeping closed-loop MetaDrive as a later phase.
- verified: abs meta fetched.

### Look, Zoom, Understand: The Robotic Eyeball for Embodied Perception (EyeVLA)
- id: arXiv:2511.15279 | date: 2025-11 | venue: arXiv preprint
- authors: Yang, Jiashu et al. | code: none seen
- relevance: LOW-MED — active perception as the output of a VLA: pan, tilt, zoom commands chosen "under pixel and spatial budget constraints" to acquire the most informative view for an instruction.
- what: PTZ actions tokenized into the VLM vocabulary; pseudo-labels, IoU-controlled refinement and GRPO from only 500 real samples; 96% average task completion over 50 real scenes, five runs (abstract).
- thesis use: related work for learned ROI/zoom selection; not driving, not candidate-conditioned.
- verified: abs meta fetched.

### LiDAS: Lighting-driven Dynamic Active Sensing for Nighttime Perception
- id: OpenReview DRx3yJSYyz | date: 2026 | venue: CVPR 2026 (OpenReview venue string)
- authors: not shown | code: https://simondemoreau.github.io/LiDAS/
- relevance: LOW — allocates a fixed illumination budget (headlights) to maximise downstream perception; +18.7% mAP50 and +5.0% mIoU over low beam at equal power, or 40% less energy at maintained performance (abstract).
- thesis use: an example of resource allocation optimized for downstream performance in driving; no planner in the loop.
- verified: OpenReview search record (abstract) read.

### Learning to Verify: Allocating Revision Effort in Embodied Agents (LVR)
- id: OpenReview lISktdEchA (ICLR 2027 submission) | date: 2026-09 | venue: ICLR 2027 submission
- authors: not shown | code: none seen
- relevance: LOW — selects clarification questions "by their expected effect on verification decisions"; 87.2% success versus 76.6% when every task is revised, with 58% fewer revisions on 47 simulated robot tasks (abstract).
- thesis use: another instance of evaluating a query selector by the decisions it enables, not by prediction accuracy.
- verified: OpenReview search record (abstract) read.

## Leads not followed
- Whether Best-of-Evidence, Support Before Sign and BCRC have arXiv versions or code (OpenReview full text is blocked; authors are anonymous in the search record).
- Full text of DriveAgent-R1's repository training code (tool interface, reward) to copy its tool-call format; only the README was read.
- 2609.08217 (Drive by Hindsight and Foresight) as a competitor: only its baseline paragraph was read.
- CF-VLA and ELF-VLA CVPR 2026 PDFs: existence confirmed only, no author list or numbers read.
- Remaining "per search summary" numbers listed above as STILL UNVERIFIED (BCOD, MVPruner/SToRM, HybridDriveVLA/DualDriveVLA, E:119 traffic-light claim, CropVLM and EnDfuser venues, KITScenes venue).
- SearchAD, ActiveAD and Spatial Retrieval Augmented AD (CVPR 2026) were read only as OpenReview abstracts (Spatial Retrieval) or not at all; none matches the project.
- ICLR 2027 searches were all with the public API (title, keywords, abstract); papers whose abstracts omit driving or query words can still be missed.
