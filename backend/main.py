"""
RENI — FastAPI Backend with WebSocket Streaming
Features:
  - REST: File upload, investigate, feedback, stats endpoints
  - WebSocket: Real-time investigation event streaming with HITL support
  - Heatmap serving
  - Full LangGraph pipeline integration
  - Active learning feedback loop
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import shutil
import asyncio
import json
import uuid
import time

# Import the real pipeline
from orchestration.graph import reni_app, set_event_queue
from intelligence.active_learning import get_store

app = FastAPI(
    title="RENI — Reasoning Engine for Neural Integrity",
    description="Multi-agent forensic investigation API with real-time streaming, Dempster-Shafer fusion, and explainable verdicts",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ──────────────────────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    doc_id: str
    original_verdict: str
    officer_verdict: str
    confidence: float = 0
    notes: str = ""


# ──────────────────────────────────────────────────────────
# REST Endpoints
# ──────────────────────────────────────────────────────────
@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a document and return a doc_id for investigation."""
    doc_id = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, doc_id)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print(f"\n>> [API] File uploaded: {doc_id}")
    return {"doc_id": doc_id, "status": "uploaded"}


@app.post("/api/v1/investigate")
async def investigate_rest(file: UploadFile = File(...)):
    """Upload + investigate in one call (REST mode, no streaming)."""
    doc_id = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, doc_id)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print(f"\n>> [API] REST investigation started: {doc_id}")
    
    try:
        initial_state = {
            "doc_id": doc_id,
            "file_path": file_path,
            "iterations": 0,
        }
        
        # Use stream_mode="values" to get the full state
        final_state = initial_state.copy()
        for state_update in reni_app.stream(initial_state, stream_mode="values"):
            final_state = state_update
        
        result = final_state
        if result:
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "verdict": result.get("verdict", "INCONCLUSIVE"),
                "report": result.get("report", ""),
                "heatmap_base64": result.get("heatmap_base64", ""),
                "fusion_result": result.get("fusion_result", {}),
                "agent_findings": _sanitize_findings(result.get("agent_findings", [])),
                "hitl_required": result.get("hitl_required", False),
                "duration_ms": result.get("duration_ms", 0),
            }
        
        raise HTTPException(status_code=500, detail="Pipeline produced no output")
        
    except Exception as e:
        print(f">> [API] ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit officer HITL feedback for active learning."""
    try:
        store = get_store()
        store.log_feedback(
            doc_id=feedback.doc_id,
            original_verdict=feedback.original_verdict,
            officer_verdict=feedback.officer_verdict,
            confidence=feedback.confidence,
            notes=feedback.notes,
        )
        stats = store.get_stats()
        return {
            "status": "logged",
            "message": f"Feedback recorded. System has learned from {stats['officer_corrections']} corrections.",
            "accuracy_improvement": stats["accuracy_improvement"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_stats():
    """Get investigation statistics and active learning metrics."""
    try:
        store = get_store()
        stats = store.get_stats()
        recent = store.get_recent_investigations(limit=5)
        return {
            "stats": stats,
            "recent_investigations": recent,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────
# WebSocket — Real-time Investigation Streaming
# ──────────────────────────────────────────────────────────
@app.websocket("/ws/investigate")
async def websocket_investigate(websocket: WebSocket):
    """
    WebSocket endpoint for real-time investigation streaming.
    
    Protocol:
    1. Client connects
    2. Client sends: {"doc_id": "..."} (file must be uploaded first via REST)
    3. Server streams agent events as they happen
    4. Server sends HITL event if adversarial rebuts ≥2 findings
    5. Server sends final result with type="result"
    """
    await websocket.accept()
    print(">> [WS] Client connected")
    
    try:
        # Wait for the client to send investigation parameters
        data = await websocket.receive_text()
        params = json.loads(data)
        doc_id = params.get("doc_id", "")
        
        if not doc_id:
            await websocket.send_json({"type": "error", "message": "No doc_id provided"})
            await websocket.close()
            return
        
        file_path = os.path.join(UPLOAD_DIR, doc_id)
        if not os.path.exists(file_path):
            await websocket.send_json({"type": "error", "message": f"File {doc_id} not found"})
            await websocket.close()
            return
        
        # Create event queue for this investigation
        event_queue = asyncio.Queue()
        set_event_queue(event_queue)
        
        await websocket.send_json({
            "type": "agent_event",
            "agent": "System",
            "status": "running",
            "message": f"Investigation initiated for {doc_id}",
        })
        
        # Run the pipeline in a background task
        async def run_pipeline():
            try:
                initial_state = {
                    "doc_id": doc_id,
                    "file_path": file_path,
                    "iterations": 0,
                }
                
                # Use stream_mode="values" to get the full state
                final_state = initial_state.copy()
                for state_update in reni_app.stream(initial_state, stream_mode="values"):
                    final_state = state_update
                    await asyncio.sleep(0.01)
                
                return final_state
            except Exception as e:
                await event_queue.put({
                    "type": "error",
                    "agent": "System",
                    "message": f"Pipeline error: {str(e)[:200]}"
                })
                return None
        
        # Start pipeline and event streaming concurrently
        pipeline_task = asyncio.create_task(run_pipeline())
        
        # Stream events as they arrive
        while not pipeline_task.done():
            try:
                event = await asyncio.wait_for(event_queue.get(), timeout=0.5)
                await websocket.send_json(event)
            except asyncio.TimeoutError:
                continue
            except Exception:
                break
        
        # Drain remaining events
        while not event_queue.empty():
            try:
                event = await event_queue.get()
                await websocket.send_json(event)
            except Exception:
                break
        
        # Get accumulated result from all pipeline nodes
        result = await pipeline_task
        
        if result:
            
            await websocket.send_json({
                "type": "result",
                "doc_id": doc_id,
                "verdict": result.get("verdict", "INCONCLUSIVE"),
                "report": result.get("report", ""),
                "heatmap_base64": result.get("heatmap_base64", ""),
                "fusion_result": result.get("fusion_result", {}),
                "agent_findings": _sanitize_findings(result.get("agent_findings", [])),
                "hitl_required": result.get("hitl_required", False),
                "adversarial_rebuttals": result.get("adversarial_rebuttals", ""),
                "duration_ms": result.get("duration_ms", 0),
            })
        
        # Reset the global event queue
        set_event_queue(None)
        
    except WebSocketDisconnect:
        print(">> [WS] Client disconnected")
        set_event_queue(None)
    except Exception as e:
        print(f">> [WS] Error: {e}")
        set_event_queue(None)
        try:
            await websocket.send_json({"type": "error", "message": str(e)[:200]})
        except Exception:
            pass


# ──────────────────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────────────────
def _sanitize_findings(findings):
    """Ensure all findings are JSON-serializable."""
    sanitized = []
    for agent_result in findings:
        if isinstance(agent_result, dict):
            clean = {
                "agent": agent_result.get("agent", "Unknown"),
                "findings": agent_result.get("findings", []),
                "belief_mass": agent_result.get("belief_mass", {}),
            }
            # Remove non-serializable fields
            for f in clean["findings"]:
                for k, v in list(f.items()):
                    if not isinstance(v, (str, int, float, bool, list, dict, type(None))):
                        f[k] = str(v)
            sanitized.append(clean)
    return sanitized


@app.get("/")
async def root():
    return {
        "system": "RENI — Reasoning Engine for Neural Integrity",
        "version": "1.0",
        "status": "operational",
        "agents": ["Pixel Forensics", "OCR Semantic", "Layout Topology", "Provenance", "Cross-Reference", "Adversarial Stress"],
        "endpoints": {
            "upload": "POST /api/v1/upload",
            "investigate_rest": "POST /api/v1/investigate",
            "investigate_ws": "WS /ws/investigate",
            "feedback": "POST /api/v1/feedback",
            "stats": "GET /api/v1/stats",
        }
    }


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  RENI API GATEWAY — Starting")
    print("  6 Agents | D-S Fusion | XAI Narration")
    print("=" * 50)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)