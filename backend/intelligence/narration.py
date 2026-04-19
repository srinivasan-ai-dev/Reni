"""
RENI — XAI Narration Agent
Converts structured forensic findings + D-S fusion scores into a
causal reasoning chain suitable for non-technical verification officers.
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


class XAINarrator:
    """
    Generates forensic-grade narrative reports from structured agent findings.
    Uses Gemini to convert SHAP-weighted findings into natural language.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.25,
        )

    def generate_report(self, doc_id: str, fusion_result: dict, agent_findings: list, adversarial_rebuttals: str = "") -> str:
        """
        Generate a structured forensic narrative from real investigation data.
        """
        # Build the structured evidence summary
        evidence_blocks = []
        for agent in agent_findings:
            agent_name = agent.get("agent", "Unknown")
            belief = agent.get("belief_mass", {})
            findings = agent.get("findings", [])

            block = f"### {agent_name}\n"
            block += f"Belief Mass: Forged={belief.get('forged', 0):.0%}, Genuine={belief.get('genuine', 0):.0%}, Uncertain={belief.get('uncertain', 0):.0%}\n"
            for f in findings:
                severity = f.get("severity", 0)
                shap = f.get("shap_weight", 0)
                block += f"- [{f.get('type', 'FINDING')}] (severity={severity:.0%}, SHAP={shap:.2f}): {f.get('description', '')}\n"
            evidence_blocks.append(block)

        evidence_text = "\n".join(evidence_blocks)

        # Build plausibility info
        pl = fusion_result.get("plausibility", [0, 1])
        
        prompt = f"""ROLE: You are orchestrating a cinematic "LIVE AI COURTROOM" experience. Convert the following forensic findings into a real-time debate.

DOCUMENT: {doc_id}

DEMPSTER-SHAFER FUSION RESULTS:
- Verdict: {fusion_result.get("verdict", "UNKNOWN")}
- Confidence: {fusion_result.get("confidence", 0):.1%}
- Conflict Mass: {fusion_result.get("conflict_mass", 0):.4f}
- Plausibility Interval: [{pl[0]:.1%}, {pl[1]:.1%}]

AGENT EVIDENCE:
{evidence_text}

ADVERSARIAL STRESS TEST:
{adversarial_rebuttals if adversarial_rebuttals else "No successful rebuttals."}

INSTRUCTIONS:
You must output ONLY a raw JSON array of objects representing the debate transcript. Do not use markdown code blocks like ```json around the output. Just output the list itself.
There are three main roles in the debate:
- "Investigator": Accuses using concrete evidence (coordinates, SHAP weights, specific anomalies).
- "Defender": Provides realistic counter-explanations (compression artifacts, formatting variations, scanned noise).
- "Critic": Aggressively evaluates both sides, calling out weak logic or missing evidence.

The debate should last exactly 4-6 turns, building tension. 
After the debate, the FINAL object in the array MUST be the "Judge", who delivers the definitive verdict based EXACTLY on the Dempster-Shafer fusion parameters provided above.

JSON STRUCTURE EXAMPLE:
[
  {{ "role": "Investigator", "text": "I detect a severe ELA spike of 82% at coordinates [340, 218]. This is a clear manipulation signature." }},
  {{ "role": "Defender", "text": "Objection. That's a high-contrast boundary. Compression naturally pools artifacts there." }},
  {{ "role": "Critic", "text": "If it were natural compression, the noise grid variance wouldn't trigger a 4.2 Z-score. The Defender is stretching." }},
  {{ "role": "Judge", "text": "FINAL VERDICT: LIKELY FORGED (91% Confidence). Validated by 5 distinct forensic models. Plausibility bounds set at [91%, 96%]." }}
]

Output *only* the JSON array. Make the dialogue short, sharp, and highly specific to the provided evidence.
"""

        print(f">> [XAI] Generating forensic narrative for {doc_id}...")
        try:
            response = self.llm.invoke(prompt)
            # Strip potential markdown formatting if model didn't listen
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            return content
        except Exception as e:
            print(f">> [XAI] LLM narration failed: {e}")
            return self._fallback_report(doc_id, fusion_result, agent_findings)

    def _fallback_report(self, doc_id, fusion_result, agent_findings):
        """Generate a structured report without LLM if API fails."""
        import json
        verdict = fusion_result.get("verdict", "INCONCLUSIVE")
        confidence = fusion_result.get("confidence", 0)
        pl = fusion_result.get("plausibility", [0, 1])
        
        fallback = [
            {"role": "Investigator", "text": "System overload detected. Proceeding with static evidence review."},
            {"role": "Defender", "text": "Acknowledged. No further real-time debate can be simulated."},
            {"role": "Critic", "text": f"D-S Fusion computed {fusion_result.get('num_agents_fused', 0)} agents. Conflict Mass: {fusion_result.get('conflict_mass', 0):.4f}. Proceeding to judgment."},
            {"role": "Judge", "text": f"FINAL VERDICT: {verdict.upper()} (Confidence: {confidence:.0%}). Plausibility bounds set at [{pl[0]:.0%}, {pl[1]:.0%}]."}
        ]
        
        return json.dumps(fallback)


# --- TEST RUNNER ---
if __name__ == "__main__":
    narrator = XAINarrator()
    sample_fusion = {
        'forged': 0.91, 'genuine': 0.04, 'uncertain': 0.05,
        'conflict_mass': 0.0312, 'plausibility': [0.91, 0.96],
        'verdict': 'LIKELY FORGED', 'confidence': 0.91, 'num_agents_fused': 5,
    }
    sample_findings = [{
        "agent": "Pixel Forensics",
        "findings": [{"type": "ELA_ANOMALY", "description": "ELA spike at (340, 218)", "severity": 0.82, "shap_weight": 0.54}],
        "belief_mass": {"forged": 0.85, "genuine": 0.05, "uncertain": 0.10},
    }]
    print(narrator.generate_report("DOC-2891", sample_fusion, sample_findings))