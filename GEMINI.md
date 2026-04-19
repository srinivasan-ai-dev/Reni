RENI
Reasoning Engine for Neural Integrity

Project Blueprint — Track C: Explainable AI for Document Forgery Detection
ThinkRoot x Vortex Hackathon 2026  |  36-Hour Challenge
Core Technologies
LangGraph	State Machine Orchestration
CrewAI	6 Specialist Agents
Dempster-Shafer	Belief Fusion
GradCAM / SHAP	Explainability Layer
EasyOCR	Regional Language Support
FastAPI + React	Full-Stack Interface


Version 1.0 — April 2026
 
1. Executive Summary
RENI (Reasoning Engine for Neural Integrity) is a multi-agent AI system designed to investigate, detect, and explain document forgery with forensic-grade precision. Unlike conventional approaches that reduce the problem to a single model confidence score, RENI treats every document as a crime scene — deploying six specialist AI agents, a stateful investigation graph, and mathematically rigorous belief fusion to produce explainable verdicts that verification officers can act on.

RENI is built for Track C of the ThinkRoot x Vortex Hackathon 2026. The system targets college admissions, scholarship applications, and government identity verification — contexts where a forged certificate can have life-altering consequences.

Core thesis: Detection is a commodity. Explanation is engineering. RENI does both — and explains every decision in language a non-technical verification officer can understand.

1.1 What Makes RENI Unique
Most hackathon entries in this track will follow the same pattern: upload document, run a CNN or LayoutLM model, return a confidence score. RENI diverges from this pattern at every architectural level:

•	A LangGraph state machine orchestrates a non-linear investigation that loops, branches, and triggers deeper inspection when agents disagree — a "Cycle of Doubt" that mimics how real forensic investigators work.
•	Six CrewAI specialist agents each bring a unique forensic lens: pixel integrity, OCR semantics, layout topology, metadata provenance, live cross-referencing, and adversarial stress-testing.
•	Dempster-Shafer belief fusion — a mathematically rigorous framework used in real fraud detection labs — combines agent findings while explicitly handling contradictions, rather than washing them out with averaging.
•	A causal XAI layer converts SHAP attribution values into natural-language reasoning chains, so the verdict reads like a forensic report rather than a dashboard widget.
•	An adversarial stress agent actively tries to debunk RENI's own forgery verdict, forcing the final output to address and rebut alternative innocent explanations.
•	An active learning feedback loop lets verification officer corrections retrain the scoring model in-session — the system visibly improves during the demo.
 
2. System Architecture
RENI is structured as five distinct layers, each with clear responsibilities and clean interfaces. The architecture is designed for hackathon velocity — every layer can be built and tested independently — while remaining extensible to production deployment.

 
Figure 1: RENI Full System Architecture — Five-layer stack from presentation to storage

2.1 Layer Breakdown
The five layers are:

Layer	Primary Role	Key Components	Technology
Presentation	Officer-facing UI	Drag-and-drop upload, live agent log, heatmap overlay, report download	React, Tailwind CSS, WebSocket
API	Request routing & streaming	FastAPI backend, WebSocket server, REST endpoints, report renderer	FastAPI, Python
Orchestration	Investigation control flow	LangGraph state machine, CrewAI crew, Cycle of Doubt, HITL handler	LangGraph, CrewAI
Intelligence	Forensic analysis & XAI	Six specialist agents, D-S fusion, SHAP, GradCAM narration	PyTorch, OpenCV, SHAP
Storage	Persistence & learning	SQLite active learning store, template DB, model weights cache	SQLite, filesystem

2.2 Data Flow
A document submitted by a verification officer enters the Presentation Layer and is immediately forwarded to the API Layer, which initialises a LangGraph investigation session. The Orchestration Layer dispatches all six agents in parallel via CrewAI, collects their findings into a shared state object, and applies the Cycle of Doubt logic if agents conflict. The Intelligence Layer's Dempster-Shafer fusion engine combines all belief masses into a final confidence score, which the XAI Narration Agent converts into a structured forensic report. The report — including the GradCAM heatmap overlay — is streamed back to the frontend in real time via WebSocket.
 
3. LangGraph State Machine — Investigation Flow
The LangGraph state machine is the heart of RENI. Unlike a linear pipeline, the graph has conditional edges that allow the investigation to loop, branch, and escalate based on what agents discover. This mirrors the non-linear nature of real forensic investigations, where a single finding can reopen earlier conclusions.

 
Figure 2: LangGraph State Machine — All nodes, conditional edges, and the Cycle of Doubt loop

