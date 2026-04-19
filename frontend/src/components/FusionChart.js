import React from 'react';
import { motion } from 'framer-motion';
import { Eye, Shield, FileSearch, ScanSearch } from 'lucide-react';

const AGENT_COLORS = {
  'Pixel Forensics': '#f43f5e',
  'OCR Semantic': '#8b5cf6',
  'Layout Topology': '#06b6d4',
  'Provenance': '#f59e0b',
};

const AGENT_ICONS = {
  'Pixel Forensics': Eye,
  'OCR Semantic': ScanSearch,
  'Layout Topology': FileSearch,
  'Provenance': Shield,
};

export default function FusionChart({ agentFindings }) {
  if (!agentFindings || agentFindings.length === 0) return null;

  return (
    <div className="fusion-chart">
      <div className="fusion-chart-header">
        <span>AGENT BELIEF MASSES</span>
      </div>

      <div className="fusion-chart-body">
        {agentFindings.map((agent, idx) => {
          const name = agent.agent || 'Unknown';
          const belief = agent.belief_mass || {};
          const forged = (belief.forged || 0) * 100;
          const genuine = (belief.genuine || 0) * 100;
          const uncertain = (belief.uncertain || 0) * 100;
          const color = AGENT_COLORS[name] || '#64748b';
          const Icon = AGENT_ICONS[name] || Shield;

          // Skip agents that returned pure uncertainty
          if (forged === 0 && genuine === 0) return null;

          return (
            <motion.div
              key={idx}
              className="fusion-agent-row"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: idx * 0.15 }}
            >
              <div className="fusion-agent-label">
                <Icon size={14} style={{ color }} />
                <span style={{ color }}>{name}</span>
              </div>
              <div className="fusion-stacked-bar">
                <motion.div
                  className="fusion-bar-segment"
                  style={{ backgroundColor: '#ef4444' }}
                  initial={{ width: 0 }}
                  animate={{ width: `${forged}%` }}
                  transition={{ duration: 0.8, delay: 0.3 + idx * 0.15 }}
                  title={`Forged: ${forged.toFixed(1)}%`}
                />
                <motion.div
                  className="fusion-bar-segment"
                  style={{ backgroundColor: '#22c55e' }}
                  initial={{ width: 0 }}
                  animate={{ width: `${genuine}%` }}
                  transition={{ duration: 0.8, delay: 0.4 + idx * 0.15 }}
                  title={`Genuine: ${genuine.toFixed(1)}%`}
                />
                <motion.div
                  className="fusion-bar-segment"
                  style={{ backgroundColor: '#475569' }}
                  initial={{ width: 0 }}
                  animate={{ width: `${uncertain}%` }}
                  transition={{ duration: 0.8, delay: 0.5 + idx * 0.15 }}
                  title={`Uncertain: ${uncertain.toFixed(1)}%`}
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="fusion-legend">
        <span><i style={{ background: '#ef4444' }} /> Forged</span>
        <span><i style={{ background: '#22c55e' }} /> Genuine</span>
        <span><i style={{ background: '#475569' }} /> Uncertain</span>
      </div>
    </div>
  );
}
