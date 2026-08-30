import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldAlert, X, CheckCircle2 } from 'lucide-react';
import { useSession } from '../context/SessionContext';
import { flagComplaint } from '../services/api';

export default function ReportFlagModal({ complaintId, isOpen, onClose }) {
  const { t } = useTranslation();
  const { sessionId } = useSession();
  const [reason, setReason] = useState('UNVERIFIED_DEFAMATION');
  const [explanation, setExplanation] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await flagComplaint(complaintId, reason, explanation, sessionId);
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 2500);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between border-b pb-3">
          <div className="flex items-center gap-2 text-red-600">
            <ShieldAlert className="w-5 h-5" />
            <h3 className="font-bold text-base text-slate-900">Report Community Violation</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        {success ? (
          <div className="py-6 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
            <h4 className="font-bold text-sm text-slate-900">Report Submitted</h4>
            <p className="text-xs text-slate-600">Our moderation desk will review this complaint promptly.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div className="space-y-1">
              <label className="font-bold text-slate-700">Reason for Reporting</label>
              <select
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl font-medium"
              >
                <option value="UNVERIFIED_DEFAMATION">Unverified Personal Defamation against Individual</option>
                <option value="HATE_SPEECH">Hate Speech / Discriminatory Language</option>
                <option value="SPAM">Spam / Advertisement / Irrelevant Content</option>
                <option value="FALSE_LOCATION">Fabricated / False GPS Location</option>
                <option value="PERSONAL_DATA_LEAK">Unauthorized Leak of Private Citizen Phone/Data</option>
                <option value="OTHER">Other Community Policy Violation</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="font-bold text-slate-700">Additional Details</label>
              <textarea
                value={explanation}
                onChange={(e) => setExplanation(e.target.value)}
                rows={3}
                placeholder="Explain why this content violates community guidelines..."
                className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-2 bg-slate-100 text-slate-700 font-bold rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl shadow"
              >
                {loading ? 'Submitting...' : 'Submit Report'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
