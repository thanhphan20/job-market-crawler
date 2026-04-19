import { spawn } from 'child_process';
import { NextRequest } from 'next/server';
import path from 'path';

export async function GET(req: NextRequest) {
  const encoder = new TextEncoder();
  const pythonPath = process.env.PYTHON_EXECUTABLE || 'python3';
  
  const stream = new ReadableStream({
    start(controller) {
      const pythonProcess = spawn(pythonPath, ['scripts/sync_intelligence.py'], {
        env: { 
          ...process.env, 
          PYTHONUNBUFFERED: '1',
          PYTHONPATH: process.cwd()
        }
      });

      pythonProcess.stdout.on('data', (data) => {
        controller.enqueue(encoder.encode(data.toString()));
      });

      pythonProcess.stderr.on('data', (data) => {
        controller.enqueue(encoder.encode(`[ERROR] ${data.toString()}`));
      });

      pythonProcess.on('close', (code) => {
        controller.enqueue(encoder.encode(`[SYSTEM] Process exited with code ${code}`));
        controller.close();
      });
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
