import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV === "development") {
      return [
        {
          source: "/api/sync/:path*",
          destination: "http://localhost:8000/api/sync/:path*",
        },
        {
          source: "/api/sync",
          destination: "http://localhost:8000/api/sync",
        },
        {
          source: "/api/market-data",
          destination: "http://localhost:8000/api/market-data",
        },
        {
          source: "/api/python-health",
          destination: "http://localhost:8000/api/python-health",
        },
        {
          source: "/api/kaggle-data",
          destination: "http://localhost:8000/api/kaggle-data",
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
