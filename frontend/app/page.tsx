"use client";

import { useState } from 'react';
import axios from 'axios';
import { Upload, Send, FileText, Loader2 } from 'lucide-react';

const API_BASE = "http://localhost:8000/v1";

export default function Home() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<{role: string, content: string, sources?: any[]}[]>([]);

  const handleUpload = async () => {
    if (!files) return;
    setLoading(true);
    const formData = new FormData();
    Array.from(files).forEach(file => formData.append('files', file));

    try {
      const res = await axios.post(`${API_BASE}/upload`, formData);
      setSessionId(res.data.session_id);
      setChatHistory([{ role: 'assistant', content: 'Documents uploaded successfully! How can I help you today?' }]);
    } catch (err) {
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message || !sessionId) return;

    const userMsg = message;
    setMessage("");
    setChatHistory(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        message: userMsg,
        session_id: sessionId
      });
      setChatHistory(prev => [...prev, { role: 'assistant', content: res.data.answer, sources: res.data.sources }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', content: "Sorry, something went wrong." }]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <main className="flex flex-col h-screen bg-gray-50">
      <header className="bg-white border-b p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <FileText className="text-blue-600" /> DocuChat AI
        </h1>
        {!sessionId ? (
          <div className="flex gap-2 items-center">
            <input 
              type="file" 
              multiple 
              accept=".pdf" 
              onChange={(e) => setFiles(e.target.files)}
              className="text-sm"
            />
            <button 
              onClick={handleUpload}
              disabled={loading || !files}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
              Upload
            </button>
          </div>
        ) : (
          <span className="text-sm text-green-600 font-medium">Session Active</span>
        )}
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatHistory.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border'}`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t text-xs opacity-70">
                  Sources: {msg.sources.map(s => `${s.file_name} (p.${s.page})`).join(', ')}
                </div>
              )}
            </div>
          </div>
        ))}
        {chatLoading && (
          <div className="flex justify-start">
            <div className="bg-white border p-3 rounded-lg">
              <Loader2 className="animate-spin text-blue-600" />
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleChat} className="p-4 bg-white border-t flex gap-2">
        <input 
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={sessionId ? "Ask a question about your documents..." : "Upload documents to start chatting"}
          disabled={!sessionId || chatLoading}
          className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button 
          type="submit"
          disabled={!sessionId || chatLoading}
          className="bg-blue-600 text-white p-2 rounded-lg disabled:opacity-50"
        >
          <Send size={20} />
        </button>
      </form>
    </main>
  );
}
