import React from 'react';
import { Download } from 'lucide-react';

export default function ReportDownload({ result }) {
  if (!result) return null;

  const handleDownload = () => {
    const reportContent = result.report || 'No report generated.';
    const verdict = result.verdict || 'INCONCLUSIVE';
    const fusion = result.fusion_result || {};
    const docId = result.doc_id || 'UNKNOWN';

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>RENI Forensic Report — ${docId}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0f1a; color: #e2e8f0; padding: 40px; line-height: 1.7; }
    .header { text-align: center; margin-bottom: 40px; padding-bottom: 24px; border-bottom: 2px solid #1e293b; }
    .header h1 { font-size: 28px; color: #38bdf8; margin-bottom: 4px; }
    .header p { color: #64748b; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; }
    .verdict-box { text-align: center; padding: 24px; margin: 24px 0; border-radius: 12px; border: 1px solid #1e293b; background: #111827; }
    .verdict-text { font-size: 22px; font-weight: 800; letter-spacing: 1px; }
    .verdict-forged { color: #ef4444; }
    .verdict-genuine { color: #22c55e; }
    .verdict-uncertain { color: #f59e0b; }
    .stats { display: flex; justify-content: center; gap: 32px; margin-top: 16px; }
    .stat { text-align: center; }
    .stat-label { font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
    .stat-value { font-size: 18px; font-weight: 700; color: #e2e8f0; font-family: monospace; }
    .report-body { margin-top: 32px; }
    .report-body h1 { font-size: 22px; color: #f8fafc; margin: 32px 0 12px; padding-bottom: 8px; border-bottom: 1px solid #1e293b; }
    .report-body h2 { font-size: 17px; color: #38bdf8; margin: 24px 0 8px; text-transform: uppercase; letter-spacing: 0.5px; }
    .report-body h3 { font-size: 14px; color: #06b6d4; margin: 16px 0 6px; }
    .report-body p { margin-bottom: 12px; color: #94a3b8; }
    .report-body strong { color: #f8fafc; }
    .report-body ul { padding-left: 20px; margin-bottom: 12px; }
    .report-body li { margin-bottom: 4px; color: #94a3b8; }
    .footer { text-align: center; margin-top: 48px; padding-top: 24px; border-top: 1px solid #1e293b; color: #475569; font-size: 11px; }
    @media print {
      body { background: white; color: #1a1a1a; padding: 20px; }
      .header h1 { color: #0a0f1a; }
      .verdict-box { background: #f3f4f6; border-color: #d1d5db; }
      .report-body h2 { color: #1e40af; }
      .report-body p, .report-body li { color: #374151; }
      .footer { color: #9ca3af; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>RENI — Forensic Investigation Report</h1>
    <p>Reasoning Engine for Neural Integrity • Document ${docId}</p>
  </div>
  <div class="verdict-box">
    <div class="verdict-text ${verdict.includes('FORGED') ? 'verdict-forged' : verdict.includes('GENUINE') ? 'verdict-genuine' : 'verdict-uncertain'}">
      ${verdict}
    </div>
    <div class="stats">
      <div class="stat"><span class="stat-label">Confidence</span><br/><span class="stat-value">${((fusion.confidence || 0) * 100).toFixed(1)}%</span></div>
      <div class="stat"><span class="stat-label">Conflict Mass</span><br/><span class="stat-value">${(fusion.conflict_mass || 0).toFixed(4)}</span></div>
      <div class="stat"><span class="stat-label">Agents Fused</span><br/><span class="stat-value">${fusion.num_agents_fused || 0}</span></div>
      <div class="stat"><span class="stat-label">Plausibility</span><br/><span class="stat-value">[${((fusion.plausibility?.[0] || 0)*100).toFixed(0)}%, ${((fusion.plausibility?.[1] || 0)*100).toFixed(0)}%]</span></div>
    </div>
  </div>
  <div class="report-body">
    ${reportContent.replace(/^# /gm, '<h1>').replace(/^## /gm, '<h2>').replace(/^### /gm, '<h3>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/^- (.*)/gm, '<li>$1</li>').replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br/>')}
  </div>
  <div class="footer">
    RENI v1.0 — Track C: Explainable AI for Document Forgery Detection<br/>
    ThinkRoot × Vortex Hackathon 2026 • Generated ${new Date().toISOString()}
  </div>
</body>
</html>`;

    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `RENI_Report_${docId}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <button className="btn-download" onClick={handleDownload} id="download-report-btn">
      <Download size={16} />
      <span>Download Forensic Report</span>
    </button>
  );
}
