import { prisma } from "./db";
import { unstable_cache } from "next/cache";

export const getCachedIntelligence = unstable_cache(
  async () => {
    return prisma.globalIntelligence.findMany({ 
      orderBy: { demand: 'desc' } 
    });
  },
  ["global-intelligence"],
  { revalidate: 3600, tags: ["intelligence"] }
);

export const getCachedTrends = unstable_cache(
  async () => {
    return prisma.salaryTrend.findMany({ 
      orderBy: { year: 'asc' } 
    });
  },
  ["salary-trends"],
  { revalidate: 3600, tags: ["intelligence"] }
);

export const getCachedImpact = unstable_cache(
  async () => {
    return prisma.aIImpactMatrix.findMany();
  },
  ["ai-impact"],
  { revalidate: 3600, tags: ["intelligence"] }
);
