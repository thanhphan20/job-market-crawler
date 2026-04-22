import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";

export async function POST(req: NextRequest) {
  const { command, args = [] } = await req.json();

  if (!["--flow", "--itviec", "--extract"].includes(command)) {
    return NextResponse.json({ error: "Invalid command" }, { status: 400 });
  }

  const stream = new ReadableStream({
    start(controller) {
      console.log(`[*] Spawning python3 main.py ${command} ${args.join(" ")}`);
      
      const process = spawn("python3", ["main.py", command, ...args]);

      process.stdout.on("data", (data) => {
        controller.enqueue(data.toString());
      });

      process.stderr.on("data", (data) => {
        controller.enqueue(`[ERR] ${data.toString()}`);
      });

      process.on("close", (code) => {
        controller.enqueue(`\n[PROCESS_COMPLETED] with code ${code}\n`);
        controller.close();
      });

      process.on("error", (err) => {
        controller.enqueue(`[SYSTEM_ERR] ${err.message}\n`);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Transfer-Encoding": "chunked",
    },
  });
}
