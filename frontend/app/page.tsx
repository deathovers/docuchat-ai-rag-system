"use client";

import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Upload, Send, FileText, Loader2, Trash2 } from 'lucide-react';

export default function DocuChat() {
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState('');
  const [files, setFiles] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let id = localStorage.getItem('docuchat_session');
    if (!id) {
      id = uuidv4();
      localStorage.setItem('docuchat_session', id);
    }
    setSessionId(id);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    setUploading(true);
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
      const res = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        setFiles(prev => [...prev, file.name]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: userMsg,
          history: messages
        }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const clearSession = async () => {
    await fetch(`http://localhost:8000/files/${sessionId}`, { method: 'DELETE' });
    setFiles([]);
    setMessages([]);
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r flex flex-col p-4">
        <h1 className="text-xl font-bold mb-6 flex items-center gap-2">
          <FileText className="text-blue-600" /> DocuChat AI
        </h1>
        
        <div className="flex-1 overflow-y-auto">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Documents</h2>
          {files.map((f, i) => (
            <div key={i} className="flex items-center gap-2 p-2 text-sm text-gray-700 bg-gray-100 rounded mb-1 truncate">
              <FileText size={14} /> {f}
            </div>
          ))}
        </div>

        <div className="mt-4 space-y-2">
          <label className="flex items-center justify-center gap-2 w-full p-2 bg-blue-600 text-white rounded cursor-pointer hover:bg-blue-700 transition">
            {uploading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
            <span>Upload PDF</span>
            <input type="file" className="hidden" accept=".pdf" onChange={handleUpload} disabled={uploading} />
          </label>
          <button 
            onClick={clearSession}
            className="flex items-center justify-center gap-2 w-full p-2 border border-red-200 text-red-600 rounded hover:bg-red-50 transition"
          >
            <Trash2 size={18} /> Clear All
          </button>
        </div>
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col">
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <FileText size={48} className="mb-4 opacity-20" />
              <p>Upload a document to start chatting</p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-3 rounded-lg ${
                m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border text-gray-800 shadow-sm'
              }`}>
                <p className="whitespace-pre-wrap text-sm">{m.content}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border p-3 rounded-lg shadow-sm">
                <Loader2 className="animate-spin text-blue-600" size={18} />
              </div>
            </div>
          )}
        </div>

        <div className="p-4 bg-white border-t">
          <div className="max-w-4xl mx-auto flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask a question about your documents..."
              className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
