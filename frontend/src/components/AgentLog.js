import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ScanSearch, Shield, Eye, FileSearch, Globe, Swords,
  Cpu, CheckCircle2, AlertTriangle, Router
} from 'lucide-react';

const AGENT_CONFIG = {
  'System':          { icon: Cpu, color: '#38bdf8' },
  'Orchestrator':    { icon: Cpu, color: '#38bdf8' },
  'Router':          { icon: Router, color: '#a78bfa' },
  'Pixel Forensics': { icon: Eye, color: '#f43f5e' },
  'OCR Semantic':    { icon: ScanSearch, color: '#8b5cf6' },
  'Layout Topology': { icon: FileSearch, color: '#06b6d4' },
  'Provenance':      { icon: Shield, color: '#f59e0b' },
  'Cross-Reference': { icon: Globe, color: '#22c55e' },
  'Adversarial':     { icon: Swords, color: '#ef4444' },
  'D-S Fusion':      { icon: Cpu, color: '#ec4899' },
  'XAI Narration':   { icon: FileSearch, color: '#14b8a6' },
};

function getAgentConfig(agentName) {
  return AGENT_CONFIG[agentName] || { icon: Cpu, color: '#64748b' };
}

export default function AgentLog({ events }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div className="agent-log-container">
      <div className="agent-log-header">
        <Cpu size={14} />
        <span>LIVE INVESTIGATION LOG</span>
        {events.length > 0 && (
          <span className="agent-log-count">{events.length} events</span>
        )}
      </div>
      
      <div className="agent-log-scroll" ref={scrollRef}>
        <AnimatePresence>
          {events.length === 0 && (
            <div className="agent-log-empty">
              <ScanSearch size={24} className="pulse" />
              <span>Awaiting investigation start...</span>
            </div>
          )}
          
          {events.map((event, idx) => {
            const config = getAgentConfig(event.agent);
            const Icon = config.icon;
            const isComplete = event.status === 'complete';
            const isError = event.status === 'error';
            const isWarning = event.message?.includes('⚠');

            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20, height: 0 }}
                animate={{ opacity: 1, x: 0, height: 'auto' }}
                transition={{ duration: 0.3, delay: 0.05 }}
                className={`agent-log-entry ${isComplete ? 'entry-complete' : ''} ${isWarning ? 'entry-warning' : ''}`}
              >
                <div className="agent-log-icon" style={{ color: config.color }}>
                  {isComplete ? (
                    <CheckCircle2 size={14} />
                  ) : isError ? (
                    <AlertTriangle size={14} />
                  ) : isWarning ? (
                    <AlertTriangle size={14} />
                  ) : (
                    <Icon size={14} className="spin-slow" />
                  )}
                </div>
                
                <div className="agent-log-content">
                  <span className="agent-log-name" style={{ color: config.color }}>
                    {event.agent}
                  </span>
                  <span className="agent-log-message">{event.message}</span>
                </div>
                
                <div className="agent-log-status">
                  {isComplete ? (
                    <span className="status-dot status-complete" />
                  ) : (
                    <span className="status-dot status-running" />
                  )}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}
