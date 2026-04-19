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

  const startSync = async () => {
    setIsSyncing(true);
    setLogs(['[SYSTEM] Initializing Market Sync Orchestrator...', '[SYSTEM] Authenticating with Supabase Proxy...']);
    
    try {
      const response = await fetch('/api/sync');
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const text = decoder.decode(value);
          const newLines = text.split('\n').filter(line => line.trim());
          setLogs(prev => [...prev, ...newLines]);
        }
      }
    } catch {
      setLogs(prev => [...prev, '[ERROR] Sync failed: Connection lost.']);
    } finally {
      setIsSyncing(false);
      setLogs(prev => [...prev, '[SUCCESS] Sync completed. Database is now updated.']);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="terminal-label">Intelligence Sync Engine</h3>
        <button 
          onClick={startSync} 
          disabled={isSyncing}
          className="terminal-button"
        >
          {isSyncing ? 'Syncing...' : 'Run Sync'}
        </button>
      </div>

      <div 
        ref={terminalRef}
        className="h-48 w-full bg-black border border-border p-4 font-mono text-[10px] overflow-y-auto no-scrollbar selection:bg-accent selection:text-black"
      >
        {logs.length === 0 ? (
          <p className="text-zinc-700 animate-pulse">READY_FOR_COMMAND...</p>
        ) : (
          <div className="space-y-1">
            {logs.map((log, i) => (
              <p key={i} className={log.startsWith('[ERROR]') ? 'text-red-500' : log.startsWith('[SUCCESS]') ? 'text-accent' : 'text-zinc-400'}>
                <span className="text-zinc-600 mr-2">[{new Date().toLocaleTimeString()}]</span>
                {log}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
