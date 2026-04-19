[README.md](https://github.com/user-attachments/files/26871738/README.md)
<div align="center">

<img src="https://img.shields.io/badge/RENI-v1.1.0--RC-7C6EE0?style=for-the-badge&labelColor=0D1117" alt="RENI Version"/>

# RENI
### Reasoning Engine for Neural Integrity

**Multi-Agent AI Forensic Investigation System for Document Forgery Detection**

*Built for ThinkRoot × Vortex Hackathon 2026 — Track C*

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Try%20RENI-7C6EE0?style=flat-square&logo=vercel&logoColor=white)](#)
[![Documentation](https://img.shields.io/badge/Docs-ThinkRoot-2DD4BF?style=flat-square&logo=gitbook&logoColor=white)](https://reni-docs-hllxs.thinkroot.app)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-7C6EE0?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Agents-F87171?style=flat-square)](https://crewai.com)
[![License](https://img.shields.io/badge/License-MIT-4ADE80?style=flat-square)](LICENSE)

<br/>

> *"Detection is a commodity. Explanation is engineering. RENI does both."*

</div>

---

## What is RENI?

RENI treats every submitted document as a **crime scene**. Instead of running a single model and returning a confidence score, RENI deploys six specialized AI agents — each with a distinct forensic lens — orchestrated by a LangGraph state machine. Their findings are combined using **Dempster-Shafer belief fusion**, and the final verdict is explained in a natural-language forensic report any verification officer can act on.

**The problem it solves:** Forged transcripts, fake certificates, and manipulated government documents are a growing threat in college admissions, scholarship applications, and identity verification. Existing tools either catch obvious fakes or produce opaque scores with no explanation. RENI catches sophisticated forgeries *and* explains exactly why — in language that holds up in a hearing.

---

## Live Demo & Links

| Resource | Link |
|---|---|
| 🌐 Documentation Site | [reni-docs-hllxs.thinkroot.app](https://reni-docs-hllxs.thinkroot.app) |
| 🚀 Live Application | [Try RENI Live](https://reni-docs-hllxs.thinkroot.app/) |

---

## Key Features

- **6 Specialist Agents** running in parallel — pixel forensics, OCR semantics, layout topology, metadata provenance, live cross-referencing, and adversarial stress-testing
- **LangGraph State Machine** with non-linear investigation flow — the *Cycle of Doubt* loops back when agents disagree
- **Dempster-Shafer Belief Fusion** — mathematically rigorous conflict resolution, not simple averaging
- **Causal XAI Forensic Report** — SHAP attribution values converted into a natural-language reasoning chain
- **GradCAM Heatmap Overlay** — suspicious regions highlighted directly on the original document
- **Regional Language Support** — Tamil, Hindi, Devanagari, and English via EasyOCR with semantic consistency checking
- **Live Agent Dialogue Log** — watch the investigation happen in real time via WebSocket streaming
- **Adversarial Stress Agent** — tries to debunk RENI's own verdict before it is finalised
- **Active Learning Loop** — officer corrections retrain the scoring model in-session

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│           React + Tailwind  ·  Live WebSocket Log           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      API LAYER                              │
│              FastAPI  ·  WebSocket Server                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                ORCHESTRATION LAYER                          │
│         LangGraph State Machine  ·  CrewAI Crew             │
│                                                             │
│  INGEST → PARALLEL SCAN → CONFLICT CHECK → DEEP SCAN        │
│       → D-S FUSION → ADVERSARIAL → XAI → OUTPUT             │
└──────┬──────┬──────┬──────┬──────┬──────────────────────────┘
       │      │      │      │      │
  ┌────▼─┐ ┌──▼──┐ ┌─▼───┐ ┌▼────┐ ┌▼──────────┐
  │Pixel │ │ OCR │ │Lay- │ │Prov-│ │Cross-Ref  │
  │Foren-│ │Sem- │ │out  │ │en-  │ │+ Adversar-│
  │ics   │ │antic│ │Topo │ │ance │ │ial Stress │
  └──────┘ └─────┘ └─────┘ └─────┘ └───────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              DEMPSTER-SHAFER FUSION ENGINE                  │
│     Belief combination  ·  Yager conflict resolution        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   XAI NARRATION                             │
│      SHAP + GradCAM → Causal forensic report (LLM)          │
└─────────────────────────────────────────────────────────────┘
```

---

## The 6 Forensic Agents

| Agent | Domain | What It Detects |
|---|---|---|
| **Pixel Forensics** | Image integrity | ELA anomalies, DCT artifacts, clone detection, JPEG re-compression |
| **OCR + Semantic** | Text & language | Text extraction, semantic consistency, meaning drift in regional scripts |
| **Layout Topology** | Spatial forensics | Font clustering outliers (DBSCAN), kerning/spacing inconsistencies, pasted sections |
| **Provenance** | Metadata & origin | EXIF data, PDF creation tool fingerprints, timestamp chain anomalies |
| **Cross-Reference** | Live reality check | Web search to verify institution logos, seals, and document formats |
| **Adversarial Stress** | Devil's advocate | Constructs best innocent explanation — forces verdict to address counter-arguments |

---

## The Cycle of Doubt

RENI's key architectural differentiator. When two agents disagree by more than threshold δ = 0.3, the LangGraph state machine routes back and forces both conflicting agents to re-examine the disputed coordinates at higher resolution — before proceeding to fusion. Maximum 2 iterations to prevent infinite loops.

```
PARALLEL SCAN
      │
      ▼
CONFLICT DETECT ──── no conflict ──────────────────────────┐
      │                                                     │
      │  conflict detected (delta > 0.3)                    │
      ▼                                                     │
DEEP SCAN  (targeted re-scan of disputed coordinates)       │
      │                                                     │
      └──────────────── resolved ──────────────────────────┘
                                                            │
                                                            ▼
                                                      D-S FUSION
```

---

## Dempster-Shafer Belief Fusion

Each agent outputs a belief mass distribution: `{ FORGED: float, GENUINE: float, UNCERTAIN: float }`. These are combined using the Yager combination rule, which handles high-conflict situations by preserving conflict mass — rather than discarding it through averaging.

**Final output includes:**
- Combined confidence score for FORGED / GENUINE hypotheses
- Residual uncertainty mass (lower = more decisive)
- Conflict mass (degree of inter-agent disagreement)
- Plausibility interval `[Bel, Pl]`

The entire D-S fusion engine is ~100 lines of pure Python with zero external dependencies — fully auditable and reproducible.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Orchestration | **LangGraph** | Stateful investigation graph with conditional edges and loops |
| Agents | **CrewAI** | Role-based specialist agents with async parallel dispatch |
| Pixel Analysis | **OpenCV + scikit-image** | ELA, DCT coefficients, phase correlation clone detection |
| Explainability | **PyTorch + GradCAM** | Class activation maps for document heatmap overlay |
| OCR | **EasyOCR + Tesseract 5** | Multi-lingual text extraction: Tamil, Hindi, Devanagari, English |
| Language | **indic-nlp-library** | Semantic consistency checking for Indic scripts |
| PDF Parsing | **PyMuPDF + pikepdf** | Font extraction, deep PDF metadata inspection |
| Attribution | **SHAP + LIME** | Feature attribution weights for XAI narrative generation |
| Web Search | **Tavily** | Live cross-referencing for institution and format verification |
| XAI Narration | **Claude Sonnet API** | Converts SHAP values into causal forensic narrative |
| Backend | **FastAPI** | REST API + WebSocket streaming for live agent log |
| Frontend | **React + Tailwind CSS** | Drag-and-drop UI with real-time investigation display |
| Storage | **SQLite** | Active learning feedback store |
| Belief Fusion | **Custom D-S Engine** | Pure Python Dempster-Shafer implementation |

---

## Project Structure

```
reni/
├── backend/
│   ├── main.py                      # FastAPI app + WebSocket server
│   ├── graph/
│   │   ├── state.py                 # LangGraph shared state definition
│   │   ├── nodes.py                 # All graph nodes
│   │   ├── edges.py                 # Conditional edge logic (Cycle of Doubt)
│   │   └── graph.py                 # Graph assembly and compilation
│   ├── agents/
│   │   ├── crew.py                  # CrewAI crew definition
│   │   ├── pixel_forensics.py       # ELA + DCT + clone detection
│   │   ├── ocr_semantic.py          # EasyOCR + semantic consistency
│   │   ├── layout_topology.py       # Font clustering + spatial analysis
│   │   ├── provenance.py            # EXIF + PDF metadata agent
│   │   ├── cross_reference.py       # Tavily web search agent
│   │   └── adversarial.py           # Stress testing agent
│   ├── fusion/
│   │   └── dempster_shafer.py       # Pure Python D-S belief fusion engine
│   ├── xai/
│   │   ├── shap_analyzer.py         # SHAP feature attribution
│   │   ├── gradcam.py               # GradCAM heatmap generation
│   │   └── narrator.py              # LLM causal narrative generation
│   └── report/
│       └── generator.py             # Forensic PDF report renderer
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── EvidenceIntake.jsx   # Document upload panel
│   │   │   ├── InvestigationLog.jsx # Live WebSocket agent log
│   │   │   ├── ForensicReport.jsx   # Verdict + evidence summary
│   │   │   └── PipelineStatus.jsx   # Investigation pipeline sidebar
│   │   └── App.jsx
│   └── package.json
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys: Anthropic, Tavily

### 1. Clone the repository

```bash
git clone https://github.com/srinivasan-ai-dev/reni.git
cd reni
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=your_anthropic_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — RENI is ready to investigate.

---

## Sample Forensic Report Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RENI FORENSIC INVESTIGATION REPORT
  Document : tamil_nadu_certificate_2024.pdf
  Agents   : 6  |  Duration: 2.4s  |  Loops: 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  VERDICT   : ⚠  LIKELY FORGED
  CONFIDENCE: 91%
  INTERVAL  : [78%, 97%]

  EVIDENCE CHAIN (SHAP-attributed)
  ─────────────────────────────────────────────────────
  [0.54]  FONT INCONSISTENCY @ line 14
          "GOVERNMENT OF INDIA" spacing deviates 2.3σ
          Pixel Agent  : ELA spike at (340, 218)
          Layout Agent : DBSCAN outlier confirmed

  [0.31]  PROVENANCE MISMATCH
          Creation tool : Canva v3.2
          Expected      : GovPrint (confirmed via Cross-Ref)

  [0.15]  SEMANTIC DRIFT (Tamil)
          Issue date appears after expiry date —
          logically impossible in a valid certificate

  ADVERSARIAL CHALLENGE : 0 / 3 findings rebutted
  HUMAN REVIEW          : Not required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Why RENI Wins

Most Track C entries follow the same pattern: run a LayoutLM model → return a confidence score → show a standard heatmap. RENI differentiates at every architectural level:

| Feature | Typical Entry | RENI |
|---|---|---|
| Evidence combination | Simple averaging | Dempster-Shafer fusion |
| Investigation flow | Linear pipeline | Stateful graph with Cycle of Doubt |
| False positive handling | None | Adversarial Stress Agent |
| External grounding | None | Live web search (Tavily) |
| Explanation format | Confidence score + heatmap | Causal narrative + citations |
| Learning | Static | Active learning from officer feedback |

---

## Judging Criteria

| Criterion | Weight | RENI's Approach |
|---|---|---|
| Detection Accuracy | 30% | 6-agent ensemble — forgery must fool all six lenses simultaneously |
| Explainability | 25% | Causal XAI chain + GradCAM overlay + live agent dialogue log |
| Language Robustness | 15% | EasyOCR Tamil/Hindi/Devanagari + semantic drift detection |
| UI / UX | 15% | Live WebSocket investigation stream — judges watch it happen in real time |
| Documentation | 15% | This README + [ThinkRoot site](https://reni-docs-hllxs.thinkroot.app) |

---

## Built At

**ThinkRoot × Vortex Hackathon 2026** — Track C: Explainable AI for Document Forgery Detection

36 hours. One mission: make document fraud investigations explainable.

---

<div align="center">

**RENI v1.1.0-RC** · ThinkRoot × Vortex Hackathon 2026

[Documentation](https://reni-docs-hllxs.thinkroot.app) · [Live App](#) · [Report Issue](../../issues)

*RENI — Reasoning Engine for Neural Integrity*

</div>
