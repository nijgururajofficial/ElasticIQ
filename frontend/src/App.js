import ChatWindow from './components/ChatWindow';
import SourcesPanel from './components/SourcesPanel';
import UploadModal from './components/UploadModal';
import Settings from './components/Settings';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

const queryClient = new QueryClient();

function App() {
  const [showUpload, setShowUpload] = useState(false);
  const [selectedSources, setSelectedSources] = useState([]);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 text-slate-100 flex flex-col">
        <header className="border-b border-slate-800/50 px-8 py-6 flex items-center justify-between bg-slate-900/50 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-lg">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">
                ElasticIQ Assistant
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Intelligent Document Search & Analysis
              </p>
            </div>
          </div>
          <div className="flex gap-4">
            <Settings />
            <button
              onClick={() => setShowUpload(true)}
              className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-emerald-500 to-emerald-600 text-white font-medium 
                hover:from-emerald-400 hover:to-emerald-500 transition-all duration-200 shadow-lg shadow-emerald-500/20
                active:shadow-sm active:translate-y-0.5 flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Upload
            </button>
          </div>
        </header>
        <main className="flex flex-1 overflow-hidden">
          <div className="flex-1 overflow-hidden">
            <ChatWindow onSelectSources={setSelectedSources} />
          </div>
          <aside className="w-96 border-l border-slate-800/50 bg-slate-900/50 backdrop-blur-sm overflow-y-auto">
            <SourcesPanel sources={selectedSources} />
          </aside>
        </main>
        <UploadModal open={showUpload} onClose={() => setShowUpload(false)} />
      </div>
    </QueryClientProvider>
  );
}

export default App;