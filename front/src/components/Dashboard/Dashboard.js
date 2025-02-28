import React, { useEffect, useState } from 'react';
import api from '../../api'; // Same api instance used in Login.js
import LogoAi from '../../assets/Logo_Blanco_Cloud.png';

// Icons for documents
import PdfIcon from '../../assets/pdffile.png';
import TxtIcon from '../../assets/txt-file.png';
import DocIcon from '../../assets/docx-file-format-symbol.png';
import MdIcon from '../../assets/md-file.png';
import GenericIcon from '../../assets/document.png';

// Logout icon
import LogoutIcon from '../../assets/logout.png';

import './Dashboard.css';

function Dashboard({ refreshTrigger }) {
  const [documents, setDocuments] = useState([]);
  const [username] = useState('User1'); // For now, a default; later, pass via props or context

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/documents/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  // Fetch documents on mount and whenever refreshTrigger changes
  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger]);

  // Determine which icon to display based on file extension
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

  // Handle Logout
  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('token');
      await api.post('/auth/logout', {}, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      // Remove token and redirect to login page
      localStorage.removeItem('token');
      window.location.href = '/login';
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <div className="dashboard-container-unique-id">
      {/* Main content (logo, welcome, documents) */}
      <div className="dashboard-main-content-unique-id">
        <div className="dashboard-logo-section-unique-id">
          <img src={LogoAi} alt="Logo" className="dashboard-logo-unique-id" />
          <h2 className="dashboard-welcome-unique-id">
            Welcome <span className="dashboard-username-unique-id">{username}</span>
          </h2>
        </div>

        <hr className="dashboard-divider-unique-id" />

        <ul className="dashboard-doc-list-unique-id">
          {documents.map((doc) => (
            <li key={doc.id} className="dashboard-doc-item-unique-id">
              <img
                src={getIconForDocument(doc.original_filename)}
                alt="doc-icon"
                className="dashboard-doc-icon-unique-id"
              />
              <span
                className="dashboard-doc-name-unique-id"
                title={doc.original_filename}
              >
                {doc.original_filename}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Logout button at bottom */}
      <div className="dashboard-logout-section-unique-id" onClick={handleLogout}>
        <img
          src={LogoutIcon}
          alt="Logout Icon"
          className="dashboard-logout-icon-unique-id"
        />
        <span className="dashboard-logout-text-unique-id">Logout</span>
      </div>
    </div>
  );
}

export default Dashboard;
