import React, { useEffect, useState } from 'react';
import api from '../../api';
import LogoAi from '../../assets/Logo_Blanco_Cloud.png';

// Icons
import PdfIcon from '../../assets/pdffile.png';
import TxtIcon from '../../assets/txt-file.png';
import DocIcon from '../../assets/docx-file-format-symbol.png';
import MdIcon from '../../assets/md-file.png';
import GenericIcon from '../../assets/document.png';

// Logout icon
import LogoutIcon from '../../assets/logout.png';

import './Dashboard.css';

function Dashboard({ refreshTrigger, onDocumentSelect, onReturnToUploader }) {
  const [documents, setDocuments] = useState([]);
  const [currentUsername, setCurrentUsername] = useState('');

  useEffect(() => {
    const savedUsername = localStorage.getItem('username') || 'User';
    setCurrentUsername(savedUsername);
    fetchDocuments();
  }, [refreshTrigger]);

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/documents/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const getIconForDocument = (filename) => {
    if (!filename) return GenericIcon;
    const extension = filename.split('.').pop().toLowerCase();
    switch (extension) {
      case 'pdf':
        return PdfIcon;
      case 'doc':
      case 'docx':
        return DocIcon;
      case 'txt':
        return TxtIcon;
      case 'md':
        return MdIcon;
      default:
        return GenericIcon;
    }
  };

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout', {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });

      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const handleDocClick = (docId) => {
    if (onDocumentSelect) {
      onDocumentSelect(docId);
    }
  };

  return (
    <div className="dashboard-container-unique-id">
      <div className="dashboard-main-content-unique-id">
        <div className="dashboard-logo-section-unique-id">
          <img src={LogoAi} alt="Logo" className="dashboard-logo-unique-id" />
          <div className="dashboard-welcome-container-unique-id">
            <h2 className="dashboard-welcome-text-unique-id">Welcome</h2>
            <h3 className="dashboard-username-unique-id">{currentUsername}</h3>
          </div>
        </div>

        <hr className="dashboard-divider-unique-id" />

        <ul className="dashboard-doc-list-unique-id">
          {documents.map((doc) => (
            <li
              key={doc.id}
              className="dashboard-doc-item-unique-id"
              onClick={() => handleDocClick(doc.id)}
            >
              <img
                src={getIconForDocument(doc.original_filename)}
                alt="doc-icon"
                className="dashboard-doc-icon-unique-id"
              />
              <span className="dashboard-doc-name-unique-id" title={doc.original_filename}>
                {doc.original_filename}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Button to return to Uploader */}
      <div className="dashboard-return-section-unique-id" onClick={onReturnToUploader}>
        <span className="dashboard-return-text-unique-id">Upload a Document</span>
      </div>

      {/* Logout button */}
      <div className="dashboard-logout-section-unique-id" onClick={handleLogout}>
        <img src={LogoutIcon} alt="Logout Icon" className="dashboard-logout-icon-unique-id" />
        <span className="dashboard-logout-text-unique-id">Logout</span>
      </div>
    </div>
  );
}

export default Dashboard;
