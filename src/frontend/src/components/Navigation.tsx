// Basic Navigation layout for Next.js (Sidebar)
import Link from 'next/link';

export default function Navigation() {
    return (
        <nav className="fixed w-64 h-full bg-slate-900 text-white flex flex-col p-4 border-r border-slate-700">
            <div className="text-xl font-bold mb-8 tracking-wider text-slate-200 uppercase">
                Ontology Engine
            </div>

            <div className="flex flex-col space-y-4">
                <Link href="/" className="hover:bg-slate-800 p-2 rounded transition-colors duration-200 font-medium tracking-wide">
                    Intelligence Dashboard
                </Link>

                <div className="pt-4 pb-2 text-xs font-semibold text-slate-500 uppercase tracking-widest">
                    Ministry Views
                </div>

                <Link href="/mod" className="hover:bg-slate-800 p-2 rounded transition-colors duration-200 text-sm flex items-center">
                    <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>
                    Ministry of Defence (MoD)
                </Link>
                <Link href="/mea" className="hover:bg-slate-800 p-2 rounded transition-colors duration-200 text-sm flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                    Ministry of Ext. Affairs (MEA)
                </Link>
                <Link href="/mof" className="hover:bg-slate-800 p-2 rounded transition-colors duration-200 text-sm flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                    Ministry of Finance (MoF)
                </Link>
            </div>

            <div className="mt-auto pt-4 border-t border-slate-700 text-xs text-slate-500">
                System Status: <span className="text-green-400 font-mono">ONLINE</span>
            </div>
        </nav>
    );
}
