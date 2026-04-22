import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET() {
  try {
    const intelligence = await prisma.globalIntelligence.findMany();
    
    // Fallback to local JSON if DB is empty or fails
    if (!intelligence || intelligence.length === 0) {
      console.log("[API] DB empty, falling back to static JSON...");
      return fetchStaticFallback();
    }

    const trends = await prisma.salaryTrend.findMany({
      where: { source: "Kaggle" },
      orderBy: { year: 'asc' }
    });
    const impact = await prisma.aIImpactMatrix.findMany();

    return NextResponse.json({
      intelligence: intelligence.map(i => ({
        tech: i.tech,
        demand: i.demand,
        globalAvgSalary: i.globalAvgSalary,
        localAvgSalary: i.localAvgSalary,
        resilienceScore: i.resilienceScore,
        riskLevel: i.riskLevel
      })),
      trends: trends.map(t => ({
        year: t.year,
        avgSalary: t.avgSalary
      })),
      impact: impact.map(im => ({
        industry: im.industry,
        status: im.status,
        automationRisk: im.automationRisk
      })),
      updated_at: intelligence[0]?.updatedAt || new Date().toISOString()
    });
  } catch (error) {
    console.error("[API_ERR] Database fetch failed:", error);
    return fetchStaticFallback();
  }
}

async function fetchStaticFallback() {
  try {
    const fs = require('fs');
    const path = require('path');
    const filePath = path.join(process.cwd(), 'public/data/intelligence.json');
    if (fs.existsSync(filePath)) {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      return NextResponse.json(data);
    }
  } catch (e) {
    console.error("[API_ERR] Static fallback failed:", e);
  }
  return NextResponse.json({ error: "Data unavailable" }, { status: 500 });
}
