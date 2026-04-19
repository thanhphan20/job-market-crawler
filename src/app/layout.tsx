import type { Metadata } from "next";
import { Geist_Mono } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Job Market Intelligence Terminal",
  description: "High-performance job market analytics & AI impact correlation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistMono.variable} font-mono overflow-x-hidden`}>
        <div className="flex min-h-screen bg-background">
          {/* Main Content Area */}
          <main className="flex-1 border-l border-border px-8 py-10">
            {/* Terminal Header */}
            <header className="mb-12 flex items-end justify-between border-b border-border pb-6">
              <div>
                <h1 className="text-4xl font-black uppercase tracking-tighter text-foreground">
                  Intelligence <span className="text-accent">Terminal</span>
                </h1>
                <p className="terminal-label mt-2">Correlating ITViec + Kaggle + SO Global Trends</p>
              </div>
              <div className="flex flex-col items-end gap-1 font-mono text-[10px] text-accent/50 uppercase">
                <span>Status: Fully Operational</span>
                <span>Version: 2.0.0-PRO</span>
                <span>Target: VN_MARKET_AI_IMPACT</span>
              </div>
            </header>
            
            {children}
          </main>
        </div>
        <Analytics />
      </body>
    </html>
  );
}
