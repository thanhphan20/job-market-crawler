'use client';

import { useState, useRef, useEffect } from 'react';

export default function SyncTerminal() {
  const [logs, setLogs] = useState<string[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const [showReport, setShowReport] = useState(false);
  const [reportContent, setReportContent] = useState('');

  const runCommand = async (command: string, args: string[] = []) => {
    setIsSyncing(true);
    setLogs(prev => [...prev, `[SYSTEM] Preparing command: python main.py ${command} ${args.join(' ')}`]);
    
    try {
      let endpoint = '/api/sync';
      if (command === '--itviec') endpoint = '/api/sync/itviec';
      if (command === '--extract') endpoint = '/api/sync/extract';

      setLogs(prev => [...prev, `[SYSTEM] Requesting ${endpoint}...`]);
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error(`Server returned ${response.status}`);
      
      const data = await response.json();
      setLogs(prev => [...prev, `[SYSTEM] ${data.message}`]);
      setLogs(prev => [...prev, '[SUCCESS] Task queued in background.']);
      
      window.dispatchEvent(new CustomEvent('intel-sync-complete'));
    } catch (err: any) {
      setLogs(prev => [...prev, `[ERROR] Sync failed: ${err.message}`]);
      setLogs(prev => [...prev, '[HINT] Make sure the FastAPI server is running at localhost:8000 if testing locally.']);
    } finally {
      setIsSyncing(false);
    }
  };

  const fetchReport = async () => {
    const res = await fetch('/api/report');
    const data = await res.json();
    if (data.content) {
      setReportContent(data.content);
      setShowReport(true);
    }
  };

  const renderMarkdown = (content: string) => {
    // Basic regex to find ![alt](filename) and convert to <img> with the proxy URL
    const parts = content.split(/(!\[.*?\]\(.*?\))/g);
    
    return parts.map((part, index) => {
      const match = part.match(/!\[(.*?)\]\((.*?)\)/);
      if (match) {
        const alt = match[1];
        const filename = match[2];
        return (
          <div key={index} className="my-6 border border-zinc-800 p-1 bg-black">
            <img 
              src={`/api/report/image/${filename}`} 
              alt={alt} 
              className="w-full h-auto grayscale hover:grayscale-0 transition-all duration-500"
            />
            <p className="text-[8px] text-zinc-600 mt-2 text-center uppercase tracking-widest">{alt}</p>
          </div>
        );
      }
      return <span key={index} className="whitespace-pre-wrap">{part}</span>;
    });
  };

  return (
    <div className="space-y-4">
      {showReport && (
        <div className="fixed inset-0 bg-black/95 backdrop-blur-xl z-50 p-6 md:p-10 flex flex-col animate-in fade-in zoom-in-95">
          <div className="flex justify-between items-center mb-6 max-w-4xl mx-auto w-full">
            <h2 className="terminal-label text-accent tracking-widest uppercase">Strategy_Analysis_v6.1.md</h2>
            <button onClick={() => setShowReport(false)} className="text-zinc-500 hover:text-white uppercase text-[10px] tracking-widest border border-zinc-800 px-3 py-1 bg-black">Close [Esc]</button>
          </div>
          <div className="flex-1 overflow-y-auto font-mono text-[11px] leading-relaxed text-zinc-400 p-8 border border-zinc-800 bg-zinc-900/10 selection:bg-accent selection:text-black shadow-2xl max-w-4xl mx-auto w-full no-scrollbar">
            {renderMarkdown(reportContent)}
          </div>
        </div>
      )}

      <div className="flex flex-col gap-4">
        <div className="flex justify-between items-center">
          <h3 className="terminal-label">Intelligence Sync Engine</h3>
          <span className={`text-[8px] font-mono ${isSyncing ? 'text-accent animate-pulse' : 'text-zinc-600'}`}>
            {isSyncing ? 'ENGINE_ACTIVE' : 'ENGINE_STANDBY'}
          </span>
        </div>
        
        <div className="grid grid-cols-4 gap-2">
            <>
              <button 
                onClick={() => runCommand('--itviec', ['--limit', '10'])} 
                disabled={isSyncing || !!process.env.NEXT_PUBLIC_VERCEL_ENV}
                className={`terminal-button text-[9px] py-1 h-auto ${process.env.NEXT_PUBLIC_VERCEL_ENV ? 'opacity-30' : ''}`}
              >
                {process.env.NEXT_PUBLIC_VERCEL_ENV ? '🚫 Local Crawl' : '🕷️ Crawl'}
              </button>
              <button 
                onClick={() => runCommand('--flow')} 
                disabled={isSyncing}
                className="terminal-button text-[9px] py-1 h-auto bg-accent/20 border-accent/50 text-accent"
              >
                🧠 Intelligence [FastAPI]
              </button>
            </>
          <button 
            onClick={fetchReport} 
            disabled={isSyncing}
            className="terminal-button text-[9px] py-1 h-auto border-blue-500/50 text-blue-400"
          >
            📋 View Report
          </button>
          <button 
            onClick={() => setLogs([])} 
            disabled={isSyncing}
            className="terminal-button text-[9px] py-1 h-auto border-zinc-700 text-zinc-500"
          >
            🧹 Clear Console
          </button>
        </div>
      </div>

      <div 
        ref={terminalRef}
        className="h-48 w-full bg-black border border-border p-4 font-mono text-[10px] overflow-y-auto no-scrollbar selection:bg-accent selection:text-black shadow-inner"
      >
        {logs.length === 0 ? (
          <p className="text-zinc-700 animate-pulse">READY_FOR_COMMAND...</p>
        ) : (
          <div className="space-y-1">
            {logs.map((log, i) => (
              <p key={i} className={
                log.startsWith('[ERR]') || log.startsWith('[ERROR]') ? 'text-red-500' : 
                log.startsWith('[SUCCESS]') || log.includes('SUCCESS') ? 'text-accent' : 
                log.includes('[PROCESS_COMPLETED]') ? 'text-zinc-500 italic' :
                'text-zinc-400'
              }>
                <span className="text-zinc-600 mr-2">[{new Date().toLocaleTimeString([], { hour12: false })}]</span>
                {log}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
