import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
export async function GET(req: NextRequest) {
  try {
    const reportDir = path.join(process.cwd(), "analytics/reports");
    
    if (!fs.existsSync(reportDir)) {
      return NextResponse.json({ error: "Report directory not found" }, { status: 404 });
    }

    const files = fs.readdirSync(reportDir).filter(f => f.startsWith("market_intelligence_") && f.endsWith(".md"));
    
    if (files.length === 0) {
      return NextResponse.json({ error: "No reports found" }, { status: 404 });
    }

    // Get the latest one
    const latestReport = files.sort().reverse()[0];
    const content = fs.readFileSync(path.join(reportDir, latestReport), "utf-8");

    return NextResponse.json({ 
      filename: latestReport,
      content: content 
    });
  } catch (err) {
    return NextResponse.json({ error: "Failed to read report" }, { status: 500 });
  }
}
