import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import { uploadFiles } from '../services/api';

interface SidebarProps {
  sessionId: string;
  documents: string[];
  onUploadSuccess: (files: string[]) => void;
}

const Sidebar = ({ sessionId, documents, onUploadSuccess }: SidebarProps) => {
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    
    setIsUploading(true);
    try {
      const files = Array.from(e.target.files);
      const result = await uploadFiles(files, sessionId);
      onUploadSuccess(result.files);
    } catch (error) {
      console.error("Upload failed", error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-72 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <FileText className="text-blue-500" /> DocuChat AI
        </h1>
      </div>

      <div className="p-4 flex-1 overflow-y-auto">
        <div className="mb-6">
          <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              {isUploading ? (
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              ) : (
                <>
                  <Upload className="w-8 h-8 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-400">Upload PDFs</p>
                </>
              )}
            </div>
            <input type="file" className="hidden" multiple accept=".pdf" onChange={handleFileChange} disabled={isUploading} />
          </label>
        </div>

        <div className="space-y-2">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Documents</h2>
          {documents.map((doc, i) => (
            <div key={i} className="flex items-center gap-2 p-2 bg-gray-700/50 rounded text-sm">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span className="truncate">{doc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
