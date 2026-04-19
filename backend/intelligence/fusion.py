"""
RENI — Dempster-Shafer Belief Fusion Engine
Combines evidence from independent forensic agents using Yager's combination rule.

Unlike simple averaging, D-S theory:
  - Explicitly models uncertainty as a separate category
  - Preserves conflict information instead of washing it out
  - Produces plausibility intervals that bound the true probability
"""


class DSFusion:
    """
    Implements Dempster-Shafer evidence theory with Yager's combination rule
    for handling high-conflict forensic evidence.
    
    Each agent outputs a belief mass distribution:
        m = {forged: float, genuine: float, uncertain: float}
    where forged + genuine + uncertain = 1.0
    """

    HYPOTHESES = ['forged', 'genuine', 'uncertain']

    # Document-type-aware agent weights
    AGENT_WEIGHTS = {
        "pdf": {
            "Pixel Forensics": 0.8,
            "OCR Semantic": 1.0,
            "Layout Topology": 1.2,
            "Provenance": 1.3,
            "Cross-Reference": 1.0,
        },
        "image": {
            "Pixel Forensics": 1.3,
            "OCR Semantic": 0.9,
            "Layout Topology": 0.5,
            "Provenance": 0.8,
            "Cross-Reference": 1.0,
        },
    }

    def combine(self, m1: dict, m2: dict) -> dict:
        """
        Yager's combination rule for two belief mass distributions.
        Conflict mass is assigned to 'uncertain' rather than discarded.
        """
        new_mass = {'forged': 0.0, 'genuine': 0.0, 'uncertain': 0.0}

        # Consonant intersections (hypotheses agree)
        new_mass['forged'] = (
            m1['forged'] * m2['forged'] +
            m1['forged'] * m2['uncertain'] +
            m1['uncertain'] * m2['forged']
        )
        new_mass['genuine'] = (
            m1['genuine'] * m2['genuine'] +
            m1['genuine'] * m2['uncertain'] +
            m1['uncertain'] * m2['genuine']
        )

        # Conflict mass: forged × genuine (agents directly contradict)
        k = m1['forged'] * m2['genuine'] + m1['genuine'] * m2['forged']

        # Yager's rule: assign conflict to uncertain (not discarded)
        new_mass['uncertain'] = m1['uncertain'] * m2['uncertain'] + k

        return new_mass

    def get_final_verdict(self, agent_reports: list, doc_type: str = "image") -> dict:
        """
        Iteratively fuses belief masses from all agents.
        
        Returns:
            {
                forged: float,          # combined belief in forgery
                genuine: float,         # combined belief in authenticity
                uncertain: float,       # residual uncertainty
                conflict_mass: float,   # degree of inter-agent conflict
                plausibility: [lo, hi], # plausibility interval for 'forged'
                verdict: str,           # LIKELY FORGED | LIKELY GENUINE | INCONCLUSIVE
                confidence: float,      # verdict confidence (0-1)
                per_agent: [...]        # individual agent contributions
            }
        """
        if not agent_reports:
            return self._empty_result()

        # Filter out agents that returned pure uncertainty (skipped)
        valid_reports = [
            r for r in agent_reports
            if not (r.get('forged', 0) == 0 and r.get('genuine', 0) == 0)
        ]

        if not valid_reports:
            return self._empty_result()

        print(f">> [FUSION] Fusing {len(valid_reports)} belief masses...")

        # Track individual agent contributions
        per_agent = []
        for i, report in enumerate(valid_reports):
            per_agent.append({
                "index": i,
                "forged": round(report['forged'], 4),
                "genuine": round(report['genuine'], 4),
                "uncertain": round(report['uncertain'], 4),
            })

        # Start with total uncertainty and iteratively combine
        fused = {'forged': 0.0, 'genuine': 0.0, 'uncertain': 1.0}
        total_conflict = 0.0

        for report in valid_reports:
            # Compute conflict before combining
            k = fused['forged'] * report['genuine'] + fused['genuine'] * report['forged']
            total_conflict += k
            fused = self.combine(fused, report)

        # Normalize numerical drift
        total = fused['forged'] + fused['genuine'] + fused['uncertain']
        if total > 0:
            fused = {k: v / total for k, v in fused.items()}

        # --- Plausibility interval for 'forged' hypothesis ---
        # Belief(forged) = lower bound; Plausibility(forged) = Bel + uncertain
        bel_forged = fused['forged']
        pl_forged = fused['forged'] + fused['uncertain']

        # --- Determine verdict ---
        if fused['forged'] > 0.55:
            verdict = "LIKELY FORGED"
            confidence = fused['forged']
        elif fused['genuine'] > 0.55:
            verdict = "LIKELY GENUINE"
            confidence = fused['genuine']
        elif fused['forged'] > fused['genuine']:
            verdict = "SUSPICIOUS — REVIEW RECOMMENDED"
            confidence = fused['forged']
        else:
            verdict = "INCONCLUSIVE"
            confidence = max(fused['forged'], fused['genuine'])

        result = {
            "forged": round(fused['forged'], 4),
            "genuine": round(fused['genuine'], 4),
            "uncertain": round(fused['uncertain'], 4),
            "conflict_mass": round(total_conflict, 4),
            "plausibility": [round(bel_forged, 4), round(pl_forged, 4)],
            "verdict": verdict,
            "confidence": round(confidence, 4),
            "per_agent": per_agent,
            "num_agents_fused": len(valid_reports),
        }

        print(f">> [FUSION] Result: {verdict} (confidence={confidence:.2%}, conflict={total_conflict:.4f})")
        return result

    def compute_conflict_score(self, agent_reports: list) -> float:
        """
        Compute inter-agent disagreement as max delta between any two agents'
        forged scores. Used by the Cycle of Doubt router.
        """
        if len(agent_reports) < 2:
            return 0.0

        forged_scores = [r.get('forged', 0.0) for r in agent_reports
                         if not (r.get('forged', 0) == 0 and r.get('genuine', 0) == 0)]
        
        if len(forged_scores) < 2:
            return 0.0

        return max(forged_scores) - min(forged_scores)

    def compute_shap_weights(self, agent_findings: list) -> list:
        """
        Compute SHAP-like attribution weights for each finding.
        Based on severity × belief_impact × agent_reliability.
        """
        all_weighted = []
        for agent in agent_findings:
            belief = agent.get("belief_mass", {})
            agent_impact = abs(belief.get("forged", 0) - belief.get("genuine", 0))
            for finding in agent.get("findings", []):
                severity = finding.get("severity", 0)
                weight = round(severity * agent_impact * 0.8 + finding.get("shap_weight", 0) * 0.2, 4)
                all_weighted.append({
                    "agent": agent.get("agent", "Unknown"),
                    "finding_type": finding.get("type", ""),
                    "description": finding.get("description", ""),
                    "severity": severity,
                    "computed_shap": weight,
                })
        
        # Normalize
        total = sum(f["computed_shap"] for f in all_weighted) or 1.0
        for f in all_weighted:
            f["normalized_shap"] = round(f["computed_shap"] / total, 4)
        
        return sorted(all_weighted, key=lambda x: x["computed_shap"], reverse=True)

    def _empty_result(self):
        return {
            "forged": 0.0, "genuine": 0.0, "uncertain": 1.0,
            "conflict_mass": 0.0,
            "plausibility": [0.0, 1.0],
            "verdict": "INCONCLUSIVE",
            "confidence": 0.0,
            "per_agent": [],
            "num_agents_fused": 0,
        }


# --- TEST RUNNER ---
if __name__ == "__main__":
    engine = DSFusion()

    # Scenario: Strong disagreement between Pixel and Provenance agents
    pixel_report = {'forged': 0.82, 'genuine': 0.08, 'uncertain': 0.10}
    meta_report = {'forged': 0.15, 'genuine': 0.70, 'uncertain': 0.15}
    layout_report = {'forged': 0.60, 'genuine': 0.20, 'uncertain': 0.20}
    cross_ref_report = {'forged': 0.45, 'genuine': 0.30, 'uncertain': 0.25}

    result = engine.get_final_verdict([pixel_report, meta_report, layout_report, cross_ref_report])
    print(f"\nFused: {result}")
    print(f"Conflict Score: {engine.compute_conflict_score([pixel_report, meta_report, layout_report, cross_ref_report])}")