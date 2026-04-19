"""
RENI — OCR & Semantic Intelligence Engine
Multi-lingual OCR with semantic consistency checks for document verification.
"""
import easyocr
import os
import re
import fitz  # PyMuPDF

print(">> [OCR ENGINE] Loading multi-lingual text extraction models...")
# Support English + regional Indian languages (Note: EasyOCR cannot mix Tamil and Hindi in the same reader)
reader_devanagari = easyocr.Reader(['en', 'hi', 'mr'], gpu=False)
try:
    reader_tamil = easyocr.Reader(['en', 'ta'], gpu=False)
except Exception as e:
    print(f"  [OCR] Warning: Could not load Tamil model ({e}). Falling back to Devanagari/English.")
    reader_tamil = reader_devanagari

def _get_reader_for_doc(file_path):
    # In a full implementation, this might use langid or tesseract osd.
    # For the hackathon, we default to the devanagari reader unless Tamil is explicitly expected.
    return reader_devanagari
def scan_document(file_path: str) -> dict:
    """
    Extract text from document and perform semantic consistency checks.
    Returns structured output with text, field analysis, and belief mass.
    """
    print(f">> [OCR ENGINE] Scanning: {file_path}")

    if not os.path.exists(file_path):
        return _error_result("File not found.")

    try:
        extracted_text = ""
        text_regions = []
        ext = os.path.splitext(file_path)[1].lower()

        # --- Route 1: PDF Documents ---
        if ext == '.pdf':
            print("  [OCR] PDF detected. Extracting text layers...")
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                extracted_text += page_text + "\n"
                
                # Also extract text blocks with positions for semantic analysis
                blocks = page.get_text("blocks")
                for b in blocks:
                    if len(b) >= 5:
                        text_regions.append({
                            "page": page_num,
                            "bbox": [b[0], b[1], b[2], b[3]],
                            "text": b[4].strip() if isinstance(b[4], str) else "",
                        })
            doc.close()

        else:
            print("  [OCR] Image detected. Engaging Neural OCR...")
            doc_reader = _get_reader_for_doc(file_path)
            results = doc_reader.readtext(file_path, detail=1)
            for (bbox, text, conf) in results:
                extracted_text += text + " "
                text_regions.append({
                    "bbox": [int(bbox[0][0]), int(bbox[0][1]), int(bbox[2][0]), int(bbox[2][1])],
                    "text": text,
                    "confidence": round(conf, 3),
                })

        extracted_text = extracted_text.strip()

        if not extracted_text:
            return {
                "agent": "OCR Semantic",
                "extracted_text": "",
                "findings": [{"type": "BLANK_DOCUMENT", "description": "Document appears blank or text is embedded as unreadable vectors.", "severity": 0.3}],
                "belief_mass": {"forged": 0.20, "genuine": 0.20, "uncertain": 0.60},
                "text_regions": [],
            }

        # --- Semantic Consistency Checks ---
        findings = []
        belief = {"forged": 0.05, "genuine": 0.60, "uncertain": 0.35}

        # Check 1: Date field ordering
        date_issues = _check_date_consistency(extracted_text)
        if date_issues:
            findings.extend(date_issues)
            belief["forged"] = min(belief["forged"] + 0.25, 0.90)
            belief["genuine"] = max(belief["genuine"] - 0.25, 0.05)

        # Check 2: Common forgery patterns
        pattern_issues = _check_forgery_patterns(extracted_text)
        if pattern_issues:
            findings.extend(pattern_issues)
            belief["forged"] = min(belief["forged"] + 0.15, 0.90)
            belief["genuine"] = max(belief["genuine"] - 0.15, 0.05)

        # Check 3: Low OCR confidence regions (image-based only)
        if text_regions:
            low_conf = [r for r in text_regions if r.get("confidence", 1.0) < 0.5]
            if len(low_conf) > 3:
                findings.append({
                    "type": "LOW_OCR_CONFIDENCE",
                    "description": (
                        f"{len(low_conf)} text regions have very low OCR confidence (<50%). "
                        "This may indicate overlaid or poorly blended text edits."
                    ),
                    "severity": 0.35,
                    "shap_weight": 0.12,
                })

        if not findings:
            findings.append({
                "type": "SEMANTIC_CLEAN",
                "description": "Text content appears semantically consistent. No logical anomalies detected.",
                "severity": 0.05,
                "shap_weight": 0.15,
            })

        belief["uncertain"] = round(max(0, 1.0 - belief["forged"] - belief["genuine"]), 3)

        print(f">> [OCR ENGINE] Extracted {len(extracted_text)} chars, {len(findings)} finding(s).")
        return {
            "agent": "OCR Semantic",
            "extracted_text": extracted_text[:3000],  # Cap for API response size
            "findings": findings,
            "belief_mass": belief,
            "text_regions": text_regions[:50],  # Cap region count
            "char_count": len(extracted_text),
        }

    except Exception as e:
        print(f">> [OCR ENGINE] Error: {e}")
        return _error_result(str(e))


