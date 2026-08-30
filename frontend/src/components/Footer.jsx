import React from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldCheck, Lock, Landmark, FileText, CheckCircle2 } from 'lucide-react';

export default function Footer({ setActiveTab }) {
  const { t } = useTranslation();

  return (
    <footer className="bg-slate-900 text-slate-300 pt-12 pb-8 border-t border-slate-800 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-10 border-b border-slate-800">
          
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-black text-white tracking-tight">आवाज़</span>
              <span className="text-sm font-bold text-saffron-500 uppercase tracking-widest">Awaaz</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              No-login civic complaint and evidence infrastructure. Sits on top of Nagar Nigam 311 and Panchayat grievance portals as an open public accountability layer.
            </p>
            <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium pt-1">
              <Lock className="w-3.5 h-3.5" />
              <span>100% Anonymous & Zero-Auth</span>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider text-xs">Evidentiary Integrity</h4>
            <ul className="space-y-2 text-slate-400">
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-saffron-500 mt-0.5 flex-shrink-0" />
                <span>Live camera capture only (Gallery uploads blocked)</span>
              </li>
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-saffron-500 mt-0.5 flex-shrink-0" />
                <span>Server-stamped SHA-256 hash & immutable GPS metadata</span>
              </li>
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-saffron-500 mt-0.5 flex-shrink-0" />
                <span>Transparent public audit timeline on all status updates</span>
              </li>
            </ul>
          </div>

          <div className="space-y-2 text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider text-xs">Rural & Urban Parity</h4>
            <p className="text-slate-400 leading-relaxed">
              Built for Gram Panchayats (Sarpanch/Panch) and Urban Municipalities (Ward Corporator/Mayor) equally. Config-driven authority directories that evolve without code changes.
            </p>
            <div className="flex gap-2 pt-1">
              <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[11px]">Gram Panchayat</span>
              <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[11px]">Nagar Nigam</span>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider text-xs">Escalation & RTI</h4>
            <p className="text-slate-400 leading-relaxed">
              Auto-generate formal RTI dossiers and grievance petitions when community corroboration crosses threshold pressure points.
            </p>
            <div className="pt-1">
              <button
                onClick={() => setActiveTab('about')}
                className="text-saffron-400 hover:text-saffron-300 underline text-xs font-semibold"
              >
                Read Moderation & Defamation Policy →
              </button>
            </div>
          </div>

        </div>

        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
          <p>© 2026 Awaaz Civic Accountability Initiative. Open & Citizen-Led.</p>
          <div className="flex gap-4">
            <span>Server-side SHA-256 Tamper-Evidence</span>
            <span>•</span>
            <span>Panchayat & Nagar Nigam Bridge</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
