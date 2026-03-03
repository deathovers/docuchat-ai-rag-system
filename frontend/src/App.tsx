import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [sessionId, setSessionId] = useState<string>('');
  const [documents, setDocuments] = useState<string[]>([]);

  useEffect(() => {
    const id = localStorage.getItem('docuchat_session') || uuidv4();
    localStorage.setItem('docuchat_session', id);
    setSessionId(id);
  }, []);

  const handleUploadSuccess = (newFiles: string[]) => {
    setDocuments(prev => [...new Set([...prev, ...newFiles])]);
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <Sidebar 
        sessionId={sessionId} 
        documents={documents} 
        onUploadSuccess={handleUploadSuccess} 
      />
      <main className="flex-1 flex flex-col">
        <Chat sessionId={sessionId} />
      </main>
    </div>
  );
}

export default App;
