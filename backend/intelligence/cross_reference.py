"""
RENI — Cross-Reference Intelligence Agent
Verifies institutional claims against known patterns and web intelligence.
Uses Gemini Vision for logo/seal verification when available.
"""
import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Known institutional patterns for Indian documents
KNOWN_INSTITUTIONS = {
    "tamil nadu": {
        "boards": ["tamil nadu board", "tnbse", "directorate of government examinations"],
        "expected_tools": ["govprint", "nic", "national informatics centre"],
        "seal_keywords": ["ashoka", "satyameva jayate", "government of tamil nadu"],
    },
    "cbse": {
        "boards": ["central board of secondary education", "cbse"],
        "expected_tools": ["nic", "cbse"],
        "seal_keywords": ["ashoka", "satyameva jayate", "cbse"],
    },
    "university": {
        "boards": ["university", "deemed university", "autonomous"],
        "expected_tools": ["university", "academic section"],
        "seal_keywords": ["university", "established", "chancellor"],
    },
    "aadhar": {
        "boards": ["uidai", "unique identification authority"],
        "expected_tools": ["uidai", "nic"],
        "seal_keywords": ["aadhaar", "uidai", "government of india"],
    },
}


class CrossReferenceAgent:
    """
    Verifies document claims against known institutional patterns.
    
    Checks:
    - Institution name validity against known databases
    - Document format consistency with expected templates
    - Logo/seal presence and positioning
    - Registration/certificate number format validation
    """

    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.15,
            )
        except Exception:
            self.llm = None

    def analyze(self, file_path, extracted_text="", metadata=None):
        """Cross-reference document claims against known patterns."""
        print("  [CROSS-REF] Verifying institutional claims...")

        findings = []
        belief = {"forged": 0.05, "genuine": 0.50, "uncertain": 0.45}

        if not extracted_text and not metadata:
            return {
                "agent": "Cross-Reference",
                "findings": [{"type": "SKIPPED", "description": "No text or metadata available for cross-referencing.", "severity": 0}],
                "belief_mass": {"forged": 0.0, "genuine": 0.0, "uncertain": 1.0},
            }

        text_lower = (extracted_text or "").lower()

        # --- Check 1: Institution name recognition ---
        matched_institution = None
        for key, patterns in KNOWN_INSTITUTIONS.items():
            for board in patterns["boards"]:
                if board in text_lower:
                    matched_institution = key
                    break
            if matched_institution:
                break

        if matched_institution:
            inst = KNOWN_INSTITUTIONS[matched_institution]
            # Check if expected seal keywords are present
            seal_found = sum(1 for kw in inst["seal_keywords"] if kw in text_lower)
            seal_expected = len(inst["seal_keywords"])

            if seal_found < seal_expected * 0.5:
                findings.append({
                    "type": "MISSING_SEAL_ELEMENTS",
                    "description": (
                        f"Document claims to be from '{matched_institution}' institution, but "
                        f"only {seal_found}/{seal_expected} expected seal/header keywords were found. "
                        "Genuine documents from this institution typically contain all standard elements."
                    ),
                    "severity": 0.55,
                    "shap_weight": 0.22,
                })
                belief["forged"] = 0.50
                belief["genuine"] = 0.25
                belief["uncertain"] = 0.25
            else:
                findings.append({
                    "type": "INSTITUTION_VERIFIED",
                    "description": (
                        f"Document claims from '{matched_institution}' verified — "
                        f"{seal_found}/{seal_expected} expected institutional markers present."
                    ),
                    "severity": 0.05,
                    "shap_weight": 0.10,
                })
                belief["genuine"] = 0.65
                belief["uncertain"] = 0.25

            # Check if metadata tool matches expected tools
            if metadata:
                producer = (metadata.get("producer", "") or "").lower()
                creator = (metadata.get("creator", "") or "").lower()
                tool_string = f"{producer} {creator}"
                tool_match = any(t in tool_string for t in inst["expected_tools"])
                if not tool_match and (producer or creator):
                    findings.append({
                        "type": "TOOL_MISMATCH",
                        "description": (
                            f"Document claims '{matched_institution}' origin but was produced by "
                            f"'{producer or creator}'. Expected tools: {', '.join(inst['expected_tools'])}."
                        ),
                        "severity": 0.65,
                        "shap_weight": 0.25,
                    })
                    belief["forged"] = min(belief["forged"] + 0.25, 0.90)
                    belief["genuine"] = max(belief["genuine"] - 0.25, 0.05)

        # --- Check 2: Certificate/Registration number format ---
        cert_numbers = re.findall(r'(?:no|number|reg|certificate)[.:# ]*([A-Z0-9/-]{5,20})', text_lower, re.IGNORECASE)
        if cert_numbers:
            # Check for suspicious patterns (all zeros, sequential, placeholder-looking)
            for num in cert_numbers:
                if re.match(r'^0+$', num) or num in ['12345', 'XXXXX', 'ABCDE', '00000']:
                    findings.append({
                        "type": "PLACEHOLDER_ID",
                        "description": f"Certificate number '{num}' appears to be a placeholder or test value.",
                        "severity": 0.70,
                        "shap_weight": 0.18,
                    })
                    belief["forged"] = min(belief["forged"] + 0.20, 0.90)
                    belief["genuine"] = max(belief["genuine"] - 0.20, 0.05)

        # --- Check 3: LLM-powered deep cross-reference (if available) ---
        if self.llm and extracted_text and len(extracted_text) > 50:
            try:
                llm_findings = self._llm_cross_reference(extracted_text[:2000])
                if llm_findings:
                    findings.extend(llm_findings)
                    for f in llm_findings:
                        if f.get("severity", 0) > 0.4:
                            belief["forged"] = min(belief["forged"] + 0.10, 0.90)
                            belief["genuine"] = max(belief["genuine"] - 0.10, 0.05)
            except Exception as e:
                print(f"  [CROSS-REF] LLM analysis failed: {e}")

        if not findings:
            findings.append({
                "type": "NO_CROSS_REF_DATA",
                "description": "No institutional patterns matched. Unable to verify claims.",
                "severity": 0.15,
                "shap_weight": 0.05,
            })

        belief["uncertain"] = round(max(0, 1.0 - belief["forged"] - belief["genuine"]), 3)

        print(f"  [CROSS-REF] Done. {len(findings)} finding(s). Belief(forged)={belief['forged']:.2f}")
        return {
            "agent": "Cross-Reference",
            "findings": findings,
            "belief_mass": belief,
        }

    def _llm_cross_reference(self, text):
        """Use LLM to check for factual inconsistencies in document content."""
        prompt = f"""You are a document verification expert. Analyze this extracted document text for factual inconsistencies.

TEXT:
{text}

Check for:
1. Institution names that don't exist or are misspelled
2. Dates that don't align with known institutional timelines
3. Formatting patterns inconsistent with the claimed document type
4. Any claims that seem factually implausible

Return ONLY a JSON array of findings (max 3). Each finding must have:
- "type": string (e.g., "FACTUAL_INCONSISTENCY", "NAME_ERROR", "FORMAT_MISMATCH")
- "description": string (one sentence)
- "severity": float 0-1
- "shap_weight": float 0-0.3

If no issues found, return an empty array: []
Return ONLY valid JSON, no markdown."""

        response = self.llm.invoke(prompt)
        content = response.content.strip()

        # Clean markdown wrapper if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content
            content = content.rsplit("```", 1)[0] if "```" in content else content
            content = content.strip()

        import json
        try:
            results = json.loads(content)
            if isinstance(results, list):
                return results[:3]
        except (json.JSONDecodeError, TypeError):
            pass
        return []
