import React from 'react';
import { motion } from 'framer-motion';
import {
  FileInput, ScanSearch, GitFork, Merge, Swords, FileText, CheckCircle2, Loader2
} from 'lucide-react';

const PHASES = [
  { id: 'ingest', label: 'INGEST', icon: FileInput, desc: 'Document ingestion & format detection' },
  { id: 'parallel_scan', label: 'PARALLEL SCAN', icon: ScanSearch, desc: '5 agents dispatched simultaneously' },
  { id: 'conflict', label: 'CONFLICT CHECK', icon: GitFork, desc: 'Inter-agent disagreement analysis' },
  { id: 'fusion', label: 'D-S FUSION', icon: Merge, desc: 'Yager combination of belief masses' },
  { id: 'adversarial', label: 'ADVERSARIAL', icon: Swords, desc: "Devil's advocate stress test" },
  { id: 'narration', label: 'XAI REPORT', icon: FileText, desc: 'Causal reasoning chain generation' },
];

function getPhaseFromEvents(events) {
  if (!events || events.length === 0) return -1;
  const lastAgent = events[events.length - 1]?.agent || '';
  const lastMsg = events[events.length - 1]?.message || '';

  if (lastAgent === 'XAI Narration') return 5;
  if (lastAgent === 'Adversarial') return 4;
  if (lastAgent === 'D-S Fusion') return 3;
  if (lastAgent === 'Router') return 2;
  if (['Pixel Forensics', 'OCR Semantic', 'Layout Topology', 'Provenance', 'Cross-Reference'].includes(lastAgent)) return 1;
  if (lastAgent === 'Orchestrator' && lastMsg.includes('Ingesting')) return 0;
  if (lastAgent === 'Orchestrator') return 1;
  return 0;
}

export default function InvestigationTimeline({ events, isComplete }) {
  const currentPhase = isComplete ? PHASES.length : getPhaseFromEvents(events);

  return (
    <div className="timeline-container">
      <div className="timeline-header">
        <ScanSearch size={14} />
        <span>INVESTIGATION PIPELINE</span>
      </div>
      <div className="timeline-body">
        {PHASES.map((phase, idx) => {
          const Icon = phase.icon;
          const isActive = idx === currentPhase;
          const isDone = idx < currentPhase;
          const isPending = idx > currentPhase;

          return (
            <motion.div
              key={phase.id}
              className={`timeline-node ${isActive ? 'tl-active' : ''} ${isDone ? 'tl-done' : ''} ${isPending ? 'tl-pending' : ''}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.08 }}
            >
              <div className="tl-connector">
                <div className={`tl-dot ${isActive ? 'tl-dot-active' : ''} ${isDone ? 'tl-dot-done' : ''}`}>
                  {isDone ? (
                    <CheckCircle2 size={12} />
                  ) : isActive ? (
                    <Loader2 size={12} className="spin" />
                  ) : (
                    <Icon size={10} />
                  )}
                </div>
                {idx < PHASES.length - 1 && (
                  <div className={`tl-line ${isDone ? 'tl-line-done' : ''}`} />
                )}
              </div>
              <div className="tl-content">
                <span className="tl-label">{phase.label}</span>
                <span className="tl-desc">{phase.desc}</span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
