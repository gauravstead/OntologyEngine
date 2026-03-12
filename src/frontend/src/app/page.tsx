"use client";

import { useStore } from "@/store/useStore";

export default function Home() {
  const { systemStatus } = useStore();

  return (
    <div className="flex flex-col h-full space-y-6">
      <header className="flex items-center justify-between pb-4 border-b border-slate-800">
        <h1 className="text-3xl font-light tracking-tight text-white">
          Executive <span className="font-semibold text-slate-300">Summary</span>
        </h1>
        <div className="text-sm bg-slate-900 px-3 py-1 rounded border border-slate-700">
          Engine: <span className="text-green-400 font-mono">{systemStatus}</span>
        </div>
      </header>

      {/* Grid Layout for Level 1 Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 flex-1">

        {/* Anomaly Feed */}
        <div className="col-span-1 lg:col-span-2 bg-slate-900 border border-slate-800 rounded-lg p-5 flex flex-col">
          <h2 className="text-lg font-medium text-slate-300 mb-4 border-b border-slate-800 pb-2">Critical Anomalies & Feed</h2>
          <div className="flex-1 overflow-y-auto space-y-4">
            <div className="bg-slate-950 p-4 border-l-4 border-red-500 rounded text-sm">
              <span className="text-red-400 font-bold mr-2">ALERT:</span>
              73% spike in negative sentiment from Nation X regarding Indian tech sector.
              <div className="text-xs text-slate-500 mt-2 font-mono">Source: GDELT Pulse • Confidence: 0.92</div>
            </div>
            <div className="bg-slate-950 p-4 border-l-4 border-yellow-500 rounded text-sm">
              <span className="text-yellow-400 font-bold mr-2">WARN:</span>
              Supply chain disruption risk increased in semi-conductor dependency chain.
              <div className="text-xs text-slate-500 mt-2 font-mono">Source: Neo4j FastRP • Confidence: 0.88</div>
            </div>
          </div>
        </div>

        {/* Risk Indices */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 flex flex-col space-y-6">
          <h2 className="text-lg font-medium text-slate-300 mb-2 border-b border-slate-800 pb-2">Strategic Watchlist</h2>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Port of Gwadar (Asset)</span>
              <span className="text-red-400 font-mono">87% RISK</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5">
              <div className="bg-red-500 h-1.5 rounded-full" style={{ width: '87%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Rare Earth Minerals (Econ)</span>
              <span className="text-yellow-400 font-mono">65% RISK</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5">
              <div className="bg-yellow-500 h-1.5 rounded-full" style={{ width: '65%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Tech Sector Investment (Econ)</span>
              <span className="text-green-400 font-mono">12% RISK</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5">
              <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '12%' }}></div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
