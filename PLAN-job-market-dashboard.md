# PLAN: Job Market Intelligence Dashboard (v2.0)

A high-performance, minimalist Next.js 16 dashboard that correlates local job market data with global Kaggle AI intelligence.

---

## 🛑 SUCCESS CRITERIA
1. **Data Bridge**: Unified Supabase schema storing both Local (ITviec) and Global (Kaggle/SO) datasets.
2. **Kaggle Intelligence Hub**: Interactive explorer for Global AI Trends (2020-2030) and Automation Risk matrices.
3. **Correlation Engine**: Real-time visualization of "Market Gaps" (Local vs Global salary benchmarks).
4. **Vercel Ready**: Automated deployment with optimized Tailwind CSS v4 bundles.

---

## 🛠 TECH STACK
- **Frontend**: Next.js 16 (App Router), Tailwind CSS v4, Framer Motion (Subtle data transitions).
- **Data Viz**: Recharts (Interactive SVG charts).
- **Database**: Supabase (PostgreSQL).
- **ORM**: Prisma (Type-safe database access).
- **Backend Bridge**: Python (Intelligence Engine + Kaggle Analyzer) + Supabase Python SDK.

---

## 📐 ARCHITECTURE & DESIGN
- **Style**: "Intelligence Terminal" (Brutalist, Sharp Edges, High Contrast).
- **Geometry**: Sharp (0px radius).
- **Palette**: Dark Mode (Background: `#060606`, Text: `#FAFAFA`, Accent: `#EAB308` [Tailwind Yellow-500]).
- **Layout**: Dynamic Viewport (Tabs for: Local Insights | Global Intelligence | AI Impact).

---

## 📁 FILE STRUCTURE
```plaintext
job-market-crawler/
├── app/                      # Next.js App Router
│   ├── (dashboard)/          # Dashboard Route Group
│   │   ├── local/            # ITviec Analysis
│   │   ├── global/           # Kaggle Intelligence Hub
│   │   └── impact/           # AI Automation Risk Matrix
│   ├── layout.tsx
│   └── page.tsx              # Combined Overview
├── components/               # UI Components
│   ├── charts/               # Recharts wrappers
│   ├── intelligence/         # Kaggle-specific components
│   └── ui/                   # Primitive Tailwind components
├── prisma/                   # Database Schema
├── scripts/                  # Data Bridge Scripts
│   └── sync_intelligence.py  # Unified Local + Kaggle Sync
└── main.py                   # Existing Orchestrator
```

---

## 🏃 TASK BREAKDOWN

### Phase 1: Foundation (Infrastructure)
| Task ID | Name | Agent | Skill | Priority | Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T1.1 | Initialize Next.js 16 + Tailwind CSS v4 | `frontend-specialist` | `app-builder` | P0 | None |
| T1.2 | Design Unified Supabase Schema (Local + Global) | `database-architect` | `prisma-expert` | P0 | None |
| T1.3 | Configure Prisma Client for Multi-source Data | `backend-specialist` | `nodejs-best-practices` | P0 | T1.2 |

### Phase 2: Intelligence Bridge (Python -> DB)
| Task ID | Name | Agent | Skill | Priority | Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T2.1 | Update `KaggleMarketAnalyzer` for DB Export | `backend-specialist` | `python-patterns` | P1 | T1.2 |
| T2.2 | Create `sync_intelligence.py` for Daily Refresh | `backend-specialist` | `python-patterns` | P1 | T2.1 |
| T2.3 | Seed DB with ITviec + Kaggle + SO Snapshots | `database-architect` | `database-design` | P1 | T2.2 |

### Phase 3: Interactive Intelligence Hub (Next.js)
| Task ID | Name | Agent | Skill | Priority | Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T3.1 | Build Local Market Insight Dashboard | `frontend-specialist` | `react-best-practices` | P2 | T1.3 |
| T3.2 | Implement Kaggle Global Intelligence Explorer | `frontend-specialist` | `react-best-practices` | P2 | T1.3 |
| T3.3 | Create AI Impact & Resilience Matrix View | `frontend-specialist` | `react-best-practices` | P2 | T3.2 |
| T3.4 | Add Local vs Global "Market Gap" Comparison | `frontend-specialist` | `react-best-practices` | P2 | T3.3 |

### Phase 4: Verification & Deploy
| Task ID | Name | Agent | Skill | Priority | Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T4.1 | Performance Audit (Tailwind Bundle + Hydration) | `performance-optimizer` | `performance-profiling` | P3 | All T3 |
| T4.2 | Configure Vercel Deployment & DB Secrets | `devops-engineer` | `deployment-procedures` | P3 | T4.1 |

---

## ✅ PHASE X: VERIFICATION
- [ ] No purple/violet hex codes (`#EAB308` Yellow used).
- [ ] Next.js 16 features (Server Actions, `next/form`) utilized.
- [ ] Correlation between ITviec and Kaggle data is visible.
- [ ] AI Impact scoring reflects `IntelligenceEngine` logic.
- [ ] `python .agent/scripts/verify_all.py .` passes.
