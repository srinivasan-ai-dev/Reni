import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, ShieldCheck, ShieldQuestion } from 'lucide-react';

export default function VerdictCard({ fusionResult }) {
  if (!fusionResult) return null;

  const {
    verdict = 'INCONCLUSIVE',
    confidence = 0,
    forged = 0,
    genuine = 0,
    uncertain = 0,
    conflict_mass = 0,
    plausibility = [0, 1],
    num_agents_fused = 0,
  } = fusionResult;

  const isForged = verdict.includes('FORGED');
  const isGenuine = verdict.includes('GENUINE');
  const accentColor = isForged ? '#ef4444' : isGenuine ? '#22c55e' : '#f59e0b';
  const VerdictIcon = isForged ? ShieldAlert : isGenuine ? ShieldCheck : ShieldQuestion;

  // SVG gauge parameters
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - confidence);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="verdict-card"
      style={{ borderColor: accentColor + '40' }}
    >
      {/* Confidence Gauge */}
      <div className="verdict-gauge-container">
        <svg viewBox="0 0 120 120" className="verdict-gauge-svg">
          {/* Background track */}
          <circle cx="60" cy="60" r={radius} fill="none" stroke="#1e293b" strokeWidth="8" />
          {/* Animated fill */}
          <motion.circle
            cx="60" cy="60" r={radius}
            fill="none"
            stroke={accentColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: dashOffset }}
            transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
            transform="rotate(-90 60 60)"
            style={{ filter: `drop-shadow(0 0 8px ${accentColor}80)` }}
          />
        </svg>
        <div className="verdict-gauge-label">
          <motion.span
            className="verdict-gauge-percent"
            style={{ color: accentColor }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            {Math.round(confidence * 100)}%
          </motion.span>
          <span className="verdict-gauge-sub">confidence</span>
        </div>
      </div>

      {/* Verdict Label */}
      <div className="verdict-label" style={{ color: accentColor }}>
        <VerdictIcon size={20} />
        <span>{verdict}</span>
      </div>

      {/* Belief Mass Breakdown */}
      <div className="verdict-beliefs">
        <div className="belief-row">
          <span className="belief-name">Forged</span>
          <div className="belief-bar-track">
            <motion.div
              className="belief-bar-fill"
              style={{ backgroundColor: '#ef4444' }}
              initial={{ width: 0 }}
              animate={{ width: `${forged * 100}%` }}
              transition={{ duration: 1, delay: 0.5 }}
            />
          </div>
          <span className="belief-value">{(forged * 100).toFixed(1)}%</span>
        </div>
        <div className="belief-row">
          <span className="belief-name">Genuine</span>
          <div className="belief-bar-track">
            <motion.div
              className="belief-bar-fill"
              style={{ backgroundColor: '#22c55e' }}
              initial={{ width: 0 }}
              animate={{ width: `${genuine * 100}%` }}
              transition={{ duration: 1, delay: 0.6 }}
            />
          </div>
          <span className="belief-value">{(genuine * 100).toFixed(1)}%</span>
        </div>
        <div className="belief-row">
          <span className="belief-name">Uncertain</span>
          <div className="belief-bar-track">
            <motion.div
              className="belief-bar-fill"
              style={{ backgroundColor: '#64748b' }}
              initial={{ width: 0 }}
              animate={{ width: `${uncertain * 100}%` }}
              transition={{ duration: 1, delay: 0.7 }}
            />
          </div>
          <span className="belief-value">{(uncertain * 100).toFixed(1)}%</span>
        </div>
      </div>

      {/* Meta stats */}
      <div className="verdict-meta">
        <div className="verdict-meta-item">
          <span className="meta-label">Conflict Mass</span>
          <span className="meta-value">{conflict_mass.toFixed(4)}</span>
        </div>
        <div className="verdict-meta-item">
          <span className="meta-label">Plausibility</span>
          <span className="meta-value">[{(plausibility[0]*100).toFixed(0)}%, {(plausibility[1]*100).toFixed(0)}%]</span>
        </div>
        <div className="verdict-meta-item">
          <span className="meta-label">Agents Fused</span>
          <span className="meta-value">{num_agents_fused}</span>
        </div>
      </div>
    </motion.div>
  );
}
