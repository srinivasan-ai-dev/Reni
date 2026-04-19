import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Layers } from 'lucide-react';

export default function HeatmapOverlay({ previewUrl, heatmapBase64, isScanning }) {
  const [opacity, setOpacity] = useState(0.5);
  const [showHeatmap, setShowHeatmap] = useState(true);

  if (!previewUrl) return null;

  return (
    <div className="heatmap-container">
      <div className="heatmap-header">
        <Layers size={14} />
        <span>OPTICAL FORENSICS SCAN</span>
        {heatmapBase64 && (
          <div className="heatmap-controls">
            <label className="heatmap-toggle">
              <input
                type="checkbox"
                checked={showHeatmap}
                onChange={(e) => setShowHeatmap(e.target.checked)}
              />
              <span>Heatmap</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={opacity * 100}
              onChange={(e) => setOpacity(e.target.value / 100)}
              className="heatmap-slider"
              disabled={!showHeatmap}
            />
          </div>
        )}
      </div>

      <div className="heatmap-viewport">
        {/* Original document */}
        <motion.img
          src={previewUrl}
          alt="Document Evidence"
          className="heatmap-original"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        />

        {/* Heatmap overlay (blended perfectly on backend), opacity controlled by slider */}
        {heatmapBase64 && showHeatmap && (
          <motion.img
            src={`data:image/png;base64,${heatmapBase64}`}
            alt="ELA Heatmap"
            className="heatmap-overlay-img"
            style={{ opacity: opacity }}
            initial={{ opacity: 0 }}
            animate={{ opacity: opacity }}
            transition={{ duration: 0.3 }}
          />
        )}

        {/* Scanning laser animation */}
        {isScanning && (
          <div className="scanning-laser" />
        )}

        {/* Grid overlay while scanning */}
        {isScanning && (
          <div className="scanning-grid" />
        )}
      </div>
    </div>
  );
}
