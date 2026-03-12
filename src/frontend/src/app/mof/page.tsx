export default function MofDashboard() {
    return (
        <div className="flex flex-col h-full space-y-6">
            <header className="flex items-center justify-between pb-4 border-b border-green-900">
                <h1 className="text-3xl font-light tracking-tight text-white flex items-center">
                    <span className="w-3 h-3 bg-green-500 rounded-full mr-4"></span>
                    Ministry of <span className="font-semibold text-green-100 ml-2">Finance</span>
                </h1>
                <div className="text-sm bg-slate-900 px-3 py-1 rounded border border-slate-700 font-mono text-slate-400">
                    ECONOMIC VIEW MODE
                </div>
            </header>

            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-lgflex items-center justify-center text-slate-500 font-mono text-sm p-4 text-center">
                [MoF Dashboard Loaded] <br />
                Visualizing supply chain dependencies, FDI anomalies, and critical resource chokepoints.
            </div>
        </div>
    );
}
