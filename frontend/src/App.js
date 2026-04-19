import React, { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldAlert, Cpu, Fingerprint, Clock, ScanSearch } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

import DropZone from './components/DropZone';
import AgentLog from './components/AgentLog';
import VerdictCard from './components/VerdictCard';
import HeatmapOverlay from './components/HeatmapOverlay';
import FusionChart from './components/FusionChart';
import InvestigationTimeline from './components/InvestigationTimeline';
import HITLModal from './components/HITLModal';
import ReportDownload from './components/ReportDownload';
import CourtroomDebate from './components/CourtroomDebate';

const API_BASE = 'http://127.0.0.1:8000';
const WS_BASE = 'ws://127.0.0.1:8000';

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [events, setEvents] = useState([]);
  const [result, setResult] = useState(null);
  const [phase, setPhase] = useState('idle'); // idle | uploading | investigating | complete
  const [elapsedTime, setElapsedTime] = useState(0);
  
  // HITL State
  const [hitlData, setHitlData] = useState(null);
  const [showHitl, setShowHitl] = useState(false);
  const [verdictRevealed, setVerdictRevealed] = useState(false);

  const wsRef = useRef(null);
  const timerRef = useRef(null);

  // Timer effect
  useEffect(() => {
    if (phase === 'investigating') {
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [phase]);

  const handleFileSelected = useCallback((selectedFile) => {
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setResult(null);
    setEvents([]);
    setPhase('idle');
    setElapsedTime(0);
    setHitlData(null);
    setShowHitl(false);
    setVerdictRevealed(false);
  }, []);

  const startInvestigation = async () => {
    if (!file) return;

    setLoading(true);
    setPhase('uploading');
    setEvents([]);
    setResult(null);
    setElapsedTime(0);
    setHitlData(null);
    setVerdictRevealed(false);

    try {
      const formData = new FormData();
      formData.append('file', file);

      setEvents([{
        agent: 'System',
        status: 'running',
        message: 'Uploading document to secure forensic vault...',
      }]);

      const uploadRes = await axios.post(`${API_BASE}/api/v1/upload`, formData);
      const docId = uploadRes.data.doc_id;

      setEvents(prev => [...prev, {
        agent: 'System',
        status: 'complete',
        message: `Document secured [ID: ${docId}]. Initiating LangGraph state machine...`,
      }]);

      setPhase('investigating');

      const ws = new WebSocket(`${WS_BASE}/ws/investigate`);
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(JSON.stringify({ doc_id: docId }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'agent_event') {
            setEvents(prev => [...prev, data]);
          } else if (data.type === 'hitl_required') {
            // Trigger HITL Modal
            setHitlData(data);
            setShowHitl(true);
            setEvents(prev => [...prev, {
              agent: 'System',
              status: 'warning',
              message: '⚠ HUMAN-IN-THE-LOOP INTERVENTION REQUIRED. Pausing final assessment...',
            }]);
          } else if (data.type === 'result') {
            setResult(data);
            setPhase('complete');
            setLoading(false);
            ws.close();
          } else if (data.type === 'error') {
            setEvents(prev => [...prev, {
              agent: 'System',
              status: 'error',
              message: `Fatal error: ${data.message}`,
            }]);
            setLoading(false);
            setPhase('idle');
          }
        } catch (e) {
          console.error('WS parse error:', e);
        }
      };

      ws.onerror = () => {
        fallbackToRest(formData);
      };

      ws.onclose = () => {
        wsRef.current = null;
      };

    } catch (err) {
      console.error('Upload failed:', err);
      const formData = new FormData();
      formData.append('file', file);
      fallbackToRest(formData);
    }
  };

  const fallbackToRest = async (formData) => {
    setEvents(prev => [...prev, {
      agent: 'System',
      status: 'warning',
      message: 'WebSocket unresponsive. Failing over to REST pipeline (no streaming)...',
    }]);

    try {
      const res = await axios.post(`${API_BASE}/api/v1/investigate`, formData);
      setResult(res.data);
      setPhase('complete');
      
      if (res.data.hitl_required) {
        setHitlData({
          rebuttals: res.data.adversarial_rebuttals,
          successful_count: 2, // approximation for REST fallback
          total_findings: 5
        });
        setShowHitl(true);
      }

      setEvents(prev => [...prev, {
        agent: 'System',
        status: 'complete',
        message: `Investigation complete in ${res.data.duration_ms}ms.`,
      }]);
    } catch (err) {
      setEvents(prev => [...prev, {
        agent: 'System',
        status: 'error',
        message: `Investigation pipeline failed: ${err.message}`,
      }]);
      setPhase('idle');
    }
    setLoading(false);
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="app-root">
      {/* Background Ambience */}
      <div className="ambient-background" />

      {/* ─── Header ─── */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-logo pulse-glow">
            <Fingerprint size={28} />
          </div>
          <div className="brand-text">
            <h1>RENI <span className="brand-version">v1.1.0-RC</span></h1>
            <p>Reasoning Engine for Neural Integrity</p>
          </div>
        </div>
        
        {phase === 'investigating' && (
          <div className="header-timer">
            <Clock size={14} />
            <span>T+{formatTime(elapsedTime)}</span>
          </div>
        )}

        <div className="header-status">
          <Activity className={loading ? 'pulse' : ''} size={16} />
          <span>{loading ? 'INVESTIGATING' : 'READY TO SCAN'}</span>
          <span className={`status-indicator ${loading ? 'active' : 'idle'}`} />
        </div>
      </header>

      {/* ─── Main Layout ─── */}
      <main className="app-main">
        {/* Column 1: Intake & Pipeline */}
        <section className="panel-col">
          <div className="panel panel-evidence">
            <div className="panel-header">
              <ShieldAlert size={14}/>
              <span>EVIDENCE INTAKE</span>
            </div>
            <div className="panel-body">
              <DropZone onFileSelected={handleFileSelected} disabled={loading} />

              <button
                className={`btn-investigate ${loading ? 'btn-loading' : ''}`}
                onClick={startInvestigation}
                disabled={loading || !file}
              >
                {loading ? (
                  <>
                    <Cpu size={18} className="spin" />
                    <span>LAUNCHING CREW...</span>
                  </>
                ) : (
                  <>
                    <ScanSearch size={18} />
                    <span>START FORENSIC SCAN</span>
                  </>
                )}
              </button>

              <HeatmapOverlay
                previewUrl={previewUrl}
                heatmapBase64={result?.heatmap_base64}
                isScanning={loading}
              />
            </div>
          </div>

          <div className="panel panel-timeline">
            <InvestigationTimeline events={events} isComplete={phase === 'complete'} />
          </div>
        </section>

        {/* Column 2: Agent Telemetry Log */}
        <section className="panel panel-log">
          <AgentLog events={events} />
        </section>

        {/* Column 3: Forensic Output */}
        <section className="panel panel-report">
          <div className="panel-header">
            <Activity size={14}/>
            <span>FORENSIC REPORT & FUSION</span>
            {phase === 'complete' && result && verdictRevealed && (
              <div style={{marginLeft: 'auto'}}>
                 <ReportDownload result={result} />
              </div>
            )}
          </div>
          <div className="panel-body panel-report-body">
            <AnimatePresence mode="wait">
              {phase === 'idle' && !result && (
                <motion.div
                  key="idle"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="report-empty"
                >
                  <Fingerprint size={48} style={{ opacity: 0.3 }} />
                  <span>Awaiting document upload</span>
                  <p className="hint-text">LangGraph + 5 crew agents standing by.</p>
                </motion.div>
              )}

              {phase === 'investigating' && (
                <motion.div
                  key="investigating"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="report-loading"
                >
                  <div className="cyber-spinner" />
                  <span>Causal Reasoning Engine Active</span>
                  <span className="report-loading-sub">Integrating evidence via Dempster-Shafer fusion...</span>
                </motion.div>
              )}

              {result && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, ease: "easeOut" }}
                  className="w-full flex-1 flex flex-col"
                >
                  <CourtroomDebate 
                    reportJson={result.report} 
                    result={result} 
                    onVerdictRevealed={() => setVerdictRevealed(true)}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </section>
      </main>

      <footer className="app-footer">
        <span>RENI v1.1.0-RC — Multi-Agent Document Intelligence</span>
        <span>ThinkRoot × Vortex Hackathon 2026</span>
      </footer>

      {/* HITL Modal Component */}
      <HITLModal 
        isOpen={showHitl} 
        onClose={() => setShowHitl(false)} 
        docId={result?.doc_id || 'IN-PROGRESS'}
        originalVerdict={result?.fusion_result?.verdict || 'SUSPICIOUS'}
        rebuttals={hitlData?.rebuttals || ''}
        successfulCount={hitlData?.successful_count || 0}
        totalFindings={hitlData?.total_findings || 0}
      />
    </div>
  );
}

export default App;