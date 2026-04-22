import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET() {
  try {
    const intelligence = await prisma.globalIntelligence.findMany();
    const trends = await prisma.salaryTrend.findMany({
      where: { source: "Kaggle" },
      orderBy: { year: 'asc' }
    });
    const impact = await prisma.aIImpactMatrix.findMany();

    // Map DB entities to UI schema
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
    return NextResponse.json({ error: "Failed to fetch cloud data" }, { status: 500 });
  }
}
