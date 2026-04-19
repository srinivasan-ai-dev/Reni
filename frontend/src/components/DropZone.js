import React, { useCallback, useState } from 'react';
import { Upload, FileImage, FileText } from 'lucide-react';

export default function DropZone({ onFileSelected, disabled }) {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState('');

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOut = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      setFileName(files[0].name);
      onFileSelected(files[0]);
    }
  }, [onFileSelected]);

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFileName(e.target.files[0].name);
      onFileSelected(e.target.files[0]);
    }
  };

  const isPdf = fileName.toLowerCase().endsWith('.pdf');

  return (
    <div
      className={`dropzone ${isDragging ? 'dropzone-active' : ''} ${disabled ? 'dropzone-disabled' : ''}`}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        id="file-upload"
        accept="image/*,application/pdf"
        onChange={handleFileInput}
        disabled={disabled}
        className="hidden-input"
      />
      <label htmlFor="file-upload" className="dropzone-label">
        {fileName ? (
          <div className="dropzone-file-info">
            {isPdf ? <FileText size={32} /> : <FileImage size={32} />}
            <span className="dropzone-filename">{fileName}</span>
            <span className="dropzone-hint">Click or drop to replace</span>
          </div>
        ) : (
          <div className="dropzone-empty">
            <div className="dropzone-icon-ring">
              <Upload size={28} />
            </div>
            <span className="dropzone-title">Drop evidence here</span>
            <span className="dropzone-hint">PDF, JPG, PNG — up to 20MB</span>
          </div>
        )}
      </label>
    </div>
  );
}