3.1 Graph Nodes
The graph consists of eight nodes, each with a clearly defined responsibility:

Node	Type	Responsibility	Output to State
INGEST	Entry	Document ingestion, format detection, language identification, state initialisation	{ doc_id, pages, language, raw_text }
PARALLEL SCAN	Parallel dispatch	All six agents dispatched asynchronously; findings written to shared state as they complete	{ agent_reports: {} }
CONFLICT DETECT	Conditional	Computes inter-agent disagreement scores; routes to Deep Scan if delta > 0.3, else to Fusion	{ conflicts: [], route: "deep"|"fusion" }
DEEP SCAN	Conditional loop	Re-dispatches conflicting agents with disputed coordinates injected; max 2 iterations	{ updated_reports }
D-S FUSION	Computation	Dempster-Shafer combination of all belief masses; produces plausibility interval	{ confidence, conflict_mass }
ADVERSARIAL	Challenge	Stress agent constructs best innocent explanation; triggers HITL flag if > 2 findings rebutted	{ rebuttals, hitl_flag }
XAI NARRATION	LLM generation	SHAP values + agent logs converted to causal reasoning chain in natural language	{ narrative, citations }
OUTPUT	Terminal	GradCAM heatmap render, agent dialogue log assembly, forensic PDF report generation	{ report_url, heatmap_url }

3.2 The Cycle of Doubt
"If any two agents disagree beyond threshold δ = 0.3, the graph loops back and forces all conflicting agents to re-examine the disputed coordinates at higher resolution. Maximum two iterations."

This is the key differentiator from a linear pipeline. When the Conflict Detect node identifies a disagreement — for example, the Pixel agent says low suspicion while the Provenance agent says high suspicion — the graph routes back to the Deep Scan node. Both conflicting agents are re-dispatched with the disputed pixel coordinates and PDF byte ranges explicitly injected into their context. The conflict is resolved before the fusion step, producing a far more reliable final verdict.

3.3 Human-in-the-Loop (HITL) Interrupt
If the Adversarial Stress Agent successfully rebuts more than two of the primary agent findings, RENI raises a HITL flag and pauses the investigation. The frontend displays the conflicting evidence and asks the verification officer to provide a judgment call. This judgment is logged to the active learning store and used to retrain the fusion scorer.

During the demo, this feature is triggered deliberately with an ambiguous document to demonstrate explainable AI transparency — the system knows what it does not know.
 
4. CrewAI Specialist Agent Crew
RENI deploys six specialist agents using the CrewAI framework. Each agent has a defined role, a curated toolset, and a specific type of evidence it is responsible for. Agents run in parallel during the Parallel Scan node and are capable of targeted re-investigation during the Deep Scan node.

 
Figure 3: CrewAI Agent Architecture — Six specialist agents with shared state and D-S fusion

4.1 Agent Profiles

Agent	Domain	Core Analysis	Tools
Pixel Forensics Agent	Image integrity	Error Level Analysis (ELA), DCT coefficient inspection, clone detection via phase correlation, JPEG re-compression artifact analysis. Pinpoints tampered pixel coordinates.	OpenCV, Pillow, scikit-image, PyTorch GradCAM
OCR + Semantic Agent	Text and language	Extracts text via EasyOCR (Tamil, Hindi, Devanagari, English). Checks semantic consistency — date fields must be logically ordered, institution names in expected positions. Flags meaning drift in regional scripts.	EasyOCR, Tesseract 5, spaCy, indic-nlp-library
Layout Topology Agent	Spatial forensics	Clusters font embeddings using DBSCAN to detect pasted-in sections. Checks kerning, line-spacing, and margin consistency. Flags paragraphs with a different spatial fingerprint from the surrounding content.	PyMuPDF, pdfplumber, DBSCAN (scikit-learn), fonttools
Provenance Agent	Metadata and origin	Inspects EXIF data, PDF creation tool fingerprints (Canva, Photoshop, Word), timestamp chains, and embedded object hashes. Detects if a PDF was born digital versus scanned and re-saved.	exiftool, PyPDF2, pikepdf, hashlib
Cross-Reference Agent	Live reality check	Autonomously searches the web to verify if a listed university, company, or government body uses the specific logo, seal, or document format found in the submitted document. Grounds the investigation in live external reality.	Tavily Search API, Claude Vision, BeautifulSoup
Adversarial Stress Agent	Devil's advocate	Constructs the most convincing innocent explanation for every flagged anomaly. Forces the final verdict to address and rebut alternative hypotheses. Triggers HITL flag if more than 2 findings are successfully rebutted.	Claude Sonnet API, structured prompting

