import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, ShieldCheck, ShieldX, MessageSquare, X } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

export default function HITLModal({ isOpen, onClose, rebuttals, docId, originalVerdict, successfulCount, totalFindings }) {
  const [officerVerdict, setOfficerVerdict] = useState('');
  const [notes, setNotes] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (verdict) => {
    setSubmitting(true);
    try {
      await axios.post(`${API_BASE}/api/v1/feedback`, {
        doc_id: docId,
        original_verdict: originalVerdict,
        officer_verdict: verdict,
        confidence: 0,
        notes: notes,
      });
      setOfficerVerdict(verdict);
      setSubmitted(true);
    } catch (e) {
      console.error('Feedback submit failed:', e);
    }
    setSubmitting(false);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="hitl-backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="hitl-modal"
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ type: 'spring', damping: 25 }}
          onClick={(e) => e.stopPropagation()}
        >
          <button className="hitl-close" onClick={onClose}>
            <X size={18} />
          </button>

          <div className="hitl-header">
            <div className="hitl-warning-icon">
              <AlertTriangle size={28} />
            </div>
            <h2>Human-in-the-Loop Review Required</h2>
            <p className="hitl-subtitle">
              The Adversarial Stress Agent successfully rebutted <strong>{successfulCount}</strong> of{' '}
              <strong>{totalFindings}</strong> findings. Officer judgment is needed.
            </p>
          </div>

          {!submitted ? (
            <>
              <div className="hitl-rebuttals">
                <div className="hitl-rebuttals-header">
                  <MessageSquare size={14} />
                  <span>ADVERSARIAL REBUTTALS</span>
                </div>
                <div className="hitl-rebuttals-body">
                  {rebuttals || 'No rebuttal details available.'}
                </div>
              </div>

              <div className="hitl-notes">
                <textarea
                  placeholder="Officer notes (optional)..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                />
              </div>

              <div className="hitl-actions">
                <button
                  className="hitl-btn hitl-btn-forged"
                  onClick={() => handleSubmit('CONFIRMED FORGED')}
                  disabled={submitting}
                >
                  <ShieldX size={16} />
                  <span>Confirm Forged</span>
                </button>
                <button
                  className="hitl-btn hitl-btn-genuine"
                  onClick={() => handleSubmit('OVERRIDE — GENUINE')}
                  disabled={submitting}
                >
                  <ShieldCheck size={16} />
                  <span>Override — Genuine</span>
                </button>
                <button
                  className="hitl-btn hitl-btn-escalate"
                  onClick={() => handleSubmit('ESCALATED FOR REVIEW')}
                  disabled={submitting}
                >
                  <AlertTriangle size={16} />
                  <span>Escalate</span>
                </button>
              </div>
            </>
          ) : (
            <motion.div
              className="hitl-submitted"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <ShieldCheck size={32} />
              <h3>Feedback Recorded</h3>
              <p>Officer verdict: <strong>{officerVerdict}</strong></p>
              <p className="hitl-learn-msg">System has logged your correction for active learning.</p>
            </motion.div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
