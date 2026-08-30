import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  ArrowLeft, ShieldCheck, MapPin, Clock, Users, Building2, Trees,
  FileText, ShieldAlert, Share2, Volume2, CheckCircle2, User, Phone,
  ExternalLink, MessageSquare
} from 'lucide-react';
import CoSignButton from '../components/CoSignButton';
import StatusAuditTimeline from '../components/StatusAuditTimeline';
import EscalationLetterModal from '../components/EscalationLetterModal';
import ReportFlagModal from '../components/ReportFlagModal';
import { fetchComplaintDetail } from '../services/api';

export default function ComplaintDetailPage({ complaintId, onBack, onSelectOther }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;

  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showEscalationModal, setShowEscalationModal] = useState(false);
  const [showFlagModal, setShowFlagModal] = useState(false);

  const loadData = () => {
    setLoading(true);
    fetchComplaintDetail(complaintId)
      .then(data => setComplaint(data))
      .catch(err => {
        console.error(err);
        setError("Failed to load case docket details.");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (complaintId) {
      loadData();
    }
  }, [complaintId]);

  if (loading) {
    return (
      <div className="py-32 text-center space-y-3">
        <div className="w-10 h-10 border-4 border-saffron-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-xs text-slate-500">Retrieving case evidence & audit trail...</p>
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 space-y-4">
        <p className="text-sm text-red-600 font-bold">{error || "Complaint docket not found"}</p>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold"
        >
          Return to Feed
        </button>
      </div>
    );
  }

  const categoryName = lang === 'hi' ? complaint.category?.name_hi : complaint.category?.name_en;
  const areaTypeName = lang === 'hi' ? complaint.area_type?.name_hi : complaint.area_type?.name_en;
  const durationLabel = lang === 'hi' ? complaint.duration?.label_hi : complaint.duration?.label_en;
  const priorChannelLabel = lang === 'hi' ? complaint.prior_channel?.label_hi : complaint.prior_channel?.label_en;

  const photoEvidence = complaint.evidence?.filter(e => e.media_type === 'PHOTO') || [];
  const audioEvidence = complaint.evidence?.filter(e => e.media_type === 'AUDIO_NOTE') || [];

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-20">
      
      {/* Back Button & Top Action Strip */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="px-3.5 py-1.5 bg-white hover:bg-slate-100 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 flex items-center gap-1.5 shadow-sm transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Feed</span>
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFlagModal(true)}
            className="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-xl text-xs font-semibold flex items-center gap-1.5"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{t('detail.report_flag')}</span>
          </button>
        </div>
      </div>

      {/* Main Dossier Header */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        
        {/* Top Badges */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-sm font-black text-slate-900 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200">
              {complaint.public_id}
            </span>
            <span className="px-2.5 py-1 bg-saffron-50 text-saffron-800 border border-saffron-200 rounded-lg text-xs font-bold">
              {categoryName}
            </span>
            <span className="px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-lg text-xs font-semibold">
              {areaTypeName}
            </span>
          </div>

          <span className="px-3 py-1 bg-slate-900 text-white rounded-lg text-xs font-extrabold uppercase tracking-wider">
            {complaint.status_display || complaint.status}
          </span>
        </div>

        {/* Title & Description */}
        <div className="space-y-3">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 leading-snug">
            {complaint.title}
          </h1>

          <p className="text-sm sm:text-base text-slate-700 leading-relaxed whitespace-pre-wrap">
            {complaint.description}
          </p>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-200 text-xs">
          <div>
            <div className="text-slate-400 font-medium">Problem Duration</div>
            <div className="font-bold text-slate-900 mt-0.5">{durationLabel || 'N/A'}</div>
          </div>
          <div>
            <div className="text-slate-400 font-medium">People Impacted</div>
            <div className="font-bold text-slate-900 mt-0.5">
              {complaint.people_affected_count ? `${complaint.people_affected_count} citizens` : 'Entire locality'}
            </div>
          </div>
          <div>
            <div className="text-slate-400 font-medium">Prior Escalations</div>
            <div className="font-bold text-slate-900 mt-0.5">
              {complaint.prior_attempts_count > 0 ? `${complaint.prior_attempts_count} times (${priorChannelLabel || 'Portal'})` : 'First report on Awaaz'}
            </div>
          </div>
          <div>
            <div className="text-slate-400 font-medium">Identity Status</div>
            <div className="font-bold text-emerald-700 mt-0.5">
              {complaint.revealed_identity ? `${complaint.filer_name}` : '100% Anonymous'}
            </div>
          </div>
        </div>

        {/* Co-Sign & Pressure Escalation Banner */}
        <div className="p-5 bg-gradient-to-r from-saffron-50 to-amber-50 rounded-2xl border border-saffron-200 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center sm:text-left">
            <h4 className="font-extrabold text-sm sm:text-base text-saffron-950">
              Community Accountability Pressure
            </h4>
            <p className="text-xs text-saffron-800">
              {complaint.co_sign_count} citizens have co-signed facing this exact problem.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <CoSignButton
              complaintId={complaint.id}
              initialCount={complaint.co_sign_count}
              onSuccess={loadData}
              size="md"
            />

            <button
              type="button"
              onClick={() => setShowEscalationModal(true)}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl flex items-center gap-1.5 shadow"
            >
              <FileText className="w-4 h-4 text-saffron-400" />
              <span>Generate RTI / Letter</span>
            </button>
          </div>
        </div>

      </div>

      {/* Live Evidence & SHA-256 Integrity Section */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b pb-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            <h3 className="font-bold text-base text-slate-900">
              Tamper-Evident Live Captured Proof
            </h3>
          </div>
          <span className="text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-bold border border-emerald-200">
            Immutable Receipt
          </span>
        </div>

        {/* Photo Gallery */}
        {photoEvidence.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {photoEvidence.map((ev, idx) => (
              <div key={ev.id || idx} className="space-y-2">
                <div className="relative aspect-video rounded-2xl overflow-hidden bg-slate-900 border shadow-inner">
                  <img 
                    src={ev.file || ev.file_url} 
                    alt="Captured evidence"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute bottom-2 left-2 bg-black/70 text-white px-2 py-0.5 rounded text-[10px] font-mono backdrop-blur-sm">
                    {ev.capture_timestamp?.substring(0, 19).replace('T', ' ')} UTC
                  </div>
                </div>
                {/* SHA-256 Hash Display */}
                <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-[11px] space-y-0.5 font-mono">
                  <span className="text-slate-400 font-sans font-bold block text-[10px] uppercase">SHA-256 Checksum:</span>
                  <span className="text-slate-700 break-all">{ev.sha256_hash}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500">No photo attachments uploaded.</p>
        )}

        {/* Voice Note Audio Player */}
        {audioEvidence.length > 0 && (
          <div className="p-4 bg-amber-50 rounded-2xl border border-amber-200 space-y-2">
            <span className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
              <Volume2 className="w-4 h-4 text-amber-700" />
              Citizen Live Voice-Note Record:
            </span>
            {audioEvidence.map((a, idx) => (
              <audio key={a.id || idx} src={a.file || a.file_url} controls className="w-full h-9" />
            ))}
          </div>
        )}
      </div>

      {/* Responsible Authority & Location Profile */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Authority in charge */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-saffron-600" />
            {t('detail.authority_in_charge')}
          </h3>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2 text-xs">
            <div className="font-extrabold text-slate-900 text-sm">
              {complaint.authority_name_override || (complaint.administrative_unit?.authorities?.[0]?.name_en || 'Designated Public Grievance Officer')}
            </div>
            <div className="text-saffron-700 font-semibold">
              {complaint.authority_designation || (complaint.administrative_unit?.authorities?.[0]?.designation_en || 'Competent Authority')}
            </div>
            <div className="text-slate-500 pt-1">
              📍 {complaint.administrative_unit?.name_en || complaint.sub_location}
            </div>
          </div>
        </div>

        {/* Location & GPS Info */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-saffron-600" />
            Verified Geo-Location
          </h3>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2 text-xs">
            <div className="font-bold text-slate-800">{complaint.sub_location}</div>
            <div className="font-mono text-slate-600">
              Latitude: {complaint.latitude?.toFixed(5)} • Longitude: {complaint.longitude?.toFixed(5)}
            </div>
            <div className="text-emerald-700 font-medium pt-1">
              ✓ GPS Accuracy Stamped at Capture Time
            </div>
          </div>
        </div>

      </div>

      {/* Public Status Audit Trail Timeline */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm">
        <StatusAuditTimeline auditTrail={complaint.audit_trail} />
      </div>

      {/* Modals */}
      <EscalationLetterModal 
        complaintId={complaint.id}
        isOpen={showEscalationModal}
        onClose={() => setShowEscalationModal(false)}
      />

      <ReportFlagModal
        complaintId={complaint.id}
        isOpen={showFlagModal}
        onClose={() => setShowFlagModal(false)}
      />

    </div>
  );
}