4.2 Agent 6: Adversarial Stress Agent (The Devil's Advocate)
This agent is RENI's most architecturally novel component. After all primary agents report their findings, the Stress Agent receives the full evidence set and attempts to construct the most convincing possible innocent explanation for every flagged anomaly.

If the stress agent successfully rebuts fewer than 2 findings, the forgery verdict stands with high confidence. If it rebuts 2 or more findings, the confidence is downgraded and the HITL flag is raised. This mechanism forces RENI to address alternative hypotheses before committing to a verdict — exactly how a real forensic expert would approach contested evidence.

The stress agent uses a structured prompting strategy with Claude Sonnet: it is given the role of a defence attorney and tasked with finding innocent explanations for each flagged anomaly. The output is a structured list of rebuttals, each scored for plausibility.
 
5. Dempster-Shafer Belief Fusion
The Dempster-Shafer (D-S) theory of evidence is a generalisation of Bayesian probability that explicitly handles uncertainty and conflict. It is the standard framework for combining evidence from independent sources in forensic and intelligence analysis — and the reason RENI's final verdict is more trustworthy than any single-model output.

 
Figure 4: D-S Belief Fusion — Per-agent belief masses (left) and combined fused output (right)

5.1 Why Not Simple Averaging?
Simple averaging of confidence scores conceals conflicting evidence. If one agent reports 0.9 (forged) and another reports 0.1 (genuine), averaging gives 0.5 — which suggests the system is uncertain, but hides the fact that two agents are in strong disagreement. D-S theory preserves this conflict information and exposes it explicitly as a "conflict mass" in the output.

5.2 How D-S Fusion Works in RENI
Each agent outputs a belief mass distribution across three hypotheses: FORGED, GENUINE, and UNCERTAIN. The D-S fusion engine combines these distributions using the Yager combination rule, which handles high-conflict situations by assigning the conflict mass to the "uncertain" category rather than discarding it. The final output includes:

•	A combined confidence score for the FORGED hypothesis
•	A combined confidence score for the GENUINE hypothesis
•	A residual uncertainty mass (lower is better)
•	A conflict mass — the degree to which agents fundamentally disagreed
•	A plausibility interval [Bel, Pl] bounding the true probability

RENI's D-S fusion engine is approximately 100 lines of pure Python — no external libraries. It is one of the most mathematically sophisticated components in the hackathon and will be immediately recognisable to any MAANG ML engineer reviewing the codebase.
 
6. Explainable AI — The Forensic Report
Explainability accounts for 25% of the judging score — and RENI's approach to it goes far beyond standard heatmaps or feature importance bars. The XAI Narration Agent converts SHAP attribution values, LIME local explanations, and the full agent dialogue log into a structured causal reasoning chain that reads like a professional forensic audit.

6.1 Sample Forensic Report Narrative
Document DOC-2891 (Tamil Nadu Board Certificate) was assessed by RENI with 91% confidence as LIKELY FORGED.  Primary signal (SHAP weight 0.54): A font inconsistency was detected at line 14. The character spacing in "GOVERNMENT OF INDIA" deviates 2.3 standard deviations from the surrounding text. This finding was independently corroborated by both the Pixel Forensics Agent (ELA residual spike at coordinates 340, 218) and the Layout Topology Agent (DBSCAN cluster outlier at the same location).  Secondary signal (SHAP weight 0.31): The PDF metadata indicates the document was created using Canva v3.2. Genuine Tamil Nadu Board certificates are produced via the government's internal GovPrint system. The Cross-Reference Agent confirmed this discrepancy via the official Tamil Nadu Board website.  Tertiary signal (SHAP weight 0.15): A semantic inconsistency was detected in the Tamil-language content. The field for issue date ('veLiyeedu tedhi') appears after the expiry date field — which is logically impossible for a valid certificate.  Adversarial Stress Agent rebutted 0 of 3 findings. Human-in-the-loop review was not triggered. Verdict: LIKELY FORGED.

6.2 GradCAM Heatmap Overlay
In addition to the narrative report, RENI overlays a GradCAM-generated heatmap onto the original document image. Regions of high suspicion are highlighted in red-orange, allowing a verification officer to see exactly which part of the document triggered the forgery verdict — without needing to read the technical narrative at all.

6.3 Live Agent Dialogue Log
The frontend streams the agent conversation log in real time via WebSocket during the investigation. Verification officers can watch the investigation unfold — seeing which agent flagged what, and how the Adversarial Stress Agent challenged each finding. This is the feature that will make judges stop and watch during the demo.
 
7. Full Technology Stack
Every component in RENI's stack was chosen for a specific reason. The following table maps each technology to its role and the architectural justification for its inclusion.

Technology	Layer	Role	Why This Choice
LangGraph	Orchestration	State machine	Enables non-linear investigation flow with conditional edges and loops — impossible with a linear pipeline
CrewAI	Orchestration	Agent framework	Role-based specialisation, parallel dispatch, and shared state make multi-agent coordination clean and testable
Tavily Search	Intelligence	Live web search	Enables the Cross-Reference Agent to ground findings in live external reality during the demo
OpenCV	Intelligence	Pixel forensics	Mature, well-tested library for ELA, DCT analysis, and clone detection — battle-tested in forensic contexts
scikit-image	Intelligence	Phase correlation	SSIM and phase correlation for clone detection that OpenCV does not natively support
PyTorch + GradCAM	Intelligence	Heatmap generation	Class Activation Maps provide pixel-level attribution visualisation for non-technical officers
EasyOCR	Intelligence	Multi-lingual OCR	Native support for Tamil, Hindi, Devanagari without language pack installation — critical for regional docs
Tesseract 5	Intelligence	OCR fallback	Higher accuracy fallback for document types where EasyOCR underperforms
indic-nlp-library	Intelligence	Semantic analysis	Provides morphological analysis and semantic tooling for Indic scripts beyond character recognition
PyMuPDF	Intelligence	PDF parsing	Fastest Python PDF library for font extraction and layout analysis — key for the Layout Topology Agent
pikepdf	Intelligence	PDF metadata	Deep PDF object-level inspection for the Provenance Agent — exposes creation tool signatures
SHAP	Intelligence	XAI attribution	Game-theoretic feature attribution that provides reliable per-finding weights for the narrative generator
Custom D-S Engine	Intelligence	Belief fusion	~100 lines of pure Python implementing Yager combination — no external dependencies, fully auditable
Claude Sonnet API	Intelligence	XAI narration	Converts structured SHAP+agent data into fluent forensic narrative via carefully engineered system prompt
FastAPI	API	Backend	High-performance async API with native WebSocket support for streaming the agent log to the frontend
React + Tailwind	Presentation	Frontend	Fast component development; Tailwind enables polished UI without a design system overhead
SQLite	Storage	Active learning	Zero-dependency persistent store for officer feedback; lightweight enough for the 36-hour build

 
8. 36-Hour Execution Plan
The 36-hour build is structured in five phases. Backend (Python/LangGraph/CrewAI) and frontend (React) tracks run in parallel from Hour 5 onwards, enabling simultaneous progress on intelligence and user experience.

 
Figure 5: 36-Hour Gantt Timeline — Five phases with parallel backend/frontend tracks

Phase	Hours	Focus	Key Deliverable
1 — Foundation	H0–H4	LangGraph state machine scaffold, CrewAI agent skeletons (all 6), document ingestion pipeline, language detection working	End-to-end graph running on a test document (even with stub agent outputs)
2 — Core Agents	H5–H12	Pixel agent (ELA + DCT), OCR agent with EasyOCR Tamil/Hindi, end-to-end pipeline on real forged document samples, basic React UI with drag-and-drop	Two agents producing real findings; UI accepting uploads
3 — Intelligence	H13–H22	Layout + Provenance agents, Cross-Reference agent (Tavily), Dempster-Shafer fusion engine, Cycle of Doubt conditional routing, SHAP integration	Full 5-agent pipeline with D-S fusion producing a verdict
4 — XAI + Polish	H23–H30	XAI Narration Agent (LLM prompt), GradCAM heatmap overlay on document image, Adversarial Stress Agent, live WebSocket agent dialogue log, forensic PDF report renderer	Full RENI output: narrative + heatmap + agent log + PDF report
5 — Ship It	H31–H36	Active learning feedback store, deployment to Railway or HuggingFace Spaces, thinkroot.dev documentation site, demo video recording, GitHub README and clean repo	Publicly accessible demo + documentation + submitted repo

8.1 Critical Path
The critical path runs through: LangGraph scaffold → Pixel Agent (ELA) → D-S Fusion engine → XAI Narration Agent → GradCAM heatmap. Everything else can be parallelised. If time pressure mounts, the Cross-Reference Agent and Active Learning store are the first features to defer — the core forensic capability does not depend on them.
 
9. Judging Criteria Alignment
The judging panel scores five criteria. This section maps each criterion to the specific RENI features and architectural decisions that address it — and explains why RENI's approach is likely to outscore competing entries in every category.

 
Figure 6: RENI vs Average Competitor — Projected judging scores per criterion

Criterion	Weight	RENI's Approach	Competitive Advantage
Detection Accuracy	30%	Six-agent ensemble with D-S fusion. ELA + provenance + layout topology + cross-reference together catch forgeries that any single model misses. The adversarial agent further stress-tests the verdict before it is finalised.	Single-model competitors have one failure mode. RENI has six independent forensic lenses — a forgery must fool all six simultaneously to escape detection.
Explainability	25%	Causal XAI reasoning chain (SHAP → LLM narrative). GradCAM heatmap overlay on original document. Live agent dialogue log streamed to frontend. Adversarial rebuttal in the report. Per-finding SHAP weights cited in the narrative.	Most teams will show a confidence score and a standard heatmap. RENI shows a structured forensic narrative, a dialogue log, and an explicit rebuttal of alternative hypotheses — three distinct explainability layers.
Language Robustness	15%	EasyOCR covers Tamil, Hindi, Devanagari, and English natively. The OCR + Semantic Agent goes beyond character recognition to check meaning consistency within regional scripts — detecting semantic drift that a simple OCR pass cannot catch.	Competitors relying on Tesseract alone will struggle with complex regional scripts. RENI demonstrates live with real Tamil Nadu and Hindi document samples.
UI / UX	15%	Drag-and-drop upload with real-time progress. Live WebSocket agent dialogue stream during investigation (judges watch the investigation happen). GradCAM heatmap rendered on the original document. One-click forensic PDF report download.	The live agent dialogue stream is the single most demo-effective feature in the project. Judges will stop what they are doing to watch RENI investigate in real time.
Documentation	15%	thinkroot.dev site with system architecture diagram, agent role descriptions, D-S fusion explainer, live demo link, sample forged documents to test, and a GitHub repo with clean README, setup instructions, and annotated code.	Documentation that includes an interactive demo and sample test cases is far more compelling than a static README. Judges can verify claims without running the code locally.
 
10. Unique Selling Points — Why RENI Wins
The following table consolidates RENI's six core differentiators and explains why each one is unlikely to appear in competing submissions.

Differentiator	What It Means	Why Competitors Won't Have It
Dempster-Shafer belief fusion	Mathematically rigorous combination of uncertain evidence from independent sources, with explicit conflict resolution — the same framework used in real fraud detection labs.	Requires understanding of evidence theory beyond standard ML curricula. Most teams will use weighted averaging or a majority vote, which conceals conflicting evidence.
Cycle of Doubt (LangGraph)	When agents disagree, the graph routes back and forces a targeted re-investigation of the disputed evidence before producing a verdict.	A non-linear LangGraph investigation loop requires understanding of stateful graph orchestration — beyond a simple CrewAI chain. Most teams will build linear pipelines.
Adversarial Stress Agent	A sixth agent whose sole job is to debunk the forgery verdict — forcing the final output to address and rebut alternative hypotheses before committing.	The adversarial agent pattern is common in AI safety research but rare in applied hackathon settings. No standard tutorial demonstrates this pattern for document forensics.
Cross-Reference Agent	Live web search to verify if a listed institution actually uses the specific logo, seal, or document format in the submitted document.	Requires a live search API (Tavily) and multimodal vision comparison — technically achievable but unlikely in a 36-hour build without prior architecture planning.
Causal XAI reasoning chain	SHAP attribution values are converted by an LLM into a structured forensic narrative with per-finding citations — not a bar chart, a forensic report.	The prompt engineering required to reliably convert SHAP values into fluent, structured legal-grade narrative requires deliberate design. Most teams stop at the SHAP visualisation.
Active learning feedback loop	Officer corrections retrain the fusion scorer in-session — the system improves during the demo itself.	Active learning requires a persistent feedback store and a retraining hook, both of which add implementation complexity that most teams will defer.

10.1 The One-Line Pitch
RENI does not detect forgeries. RENI investigates documents — and explains every conclusion in language that will hold up in a hearing.

10.2 What Competitors Will Build
Based on the problem statement and standard hackathon patterns, the typical Track C entry will likely include: a LayoutLM or fine-tuned ViT model, ELA visualisation, a confidence score output, a basic Gradio or Streamlit UI, and Tesseract-based OCR. These are all correct and sensible choices — but they are commodity solutions. RENI's differentiation is not in any single component but in the system architecture: stateful investigation, inter-agent debate, adversarial stress-testing, and causal explanation generation.
 
