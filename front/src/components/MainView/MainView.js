import React, { useState } from 'react';
import Dashboard from '../Dashboard/Dashboard';
import Uploader from '../Uploader/Uploader';
import DocumentDetail from '../DocumentDetail/DocumentDetail';
import './MainView.css';

function MainView() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [selectedDocId, setSelectedDocId] = useState(null);

  // Called after a successful file upload
  const handleUploadSuccess = () => {
    // Trigger Dashboard to refetch
    setRefreshKey(prev => prev + 1);
  };

  // Called when user clicks a document in the sidebar
  const handleDocumentSelect = (docId) => {
    setSelectedDocId(docId);
  };

  // Function to return to the uploader
  const handleReturnToUploader = () => {
    setSelectedDocId(null); // Reset selected document
  };

  return (
    <div className="main-view-container-unique-id">
      {/* Sidebar */}
      <Dashboard
        refreshTrigger={refreshKey}
        onDocumentSelect={handleDocumentSelect}
        onReturnToUploader={handleReturnToUploader} // Pass function
      />

      {/* Center area: show either Uploader or DocumentDetail */}
      {selectedDocId ? (
        <DocumentDetail docId={selectedDocId} />
      ) : (
        <Uploader onUploadSuccess={handleUploadSuccess} />
      )}
    </div>
  );
}

export default MainView;
