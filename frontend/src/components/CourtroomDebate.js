import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Search, BrainCircuit, Gavel } from 'lucide-react';
import VerdictCard from './VerdictCard';
import FusionChart from './FusionChart';

export default function CourtroomDebate({ reportJson, result, onVerdictRevealed }) {
  const [dialogue, setDialogue] = useState([]);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [showVerdict, setShowVerdict] = useState(false);
  const [parseError, setParseError] = useState(false);

  useEffect(() => {
    try {
      if (!reportJson) return;
      const parsed = JSON.parse(reportJson);
      // Ensure we have an array
      if (!Array.isArray(parsed)) {
        throw new Error("Report is not a debate array.");
      }
      setDialogue(parsed);
      setActiveIndex(0); // Start the debate
    } catch (e) {
      console.error("Courtroom parsing error:", e);
      setParseError(true);
      onVerdictRevealed(); // Fail open so the user can see the verdict
    }
  }, [reportJson]);

  useEffect(() => {
    if (activeIndex >= 0 && activeIndex < dialogue.length) {
      const currentRole = dialogue[activeIndex].role;
      
      // If the current turn is the Judge, wait longer for suspense
      const delay = currentRole === 'Judge' ? 3500 : 2500;
      
      const timer = setTimeout(() => {
        if (currentRole === 'Judge') {
          setShowVerdict(true);
          onVerdictRevealed();
        } else {
          setActiveIndex(activeIndex + 1);
        }
      }, delay);
      
      return () => clearTimeout(timer);
    } else if (activeIndex >= dialogue.length && dialogue.length > 0) {
      // Reached the end before a Judge was found (fallback)
      if (!showVerdict) {
        setShowVerdict(true);
        onVerdictRevealed();
      }
    }
  }, [activeIndex, dialogue, showVerdict, onVerdictRevealed]);

  if (parseError) {
    return (
      <div className="courtroom-error p-4 text-sm text-red-400">
        Debate stream unavailable. Fallback to static verdict overview.
      </div>
    );
  }

  const getRoleIcon = (role) => {
    switch (role) {
      case 'Investigator': return <Search size={18} />;
      case 'Defender': return <Shield size={18} />;
      case 'Critic': return <BrainCircuit size={18} />;
      case 'Judge': return <Gavel size={24} className="text-white" />;
      default: return <BrainCircuit size={18} />;
    }
  };

  const visibleDialogue = dialogue.slice(0, activeIndex + 1);

  return (
    <div className="courtroom-container w-full max-w-4xl mx-auto flex flex-col pt-4">
      <div className="courtroom-arena flex flex-col space-y-6 mb-8 mt-4 mx-6">
        <AnimatePresence>
          {visibleDialogue.map((turn, idx) => {
            if (turn.role === 'Judge') return null; // We handle judge separately

            const isInvestigator = turn.role === 'Investigator';
            const isDefender = turn.role === 'Defender';
            const isCritic = turn.role === 'Critic';
            
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20, x: isInvestigator ? -20 : isDefender ? 20 : 0 }}
                animate={{ opacity: 1, y: 0, x: 0 }}
                transition={{ type: "spring", stiffness: 200, damping: 20 }}
                className={`speech-bubble speech-${turn.role.toLowerCase()}`}
              >
                <div className="speech-avatar">
                  {getRoleIcon(turn.role)}
                </div>
                <div className="speech-content">
                  <div className="speech-role">{turn.role.toUpperCase()}</div>
                  <div className="speech-text">{turn.text}</div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
        
        {/* Animated listening indicator if debate is ongoing */}
        {activeIndex < dialogue.length - 1 && dialogue[activeIndex]?.role !== 'Judge' && (
           <motion.div 
             initial={{opacity: 0}} animate={{opacity: 1}} 
             className="flex items-center space-x-2 text-slate-500 text-xs ml-4"
           >
             <span className="dot-typing"></span> Listening...
           </motion.div>
        )}
      </div>

      {/* Judge Reveal & Verdict Display */}
      <AnimatePresence>
        {showVerdict && (
          <motion.div
            key="judge-reveal"
            initial={{ opacity: 0, scale: 0.95, filter: 'blur(10px)' }}
            animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="judge-verdict-section border-t border-slate-700/50 pt-8 mt-4 bg-slate-900/50 rounded-b-xl shadow-[0_-10px_40px_rgba(0,0,0,0.5)] relative overflow-hidden"
          >
            {/* Cinematic light flash on reveal */}
            <motion.div 
              className="absolute inset-0 bg-cyan-500/10 pointer-events-none"
              initial={{ opacity: 1 }}
              animate={{ opacity: 0 }}
              transition={{ duration: 1.5 }}
            />
            
            {/* Judge's Line */}
            {dialogue.find(d => d.role === 'Judge') && (
              <div className="judge-dialogue flex items-start space-x-4 px-8 mb-8 relative z-10">
                <div className="judge-avatar mt-1 p-3 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-700 border border-indigo-400 shadow-[0_0_20px_rgba(99,102,241,0.5)] text-white">
                  {getRoleIcon('Judge')}
                </div>
                <div>
                  <h3 className="text-sm font-black text-indigo-400 tracking-widest mb-2 uppercase">Court Judgment</h3>
                  <p className="text-xl leading-relaxed text-slate-200 font-medium">
                    "{dialogue.find(d => d.role === 'Judge').text}"
                  </p>
                </div>
              </div>
            )}

            {/* Original Technical Verdict and Charts */}
            <div className="grid grid-cols-1 md:grid-cols-1 gap-6 relative z-10">
              <VerdictCard fusionResult={result.fusion_result} />
              <FusionChart agentFindings={result.agent_findings} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
