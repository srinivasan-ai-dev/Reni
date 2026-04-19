"""
RENI — Pixel Forensics Engine
Real Error Level Analysis (ELA), noise analysis, and heatmap generation.
This is REAL forensics — not LLM hallucinations.
"""
import cv2
import numpy as np
import base64
import os
import tempfile
from PIL import Image, ImageDraw
import io


class PixelForensics:
    """
    Performs genuine pixel-level forensic analysis on document images.
    
    Techniques:
    - Error Level Analysis (ELA): Re-compress at known quality, diff to reveal edits
    - Noise Variance Analysis: Grid-based noise profiling to detect pasted regions
    - Heatmap Generation: Visual overlay of suspicious regions
    """

    QUALITY_LEVELS = [90, 75]
    ELA_AMPLIFICATION = 20
    HOTSPOT_MIN_AREA = 300
    NOISE_GRID_SIZE = 8
    NOISE_Z_THRESHOLD = 2.0

    def _ensure_image(self, file_path):
        """Convert PDF page to image if needed, or load image directly."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            try:
                import fitz
                doc = fitz.open(file_path)
                page = doc[0]
                pix = page.get_pixmap(dpi=200)
                img_path = os.path.join(tempfile.gettempdir(), "reni_pdf_render.png")
                pix.save(img_path)
                doc.close()
                return img_path, True
            except Exception as e:
                print(f"  [PIXEL] PDF render failed: {e}")
                return None, False
        
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp']:
            return file_path, False
        
        return None, False

    def error_level_analysis(self, image_path, quality=90):
        """
        Core ELA algorithm.
        Re-save at known JPEG quality → compute amplified pixel difference.
        Edited regions show higher residuals because they were saved at a different
        compression level than the rest of the image.
        """
        img = cv2.imread(image_path)
        if img is None:
            return None

        temp_path = os.path.join(tempfile.gettempdir(), "reni_ela_resave.jpg")
        cv2.imwrite(temp_path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        resaved = cv2.imread(temp_path)

        try:
            os.remove(temp_path)
        except OSError:
            pass

        if resaved is None or img.shape != resaved.shape:
            return None

        ela = cv2.absdiff(img, resaved).astype(np.float32) * self.ELA_AMPLIFICATION
        ela = np.clip(ela, 0, 255).astype(np.uint8)
        return ela

    def detect_hotspots(self, ela_image, threshold=80):
        """Locate contiguous high-residual regions in the ELA output."""
        gray = cv2.cvtColor(ela_image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        hotspots = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.HOTSPOT_MIN_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                region = gray[y:y + h, x:x + w]
                intensity = float(np.mean(region))
                hotspots.append({
                    "coordinates": [int(x), int(y), int(w), int(h)],
                    "area": int(area),
                    "intensity": round(intensity, 2),
                    "severity": round(min(intensity / 180.0, 1.0), 3),
                })

        return sorted(hotspots, key=lambda h: h["severity"], reverse=True)

    def generate_heatmap(self, image_path, ela_image):
        """Blend a JET colormap heatmap onto the original image and return base64 PNG."""
        original = cv2.imread(image_path)
        if original is None:
            return None

        # Resize ELA to match original if needed
        if ela_image.shape[:2] != original.shape[:2]:
            ela_image = cv2.resize(ela_image, (original.shape[1], original.shape[0]))

        gray_ela = cv2.cvtColor(ela_image, cv2.COLOR_BGR2GRAY)
        
        # Normalize for better visual contrast
        gray_ela = cv2.normalize(gray_ela, None, 0, 255, cv2.NORM_MINMAX)
        
        heatmap = cv2.applyColorMap(gray_ela, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(original, 0.55, heatmap, 0.45, 0)

        _, buffer = cv2.imencode('.png', overlay)
        return base64.b64encode(buffer).decode('utf-8')

    def generate_overlay_heatmap(self, image_path, hotspots):
        img = Image.open(image_path).convert('RGBA')
        mask = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(mask)
        for h in hotspots:
            c = h.get("coordinates", [])
            if len(c) >= 2:
                x, y = c[0], c[1]
                sev = h.get("severity", 0.5)
                alpha = int(min(sev * 180 + 40, 220))
                draw.rectangle([x, y, x + 32, y + 32], fill=(255, 30, 30, alpha))
        composite = Image.alpha_composite(img, mask).convert('RGB')
        buf = io.BytesIO()
        composite.save(buf, format='PNG')
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def noise_analysis(self, image_path):
        """
        Divide image into grid cells, compute noise variance per cell.
        Pasted regions have different noise characteristics from the background.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return []

        h, w = img.shape
        gs = self.NOISE_GRID_SIZE
        cell_h, cell_w = h // gs, w // gs

        variances = []
        for i in range(gs):
            for j in range(gs):
                cell = img[i * cell_h:(i + 1) * cell_h, j * cell_w:(j + 1) * cell_w]
                laplacian = cv2.Laplacian(cell, cv2.CV_64F)
                variance = float(laplacian.var())
                variances.append({"grid": [i, j], "variance": round(variance, 2)})

        if not variances:
            return []

        mean_var = np.mean([v["variance"] for v in variances])
        std_var = np.std([v["variance"] for v in variances])

        anomalous = []
        for v in variances:
            z = abs(v["variance"] - mean_var) / (std_var + 1e-10)
            if z > self.NOISE_Z_THRESHOLD:
                v["z_score"] = round(float(z), 2)
                anomalous.append(v)

        return anomalous

    # ------------------------------------------------------------------
    # Public API — called by the LangGraph pipeline
    # ------------------------------------------------------------------
    def analyze(self, file_path):
        """Full pixel forensics analysis. Returns findings + belief mass + heatmap."""
        print("  [PIXEL] Starting Error Level Analysis...")

        img_path, was_converted = self._ensure_image(file_path)
        if img_path is None:
            return {
                "agent": "Pixel Forensics",
                "findings": [{"type": "SKIPPED", "description": "Unsupported file format for pixel analysis.", "severity": 0}],
                "belief_mass": {"forged": 0.0, "genuine": 0.0, "uncertain": 1.0},
                "heatmap_base64": None,
            }

        findings = []
        heatmap_b64 = None
        belief = {"forged": 0.05, "genuine": 0.45, "uncertain": 0.50}

        # ---- ELA at primary quality ----
        ela = self.error_level_analysis(img_path, quality=self.QUALITY_LEVELS[0])
        if ela is not None:
            hotspots = self.detect_hotspots(ela)
            mean_residual = float(np.mean(ela))

            heatmap_b64 = self.generate_heatmap(img_path, ela)

            if hotspots:
                top = hotspots[0]
                findings.append({
                    "type": "ELA_ANOMALY",
                    "description": (
                        f"Error Level Analysis detected {len(hotspots)} suspicious region(s). "
                        f"Primary anomaly at coordinates {top['coordinates']} with severity {top['severity']:.0%}. "
                        f"Mean ELA residual: {mean_residual:.1f}."
                    ),
                    "severity": top["severity"],
                    "coordinates": top["coordinates"],
                    "shap_weight": 0.54,
                })
                belief["forged"] = min(top["severity"] * 0.75 + 0.15, 0.95)
                belief["genuine"] = max(0.05, 1.0 - belief["forged"] - 0.10)
                belief["uncertain"] = round(1.0 - belief["forged"] - belief["genuine"], 3)

                try:
                    heatmap_b64 = self.generate_overlay_heatmap(img_path, hotspots)
                except Exception:
                    heatmap_b64 = self.generate_heatmap(img_path, ela)
            else:
                findings.append({
                    "type": "ELA_CLEAN",
                    "description": (
                        "ELA found no significant anomalies. Compression artifacts appear uniform "
                        f"across the image (mean residual: {mean_residual:.1f})."
                    ),
                    "severity": 0.05,
                    "shap_weight": 0.30,
                })
                belief = {"forged": 0.05, "genuine": 0.75, "uncertain": 0.20}

        # ---- Noise analysis ----
        noise_anomalies = self.noise_analysis(img_path)
        if noise_anomalies:
            max_z = max(a["z_score"] for a in noise_anomalies)
            findings.append({
                "type": "NOISE_INCONSISTENCY",
                "description": (
                    f"Noise variance analysis flagged {len(noise_anomalies)} grid cell(s) with "
                    f"anomalous noise profiles (max z-score: {max_z:.1f}). "
                    "Regions with different noise characteristics suggest cut-paste manipulation."
                ),
                "severity": round(min(max_z / 5.0, 1.0), 3),
                "shap_weight": 0.15,
            })
            belief["forged"] = min(belief["forged"] + 0.08, 0.95)
            belief["genuine"] = max(belief["genuine"] - 0.08, 0.05)

        # Cleanup temp file
        if was_converted:
            try:
                os.remove(img_path)
            except OSError:
                pass

        print(f"  [PIXEL] Analysis complete. {len(findings)} finding(s). Belief(forged)={belief['forged']:.2f}")
        return {
            "agent": "Pixel Forensics",
            "findings": findings,
            "belief_mass": belief,
            "heatmap_base64": heatmap_b64,
        }
