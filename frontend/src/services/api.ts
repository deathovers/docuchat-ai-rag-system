import axios from 'axios';

const API_BASE = 'http://localhost:8000/v1';

export const uploadFiles = async (files: File[], sessionId: string) => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  formData.append('session_id', sessionId);

  const response = await axios.post(`${API_BASE}/upload`, formData);
  return response.data;
};

export const chatWithAi = async (query: string, sessionId: string, history: any[]) => {
  const response = await axios.post(`${API_BASE}/chat`, {
    query,
    session_id: sessionId,
    history: history.map(m => ({ role: m.role, content: m.content }))
  });
  return response.data;
};
