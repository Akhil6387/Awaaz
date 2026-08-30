import React from 'react';
import { useTranslation } from 'react-i18next';
import { History, ShieldCheck, CheckCircle2, ArrowRight, UserCheck, AlertTriangle } from 'lucide-react';

export default function StatusAuditTimeline({ auditTrail = [] }) {
  const { t } = useTranslation();

  if (!auditTrail || auditTrail.length === 0) {
    return (
      <div className="p-4 text-xs text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
        No audit entries recorded yet.
      </div>
    );
  }

  const getActorBadgeColor = (actorType) => {
    switch (actorType) {
      case 'AUTHORITY': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'MODERATOR': return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'CITIZEN': return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      default: return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 pb-2 border-b border-slate-200">
        <History className="w-4 h-4 text-saffron-600" />
        <h4 className="font-bold text-sm text-slate-900">
          {t('detail.audit_trail')}
        </h4>
        <span className="text-[11px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full font-medium">
          Tamper-Evident Chronological Record
        </span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {auditTrail.map((log, idx) => (
          <div key={log.id || idx} className="relative group">
            {/* Timeline node */}
            <div className="absolute -left-6 top-1 w-4 h-4 rounded-full bg-white border-2 border-saffron-600 flex items-center justify-center group-hover:scale-125 transition-transform shadow-sm">
              <div className="w-1.5 h-1.5 rounded-full bg-saffron-600"></div>
            </div>

            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-1.5">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex items-center gap-1.5">
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${getActorBadgeColor(log.actor_type)}`}>
                    {log.actor_type}
                  </span>
                  <span className="font-bold text-slate-800">
                    {log.actor_label}
                  </span>
                </div>

                <span className="text-[11px] text-slate-400 font-mono">
                  {new Date(log.created_at).toLocaleString('en-IN', {
                    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
                  })}
                </span>
              </div>

              {log.from_status && (
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700">
                  <span className="text-slate-500">{log.from_status}</span>
                  <ArrowRight className="w-3 h-3 text-slate-400" />
                  <span className="text-saffron-600">{log.to_status}</span>
                </div>
              )}

              <p className="text-xs text-slate-600 leading-relaxed">
                {log.notes}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
