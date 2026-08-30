import React from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldCheck, Lock, Landmark, CheckCircle2, FileText, Scale } from 'lucide-react';

export default function AboutPage() {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-20">
      
      {/* Title */}
      <div className="bg-white p-6 sm:p-10 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-saffron-100 text-saffron-800 text-xs font-bold">
          Awaaz Civic Manifesto
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Trustworthy Evidence Layer for Indian Citizens
        </h1>
        <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
          Awaaz does not replace official channels like CM Helpline (181) or Nagar Nigam 311. It acts as an open, public accountability infrastructure sitting on top of them.
        </p>
      </div>

      {/* Core Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-base text-slate-900">100% No-Login Required</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Fear of retribution from local powerful figures prevents citizens from reporting. Awaaz ensures zero-auth anonymous tracking by default.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-saffron-100 text-saffron-800 flex items-center justify-center font-bold">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-base text-slate-900">Live Camera Proof Only</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Gallery uploads are disabled to prevent fake news. All media is captured directly from in-browser camera and stamped with SHA-256 hashes.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-800 flex items-center justify-center font-bold">
            <Landmark className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-base text-slate-900">Village & City Parity</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Gram Panchayats (Sarpanch/Sachiv) and Municipal Wards (Corporator/Zone Engineer) are treated as equal first-class citizens.
          </p>
        </div>

      </div>

      {/* Moderation & Legal Policy */}
      <div className="bg-slate-900 text-white p-6 sm:p-8 rounded-3xl shadow-sm space-y-4">
        <div className="flex items-center gap-2 text-saffron-400">
          <Scale className="w-6 h-6" />
          <h3 className="text-lg font-bold">Moderation & Legal Safety Policy</h3>
        </div>

        <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
          <p>
            • <strong>No Unverified Defamation:</strong> Grievances must focus on physical infrastructure and official duties. Personal abuse or unverified claims against individuals are quarantined.
          </p>
          <p>
            • <strong>Official Conduct Stricter Review:</strong> Complaints regarding bribes or official misconduct undergo stricter corroboration thresholds before public display.
          </p>
          <p>
            • <strong>Evidentiary Usability:</strong> All timestamps and hashes comply with standard digital evidence protocols for submission to Press, RTI petitions, or High Court PILs.
          </p>
        </div>
      </div>

    </div>
  );
}
