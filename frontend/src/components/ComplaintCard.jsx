import React from 'react';
import { useTranslation } from 'react-i18next';
import { 
  MapPin, Users, Clock, ShieldCheck, ArrowRight, CheckCircle2,
  AlertCircle, Construction, Droplets, Trash2, Zap, Lightbulb,
  GraduationCap, Cross, Sparkles, Home, Dog, Bus, ShieldAlert, HelpCircle
} from 'lucide-react';
import CoSignButton from './CoSignButton';

const iconMap = {
  Construction, Droplets, Trash2, Zap, Lightbulb,
  GraduationCap, Cross, Sparkles, Home, Dog, Bus, ShieldAlert, HelpCircle
};

export default function ComplaintCard({ complaint, onSelect, onCoSignSuccess }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;

  const CategoryIcon = iconMap[complaint.category?.icon] || AlertCircle;
  const categoryName = lang === 'hi' ? complaint.category?.name_hi : complaint.category?.name_en;
  const areaTypeName = lang === 'hi' ? complaint.area_type?.name_hi : complaint.area_type?.name_en;
  const durationLabel = lang === 'hi' ? complaint.duration?.label_hi : complaint.duration?.label_en;

  const getStatusColor = (status) => {
    switch (status) {
      case 'RESOLVED': return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'IN_PROGRESS': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'ACKNOWLEDGED': return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'UNDER_REVIEW': return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'CLOSED_UNRESOLVED': return 'bg-slate-100 text-slate-700 border-slate-300';
      default: return 'bg-orange-100 text-orange-800 border-orange-300';
    }
  };

  const primaryEvidence = complaint.evidence && complaint.evidence.length > 0 ? complaint.evidence[0] : null;
  const evidenceUrl = primaryEvidence ? (primaryEvidence.file || primaryEvidence.file_url) : null;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 hover:border-saffron-300 shadow-sm hover:shadow-md transition-all flex flex-col overflow-hidden group">
      
      {/* Top Media / Header */}
      <div className="relative aspect-[16/9] bg-slate-900 overflow-hidden cursor-pointer" onClick={() => onSelect(complaint.id)}>
        {evidenceUrl ? (
          <img 
            src={evidenceUrl} 
            alt={complaint.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900 text-slate-500">
            <CategoryIcon className="w-12 h-12 stroke-1" />
          </div>
        )}

        {/* Top Badges */}
        <div className="absolute top-3 left-3 right-3 flex items-center justify-between pointer-events-none">
          <span className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider border shadow-sm backdrop-blur-md ${getStatusColor(complaint.status)}`}>
            {t(`status.${complaint.status}`, complaint.status_display || complaint.status)}
          </span>

          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-900/80 text-white border border-slate-700 flex items-center gap-1 backdrop-blur-sm">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            SHA-256 Verified
          </span>
        </div>

        {/* Area Type Tag at bottom of image */}
        <div className="absolute bottom-2 left-3">
          <span className="px-2 py-0.5 bg-black/70 text-white rounded text-[11px] font-medium backdrop-blur-sm">
            {areaTypeName || complaint.area_type?.code}
          </span>
        </div>
      </div>

      {/* Card Content */}
      <div className="p-4 sm:p-5 flex-1 flex flex-col justify-between space-y-3">
        <div className="space-y-2">
          
          {/* Category & Docket ID */}
          <div className="flex items-center justify-between text-xs text-slate-500">
            <div className="flex items-center gap-1.5 font-semibold text-saffron-700">
              <CategoryIcon className="w-4 h-4" />
              <span>{categoryName}</span>
            </div>
            <span className="font-mono text-[11px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
              {complaint.public_id}
            </span>
          </div>

          {/* Title */}
          <h3 
            onClick={() => onSelect(complaint.id)}
            className="font-bold text-slate-900 text-base leading-snug line-clamp-2 cursor-pointer hover:text-saffron-600 transition-colors"
          >
            {complaint.title}
          </h3>

          {/* Description snippet */}
          <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
            {complaint.description}
          </p>

          {/* Location & Duration info */}
          <div className="flex flex-wrap items-center gap-y-1 gap-x-3 text-[11px] text-slate-500 pt-1">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
              <span className="truncate max-w-[180px]">{complaint.sub_location}</span>
            </span>
            {durationLabel && (
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                <span>{durationLabel}</span>
              </span>
            )}
          </div>
        </div>

        {/* Footer: Co-sign CTA & Docket link */}
        <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
          <CoSignButton 
            complaintId={complaint.id}
            initialCount={complaint.co_sign_count}
            onSuccess={onCoSignSuccess}
            size="sm"
          />

          <button
            onClick={() => onSelect(complaint.id)}
            className="px-3 py-1.5 text-xs font-bold text-slate-700 hover:text-saffron-600 hover:bg-slate-50 rounded-lg flex items-center gap-1 transition-colors"
          >
            <span>Case Docket</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>

    </div>
  );
}
