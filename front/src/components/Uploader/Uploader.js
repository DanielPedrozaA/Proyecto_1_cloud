import React, { useState, useRef } from 'react';
import api from '../../api';
import UploadIcon from '../../assets/upload-file.png';
import './Uploader.css';

function Uploader({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSelectFile = () => {
    fileInputRef.current.click();
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', selectedFile);

      await api.post('/documents/upload', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });

      alert('File uploaded successfully!');
      setSelectedFile(null);

      // Trigger the refresh in Dashboard
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('File upload failed. Please try again.');
    }
  };

  return (
    <div className="uploader-container-unique-id">
      <h1 className="uploader-title-unique-id">What do you need to analyze?</h1>
      <div
        className={`uploader-drop-area-unique-id ${isDragging ? 'drag-over-unique-id' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <img src={UploadIcon} alt="Upload Icon" className="uploader-icon-unique-id" />
        <p>Drag and Drop</p>
        <p>
          or{' '}
          <span className="uploader-select-text-unique-id" onClick={handleSelectFile}>
            Select File
          </span>
        </p>
        <input
          type="file"
          ref={fileInputRef}
          className="uploader-file-input-unique-id"
          onChange={handleFileChange}
          hidden
        />
      </div>
      {selectedFile && (
        <p className="uploader-file-name-unique-id">
          Selected file: {selectedFile.name}
        </p>
      )}
      {selectedFile && (
        <button className="uploader-upload-button-unique-id" onClick={handleUpload}>
          Upload
        </button>
      )}
    </div>
  );
}

export default Uploader;
