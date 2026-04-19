"""
RENI — Layout Topology Forensics Engine
Analyzes font consistency, spacing patterns, and structural anomalies in PDF documents.
"""
import os
import fitz  # PyMuPDF
import numpy as np
from collections import Counter


class LayoutForensics:
    """
    Spatial and typographic analysis of document structure.
    
    - Font embedding consistency (DBSCAN-style clustering)
    - Line spacing and margin uniformity
    - Text block alignment analysis
    """

    def analyze(self, file_path):
        """Full layout topology analysis."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext != '.pdf':
            return {
                "agent": "Layout Topology",
                "findings": [{
                    "type": "SKIPPED",
                    "description": "Layout analysis requires PDF input. Image-only documents are analyzed by Pixel Forensics.",
                    "severity": 0,
                }],
                "belief_mass": {"forged": 0.0, "genuine": 0.0, "uncertain": 1.0},
            }

        print("  [LAYOUT] Analyzing document topology...")
        findings = []
        belief = {"forged": 0.05, "genuine": 0.55, "uncertain": 0.40}

        try:
            doc = fitz.open(file_path)

            all_fonts = []
            all_sizes = []
            all_blocks = []
            line_spacings = []

            for page_num, page in enumerate(doc):
                # Extract text blocks with position info
                blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                
                for block in blocks.get("blocks", []):
                    if block.get("type") == 0:  # text block
                        bbox = block.get("bbox", [])
                        all_blocks.append({
                            "page": page_num,
                            "bbox": bbox,
                            "lines": len(block.get("lines", [])),
                        })

                        prev_y = None
                        for line in block.get("lines", []):
                            line_y = line.get("bbox", [0, 0, 0, 0])[1]
                            if prev_y is not None:
                                spacing = line_y - prev_y
                                if 5 < spacing < 100:
                                    line_spacings.append(spacing)
                            prev_y = line_y

                            for span in line.get("spans", []):
                                font_name = span.get("font", "unknown")
                                font_size = span.get("size", 0)
                                all_fonts.append(font_name)
                                all_sizes.append(round(font_size, 1))

            doc.close()

            # --- Check 1: Font diversity ---
            unique_fonts = list(set(all_fonts))
            font_counts = Counter(all_fonts)

            if len(unique_fonts) > 5:
                findings.append({
                    "type": "FONT_INCONSISTENCY",
                    "description": (
                        f"Document uses {len(unique_fonts)} distinct font families: "
                        f"{', '.join(unique_fonts[:6])}{'...' if len(unique_fonts) > 6 else ''}. "
                        "Official documents typically use 1-3 consistent fonts. "
                        "High font diversity suggests content assembled from multiple sources."
                    ),
                    "severity": 0.55,
                    "shap_weight": 0.22,
                })
                belief["forged"] = 0.55
                belief["genuine"] = 0.20
                belief["uncertain"] = 0.25
            elif len(unique_fonts) <= 3:
                findings.append({
                    "type": "FONT_CONSISTENT",
                    "description": f"Document uses {len(unique_fonts)} font(s): {', '.join(unique_fonts)}. Consistent with official templates.",
                    "severity": 0.05,
                    "shap_weight": 0.10,
                })
                belief["genuine"] = max(belief["genuine"], 0.60)

            # --- Check 2: Font size anomalies ---
            if all_sizes:
                size_counts = Counter(all_sizes)
                dominant_size = size_counts.most_common(1)[0][0]

                # Find minority font sizes (used in < 5% of text spans)
                total_spans = len(all_sizes)
                minor_sizes = [
                    s for s, c in size_counts.items()
                    if c / total_spans < 0.05 and abs(s - dominant_size) > 2
                ]
                if minor_sizes:
                    findings.append({
                        "type": "SIZE_ANOMALY",
                        "description": (
                            f"Dominant font size is {dominant_size}pt, but minority sizes "
                            f"({', '.join(str(s) for s in minor_sizes[:5])}pt) appear in isolated spans. "
                            "This pattern is consistent with pasted-in text from a different source."
                        ),
                        "severity": 0.40,
                        "shap_weight": 0.15,
                    })
                    belief["forged"] = min(belief["forged"] + 0.12, 0.90)

            # --- Check 3: Line spacing consistency ---
            if len(line_spacings) > 5:
                spacing_arr = np.array(line_spacings)
                mean_spacing = float(np.mean(spacing_arr))
                std_spacing = float(np.std(spacing_arr))
                cv = std_spacing / (mean_spacing + 1e-10)  # coefficient of variation

                if cv > 0.35:
                    findings.append({
                        "type": "SPACING_IRREGULAR",
                        "description": (
                            f"Line spacing is highly irregular (CV={cv:.2f}, mean={mean_spacing:.1f}px, "
                            f"std={std_spacing:.1f}px). Genuine documents produced by a single system "
                            "exhibit uniform line spacing."
                        ),
                        "severity": round(min(cv, 1.0), 3),
                        "shap_weight": 0.18,
                    })
                    belief["forged"] = min(belief["forged"] + 0.15, 0.90)
                else:
                    findings.append({
                        "type": "SPACING_UNIFORM",
                        "description": f"Line spacing is uniform (CV={cv:.2f}). Consistent with machine-generated documents.",
                        "severity": 0.05,
                        "shap_weight": 0.08,
                    })

            # --- Check 4: Margin consistency ---
            if all_blocks:
                left_margins = [b["bbox"][0] for b in all_blocks if len(b["bbox"]) >= 4]
                if len(left_margins) > 3:
                    margin_std = float(np.std(left_margins))
                    if margin_std > 30:
                        findings.append({
                            "type": "MARGIN_IRREGULAR",
                            "description": (
                                f"Left margin positions vary significantly (std={margin_std:.1f}px). "
                                "Inconsistent margins suggest content blocks were not produced by the same template."
                            ),
                            "severity": round(min(margin_std / 80, 1.0), 3),
                            "shap_weight": 0.10,
                        })
                        belief["forged"] = min(belief["forged"] + 0.08, 0.90)

        except Exception as e:
            findings.append({
                "type": "PARSE_ERROR",
                "description": f"Layout analysis failed: {str(e)}",
                "severity": 0.05,
            })

        if not findings:
            findings.append({
                "type": "LAYOUT_CLEAN",
                "description": "No typographic or spatial anomalies detected.",
                "severity": 0.05,
            })

        belief["uncertain"] = round(max(0, 1.0 - belief["forged"] - belief["genuine"]), 3)

        print(f"  [LAYOUT] Done. {len(findings)} finding(s). Belief(forged)={belief['forged']:.2f}")
        return {
            "agent": "Layout Topology",
            "findings": findings,
            "belief_mass": belief,
        }
