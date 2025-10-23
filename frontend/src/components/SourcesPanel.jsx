export default function SourcesPanel({ sources }) {
  if (!sources || sources.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-800/50 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="text-sm text-slate-400">
          Retrieved sources will appear here after a query.
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
          Sources
        </h2>
        <span className="text-xs text-slate-400 bg-slate-800/50 px-2 py-1 rounded-full">
          {sources.length} results
        </span>
      </div>
      <ul className="space-y-4">
        {sources.map((source, index) => (
          <li 
            key={source.chunk_id || index} 
            className="rounded-xl border border-slate-800/50 bg-slate-900/30 p-4 backdrop-blur-sm
              hover:bg-slate-800/30 transition-colors duration-200"
          >
            <div className="flex items-center justify-between text-sm">
              <h3 className="font-medium text-slate-200">
                {source.title || 'Untitled'}
              </h3>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 bg-slate-800/50 px-2 py-1 rounded-full font-mono">
                  {source.chunk_id?.split('_')[1] || 'chunk'}
                </span>
              </div>
            </div>
            <p className="mt-2 text-sm text-slate-400 line-clamp-3">
              {source.text}
            </p>
            <div className="mt-3 flex items-center gap-3">
              {source.metadata?.url && (
                <a
                  href={source.metadata.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300
                    transition-colors duration-200"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  Open source
                </a>
              )}
              <button 
                className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-300
                  transition-colors duration-200"
                onClick={() => {
                  const text = source.text;
                  navigator.clipboard.writeText(text);
                }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
                </svg>
                Copy text
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}