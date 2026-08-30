import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldCheck, Check, X, AlertTriangle, MessageSquare, ExternalLink } from 'lucide-react';
import { fetchModerationQueue, reviewModerationComplaint } from '../services/api';

export default function ModerationPortalPage({ onSelectComplaint }) {
  const { t } = useTranslation();
  const [tab, setTab] = useState('PENDING'); // 'PENDING', 'FLAGGED'
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [moderatorNotes, setModeratorNotes] = useState({});

  const loadQueue = () => {
    setLoading(true);
    fetchModerationQueue(tab)
      .then(data => setQueue(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQueue();
  }, [tab]);

  const handleAction = async (complaintId, action) => {
    const note = moderatorNotes[complaintId] || '';
    try {
      await reviewModerationComplaint(complaintId, action, note, "Community Reviewer Desk");
      loadQueue();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-20">
      
      {/* Header */}
      <div className="bg-slate-900 text-white p-6 sm:p-8 rounded-3xl shadow-md space-y-2">
        <div className="flex items-center gap-2.5 text-indigo-400">
          <ShieldCheck className="w-6 h-6" />
          <h2 className="text-xl sm:text-2xl font-extrabold">
            {t('moderation.title')}
          </h2>
        </div>
        <p className="text-xs text-slate-300">
          {t('moderation.subtitle')}
        </p>

        {/* Tab switcher */}
        <div className="flex gap-2 pt-3">
          <button
            onClick={() => setTab('PENDING')}
            className={`px-3.5 py-1.5 text-xs font-bold rounded-xl transition-colors ${
              tab === 'PENDING' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {t('moderation.pending_tab')}
          </button>
          <button
            onClick={() => setTab('FLAGGED')}
            className={`px-3.5 py-1.5 text-xs font-bold rounded-xl transition-colors ${
              tab === 'FLAGGED' ? 'bg-red-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {t('moderation.flagged_tab')}
          </button>
        </div>
      </div>

      {/* Queue items */}
      {loading ? (
        <div className="py-20 text-center text-xs text-slate-500">Loading moderation queue...</div>
      ) : queue.length === 0 ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 text-xs text-slate-500">
          ✓ All submissions in this queue have been reviewed!
        </div>
      ) : (
        <div className="space-y-4">
          {queue.map((item) => (
            <div key={item.id} className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-slate-600">{item.public_id}</span>
                <span className="font-bold text-slate-500">📍 {item.sub_location}</span>
              </div>

              <h4 className="font-bold text-base text-slate-900">{item.title}</h4>
              <p className="text-xs text-slate-600 leading-relaxed">{item.description}</p>

              {item.is_official_conduct && (
                <div className="p-2 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 font-semibold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  Official Conduct Claim: requires verified evidence and strict reviewer oversight.
                </div>
              )}

              {/* Review notes input */}
              <input
                type="text"
                placeholder={t('moderation.notes_placeholder')}
                value={moderatorNotes[item.id] || ''}
                onChange={(e) => setModeratorNotes({ ...moderatorNotes, [item.id]: e.target.value })}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl text-xs"
              />

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-2 border-t">
                <button
                  onClick={() => onSelectComplaint(item.id)}
                  className="text-xs font-bold text-slate-700 hover:text-indigo-600 flex items-center gap-1"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Inspect Docket</span>
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleAction(item.id, 'REJECT')}
                    className="px-3 py-1.5 bg-red-100 hover:bg-red-200 text-red-800 text-xs font-bold rounded-xl flex items-center gap-1"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>{t('moderation.btn_reject')}</span>
                  </button>

                  <button
                    onClick={() => handleAction(item.id, 'APPROVE')}
                    className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl flex items-center gap-1 shadow"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>{t('moderation.btn_approve')}</span>
                  </button>
                </div>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
}
