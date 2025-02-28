import React, { useState } from 'react';
import Dashboard from '../Dashboard/Dashboard';
import Uploader from '../Uploader/Uploader';
import './MainView.css';

function MainView() {
  // This counter will trigger a refresh in Dashboard when updated.
  const [refreshKey, setRefreshKey] = useState(0);

  // Callback passed to Uploader to call when a file is uploaded successfully.
  const handleUploadSuccess = () => {
    setRefreshKey(prevKey => prevKey + 1);
  };

  return (
    <div className="main-view-container-unique-id">
      {/* Dashboard receives the refresh key as a prop */}
      <Dashboard refreshTrigger={refreshKey} />
      {/* Uploader gets the callback to trigger a refresh */}
      <Uploader onUploadSuccess={handleUploadSuccess} />
    </div>
  );
}

export default MainView;
