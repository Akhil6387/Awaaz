import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { BookmarkCheck, Clock, ArrowRight, ShieldCheck, PlusCircle } from 'lucide-react';
import { useSession } from '../context/SessionContext';
import { fetchComplaints } from '../services/api';

export default function MyComplaintsPage({ onSelectComplaint, onNavigateNew }) {
  const { t } = useTranslation();
  const { sessionId, myComplaints, myCoSigns } = useSession();
  const [liveFiledList, setLiveFiledList] = useState([]);
  const [liveCoSignedList, setLiveCoSignedList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (sessionId) {
      setLoading(true);
      fetchComplaints({ my_session_id: sessionId })
        .then(data => setLiveFiledList(data))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [sessionId]);

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      
      {/* Header */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-2">
        <div className="flex items-center gap-2.5 text-emerald-600">
          <BookmarkCheck className="w-6 h-6" />
          <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900">
            {t('nav.my_complaints')}
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
          No account needed! Your filed complaints and co-signed issues are securely tracked in your local browser session.
        </p>
      </div>

      {/* Filed Complaints List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-base text-slate-900">
            Complaints Filed by You ({liveFiledList.length})
          </h3>
          <button
            onClick={onNavigateNew}
            className="text-xs font-bold text-saffron-600 hover:underline flex items-center gap-1"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            File New Issue
          </button>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs text-slate-400">Loading your issues...</div>
        ) : liveFiledList.length === 0 ? (
          <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs text-slate-500 space-y-2">
            <p>You haven't filed any complaints from this browser yet.</p>
            <button
              onClick={onNavigateNew}
              className="px-4 py-2 bg-saffron-600 text-white font-bold rounded-xl text-xs shadow"
            >
              Report a Civic Grievance
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {liveFiledList.map((c) => (
              <div 
                key={c.id} 
                onClick={() => onSelectComplaint(c.id)}
                className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 hover:border-saffron-400 shadow-sm flex items-center justify-between gap-4 cursor-pointer transition-all"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="font-mono font-bold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">
                      {c.public_id}
                    </span>
                    <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px]">
                      {c.status_display || c.status}
                    </span>
                  </div>
                  <h4 className="font-bold text-sm text-slate-900 line-clamp-1">{c.title}</h4>
                  <p className="text-xs text-slate-500">📍 {c.sub_location} • {c.co_sign_count} Co-signed</p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 flex-shrink-0" />
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
