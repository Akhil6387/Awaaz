import React from 'react';
import { useTranslation } from 'react-i18next';
import { AlertTriangle, Users, MapPin, CheckCircle2, X, ArrowRight } from 'lucide-react';
import CoSignButton from './CoSignButton';

export default function DuplicateWarningModal({ duplicates, isOpen, onClose, onProceedNew, onSelectExisting }) {
  const { t } = useTranslation();
  if (!isOpen || duplicates.length === 0) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-amber-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="p-4 sm:p-5 bg-gradient-to-r from-amber-500 to-saffron-600 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center backdrop-blur-sm">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-base sm:text-lg">
                Nearby Similar Complaints Found ({duplicates.length})
              </h3>
              <p className="text-xs text-amber-100">
                Co-signing an existing issue builds more pressure than filing duplicates!
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-white/80 hover:text-white p-1 rounded-lg hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* List of Duplicates */}
        <div className="p-4 sm:p-6 overflow-y-auto space-y-3 divide-y divide-slate-100 flex-1">
          {duplicates.map((dup) => (
            <div key={dup.id} className="pt-3 first:pt-0 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-saffron-700 flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" />
                  {dup.distance_meters}m away • {dup.sub_location}
                </span>
                <span className="font-mono text-[11px] text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
                  {dup.public_id}
                </span>
              </div>

              <h4 className="font-bold text-sm text-slate-900 leading-snug">
                {dup.title}
              </h4>

              <p className="text-xs text-slate-600 line-clamp-2">
                {dup.description}
              </p>

              <div className="flex items-center justify-between pt-1">
                <CoSignButton 
                  complaintId={dup.id} 
                  initialCount={dup.co_sign_count} 
                  size="sm"
                />

                <button
                  type="button"
                  onClick={() => onSelectExisting(dup.id)}
                  className="text-xs font-bold text-slate-700 hover:text-saffron-600 flex items-center gap-1"
                >
                  <span>View Full Docket</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-slate-500 text-center sm:text-left">
            Is your problem distinct from these?
          </p>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 sm:flex-none px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-bold rounded-xl"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={onProceedNew}
              className="flex-1 sm:flex-none px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl shadow"
            >
              Proceed & File as New Issue
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