def _check_date_consistency(text):
    """Check if dates in the document are logically ordered."""
    findings = []
    
    # Find year-like patterns
    years = re.findall(r'\b(19|20)\d{2}\b', text)
    if len(years) >= 2:
        years_int = [int(y) for y in years]
        # Check for future dates
        from datetime import datetime
        current_year = datetime.now().year
        future_years = [y for y in years_int if y > current_year]
        if future_years:
            findings.append({
                "type": "FUTURE_DATE",
                "description": f"Document contains future year(s): {future_years}. This is logically impossible for a valid document.",
                "severity": 0.80,
                "shap_weight": 0.20,
            })

        # Check for extremely old dates mixed with recent ones
        year_range = max(years_int) - min(years_int)
        if year_range > 50:
            findings.append({
                "type": "DATE_RANGE_ANOMALY",
                "description": (
                    f"Document spans {year_range} years (from {min(years_int)} to {max(years_int)}). "
                    "An unusual date range may indicate content compiled from multiple sources."
                ),
                "severity": 0.40,
                "shap_weight": 0.10,
            })

    return findings


def _check_forgery_patterns(text):
    """Detect common textual patterns associated with forged documents."""
    findings = []
    text_lower = text.lower()

    # Check for template artifacts
    template_markers = ["[insert", "{name}", "<<", ">>", "lorem ipsum", "sample", "specimen"]
    for marker in template_markers:
        if marker in text_lower:
            findings.append({
                "type": "TEMPLATE_ARTIFACT",
                "description": f"Text contains template placeholder marker: '{marker}'. This suggests the document was generated from a template without proper customization.",
                "severity": 0.75,
                "shap_weight": 0.20,
            })
            break

    # Check for inconsistent case in proper nouns (e.g., "GOVERNMENT of INDIA")
    # Simple heuristic: look for mixed ALL-CAPS words adjacent to lowercase
    mixed_case = re.findall(r'\b[A-Z]{3,}\b\s+\b[a-z]+\b\s+\b[A-Z]{3,}\b', text)
    if mixed_case:
        findings.append({
            "type": "CASE_INCONSISTENCY",
            "description": (
                f"Inconsistent capitalization detected: '{mixed_case[0][:50]}'. "
                "Official documents maintain uniform case conventions throughout."
            ),
            "severity": 0.30,
            "shap_weight": 0.08,
        })

    return findings


def _error_result(message):
    return {
        "agent": "OCR Semantic",
        "extracted_text": "",
        "findings": [{"type": "ERROR", "description": f"OCR failed: {message}", "severity": 0.10}],
        "belief_mass": {"forged": 0.0, "genuine": 0.0, "uncertain": 1.0},
        "text_regions": [],
    }


# --- TEST RUNNER ---
if __name__ == "__main__":
    print("\n=== OCR SYSTEM CHECK ===")
    print("Engine is online. Waiting for API Gateway to pass files.")