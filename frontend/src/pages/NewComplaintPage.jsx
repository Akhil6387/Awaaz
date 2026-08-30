import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Camera, MapPin, FileText, CheckCircle2, ArrowRight, ArrowLeft, 
  ShieldCheck, AlertTriangle, Building2, Trees, Lock, UploadCloud
} from 'lucide-react';
import LiveCameraCapture from '../components/LiveCameraCapture';
import LiveAudioCapture from '../components/LiveAudioCapture';
import MapPicker from '../components/MapPicker';
import DuplicateWarningModal from '../components/DuplicateWarningModal';
import { fetchBootstrapConfig, checkDuplicates, submitComplaint, suggestUnitByCoords } from '../services/api';
import { useSession } from '../context/SessionContext';

export default function NewComplaintPage({ onComplaintCreated, onCancel, onSelectExisting }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const { sessionId, trackFiledComplaint } = useSession();

  const [step, setStep] = useState(1);
  const [config, setConfig] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Form State
  const [mediaProof, setMediaProof] = useState(null);
  const [audioNote, setAudioNote] = useState(null);
  const [areaType, setAreaType] = useState('CITY'); // 'VILLAGE', 'TOWN', 'CITY'
  const [coords, setCoords] = useState({ lat: 23.2332, lng: 77.4350, accuracy: 10 });
  const [suggestedUnit, setSuggestedUnit] = useState(null);
  const [subLocation, setSubLocation] = useState('');
  const [authorityName, setAuthorityName] = useState('');
  const [authorityDesig, setAuthorityDesig] = useState('');
  const [category, setCategory] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [duration, setDuration] = useState('');
  const [peopleAffectedType, setPeopleAffectedType] = useState('ESTIMATE');
  const [peopleAffectedCount, setPeopleAffectedCount] = useState(100);
  const [priorAttemptsCount, setPriorAttemptsCount] = useState(0);
  const [priorChannel, setPriorChannel] = useState('');
  const [priorRefNumber, setPriorRefNumber] = useState('');
  const [revealIdentity, setRevealIdentity] = useState(false);
  const [filerName, setFilerName] = useState('');
  const [filerPhone, setFilerPhone] = useState('');

  // Duplicate warning modal state
  const [duplicates, setDuplicates] = useState([]);
  const [showDupeModal, setShowDupeModal] = useState(false);

  useEffect(() => {
    fetchBootstrapConfig()
      .then(cfg => {
        setConfig(cfg);
        if (cfg.categories?.length > 0) setCategory(cfg.categories[0].id);
        if (cfg.duration_options?.length > 0) setDuration(cfg.duration_options[0].id);
        if (cfg.prior_channels?.length > 0) setPriorChannel(cfg.prior_channels[0].id);
      })
      .catch(err => console.error(err));
  }, []);

  // When location changes, auto-suggest administrative unit & check duplicates
  const handleLocationSelect = async (loc) => {
    setCoords(loc);
    try {
      const suggestRes = await suggestUnitByCoords(loc.lat, loc.lng, areaType);
      if (suggestRes?.suggested) {
        setSuggestedUnit(suggestRes.suggested);
        if (!subLocation) {
          setSubLocation(suggestRes.suggested.name_en);
        }
      }
    } catch (e) {
      console.warn(e);
    }
  };

  // Trigger duplicate check when advancing to details
  const triggerDuplicateCheck = async () => {
    if (coords && category) {
      const dupeRes = await checkDuplicates(coords.lat, coords.lng, category, 500);
      if (dupeRes?.count > 0) {
        setDuplicates(dupeRes.duplicates);
        setShowDupeModal(true);
        return true;
      }
    }
    return false;
  };

  const handleNextStep = async () => {
    setErrorMsg(null);
    if (step === 1) {
      if (!mediaProof && !audioNote) {
        setErrorMsg("Please take a live photo or record a voice note proof to proceed.");
        return;
      }
    } else if (step === 2) {
      if (!subLocation.trim()) {
        setErrorMsg("Please enter the specific locality, mohalla, or village landmark.");
        return;
      }
      await triggerDuplicateCheck();
    } else if (step === 3) {
      if (!title.trim()) {
        setErrorMsg("Please provide a title for the issue.");
        return;
      }
      if (description.trim().length < 30) {
        setErrorMsg(`Description must be at least 30 characters (${description.trim().length}/30 entered).`);
        return;
      }
    }
    setStep(prev => prev + 1);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setErrorMsg(null);
    try {
      const formData = new FormData();
      formData.append('anonymous_session_id', sessionId);
      formData.append('revealed_identity', revealIdentity);
      if (revealIdentity) {
        formData.append('filer_name', filerName);
        formData.append('filer_phone', filerPhone);
      }
      formData.append('area_type', areaType === 'VILLAGE' ? 1 : (areaType === 'TOWN' ? 2 : 3));
      formData.append('category', category);
      formData.append('duration', duration);
      formData.append('title', title);
      formData.append('description', description);
      formData.append('people_affected_type', peopleAffectedType);
      formData.append('people_affected_count', peopleAffectedCount || 0);
      formData.append('prior_attempts_count', priorAttemptsCount || 0);
      if (priorChannel) formData.append('prior_channel', priorChannel);
      if (priorRefNumber) formData.append('prior_reference_number', priorRefNumber);
      if (suggestedUnit) formData.append('administrative_unit', suggestedUnit.id);
      formData.append('sub_location', subLocation);
      if (authorityName) formData.append('authority_name_override', authorityName);
      if (authorityDesig) formData.append('authority_designation', authorityDesig);
      formData.append('latitude', coords.lat);
      formData.append('longitude', coords.lng);
      formData.append('gps_accuracy_meters', coords.accuracy || 10);
      formData.append('manual_address_text', subLocation);

      // Attach media files/dataUrls
      if (mediaProof) {
        formData.append('file_urls', mediaProof.dataUrl);
        formData.append('media_types', mediaProof.type);
      }
      if (audioNote) {
        formData.append('file_urls', audioNote.dataUrl);
        formData.append('media_types', audioNote.type);
      }

      const created = await submitComplaint(formData);
      trackFiledComplaint(created);
      onComplaintCreated(created);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "Failed to submit complaint. Please check your connection.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-16">
      
      {/* Top Header & Step Bar */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900">
              {t('form.title')}
            </h2>
            <p className="text-xs text-slate-500">
              {t('form.subtitle')}
            </p>
          </div>
          <button
            type="button"
            onClick={onCancel}
            className="text-xs text-slate-500 hover:text-slate-800 font-semibold"
          >
            Cancel
          </button>
        </div>

        {/* Step Indicator */}
        <div className="grid grid-cols-5 gap-1.5 pt-2">
          {['1. Live Proof', '2. Location', '3. Details', '4. Prior attempts', '5. Review'].map((stLabel, idx) => (
            <div key={idx} className="space-y-1">
              <div className={`h-1.5 rounded-full ${
                step > idx + 1 ? 'bg-emerald-600' :
                step === idx + 1 ? 'bg-saffron-600' : 'bg-slate-200'
              }`} />
              <div className="text-[10px] font-bold text-slate-500 truncate hidden sm:block">
                {stLabel}
              </div>
            </div>
          ))}
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs font-semibold rounded-xl flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* STEP 1: Live Media Capture */}
      {step === 1 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="space-y-1">
            <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
              <Camera className="w-5 h-5 text-saffron-600" />
              {t('form.step_media')}
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              {t('form.capture_instructions')}
            </p>
          </div>

          {/* Camera Viewfinder */}
          <LiveCameraCapture 
            onCapture={(proof) => setMediaProof(proof)}
            initialPreview={mediaProof?.dataUrl}
          />

          {/* Voice note for low-literacy */}
          <LiveAudioCapture 
            onAudioCapture={(audio) => setAudioNote(audio)}
          />

          <div className="flex justify-end pt-4 border-t">
            <button
              type="button"
              onClick={handleNextStep}
              className="px-6 py-2.5 bg-saffron-600 hover:bg-saffron-700 text-white text-xs font-bold rounded-xl flex items-center gap-2 shadow"
            >
              <span>Next: Area & Location</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Location & Area-Type Branching */}
      {step === 2 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="space-y-1">
            <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-saffron-600" />
              {t('form.step_location')}
            </h3>
            <p className="text-xs text-slate-500">
              Select whether this grievance belongs to a Gram Panchayat or Municipal Ward.
            </p>
          </div>

          {/* Area Type Selector Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div
              onClick={() => setAreaType('VILLAGE')}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                areaType === 'VILLAGE' 
                  ? 'border-emerald-600 bg-emerald-50 text-emerald-950 shadow-sm' 
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <Trees className="w-6 h-6 text-emerald-600 mb-2" />
              <h4 className="font-bold text-sm">Village / ग्रामीण</h4>
              <p className="text-[11px] text-slate-500 pt-1">Gram Panchayat / Sarpanch & Sachiv</p>
            </div>

            <div
              onClick={() => setAreaType('TOWN')}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                areaType === 'TOWN' 
                  ? 'border-amber-600 bg-amber-50 text-amber-950 shadow-sm' 
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <Building2 className="w-6 h-6 text-amber-600 mb-2" />
              <h4 className="font-bold text-sm">Town / कस्बा</h4>
              <p className="text-[11px] text-slate-500 pt-1">Nagar Panchayat / Chairman</p>
            </div>

            <div
              onClick={() => setAreaType('CITY')}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                areaType === 'CITY' 
                  ? 'border-blue-600 bg-blue-50 text-blue-950 shadow-sm' 
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <Building2 className="w-6 h-6 text-blue-600 mb-2" />
              <h4 className="font-bold text-sm">City / शहर</h4>
              <p className="text-[11px] text-slate-500 pt-1">Nagar Nigam / Ward Corporator</p>
            </div>
          </div>

          {/* Interactive Map Picker */}
          <MapPicker 
            initialCoords={coords}
            onLocationSelect={handleLocationSelect}
          />

          {/* Sub Location Name */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">
              Locality / Mohalla / Village / Landmark Name *
            </label>
            <input
              type="text"
              value={subLocation}
              onChange={(e) => setSubLocation(e.target.value)}
              placeholder="E.g. Main Market, Near Primary Health Center, Ward 45"
              className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs"
            />
          </div>

          <div className="flex items-center justify-between pt-4 border-t">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl flex items-center gap-1"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
            <button
              type="button"
              onClick={handleNextStep}
              className="px-6 py-2.5 bg-saffron-600 hover:bg-saffron-700 text-white text-xs font-bold rounded-xl flex items-center gap-2 shadow"
            >
              <span>Next: Grievance Details</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Grievance Details */}
      {step === 3 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div className="space-y-1">
            <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-saffron-600" />
              {t('form.step_details')}
            </h3>
            <p className="text-xs text-slate-500">
              Provide structured, factual information to help officials identify and resolve the issue.
            </p>
          </div>

          {/* Category Selector */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">{t('form.category_label')} *</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium"
            >
              {config?.categories?.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {lang === 'hi' ? `${cat.name_hi} (${cat.name_en})` : cat.name_en}
                </option>
              ))}
            </select>
          </div>

          {/* Title */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">{t('form.title_label')} *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={t('form.title_placeholder')}
              className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs"
            />
          </div>

          {/* Description */}
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-700">{t('form.desc_label')} *</label>
              <span className={`text-[11px] ${description.length >= 30 ? 'text-emerald-600' : 'text-amber-600'}`}>
                {description.length} / 30 chars min
              </span>
            </div>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              placeholder={t('form.desc_placeholder')}
              className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs leading-relaxed"
            />
          </div>

          {/* Duration & People Affected */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">{t('form.duration_label')}</label>
              <select
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs"
              >
                {config?.duration_options?.map((d) => (
                  <option key={d.id} value={d.id}>
                    {lang === 'hi' ? d.label_hi : d.label_en}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">{t('form.people_affected_label')}</label>
              <input
                type="number"
                value={peopleAffectedCount}
                onChange={(e) => setPeopleAffectedCount(e.target.value)}
                placeholder="E.g. 500"
                className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs"
              />
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t">
            <button
              type="button"
              onClick={() => setStep(2)}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl flex items-center gap-1"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
            <button
              type="button"
              onClick={handleNextStep}
              className="px-6 py-2.5 bg-saffron-600 hover:bg-saffron-700 text-white text-xs font-bold rounded-xl flex items-center gap-2 shadow"
            >
              <span>Next: Prior Escalations</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: Prior Escalations & Identity Option */}
      {step === 4 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div className="space-y-1">
            <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-saffron-600" />
              {t('form.step_prior')}
            </h3>
            <p className="text-xs text-slate-500">
              Awaaz serves as an evidence escalation layer over official grievance portals (CM Helpline, 311, Panchayat).
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">{t('form.prior_count_label')}</label>
              <input
                type="number"
                min="0"
                value={priorAttemptsCount}
                onChange={(e) => setPriorAttemptsCount(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">{t('form.prior_channel_label')}</label>
              <select
                value={priorChannel}
                onChange={(e) => setPriorChannel(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs"
              >
                {config?.prior_channels?.map((ch) => (
                  <option key={ch.id} value={ch.id}>
                    {lang === 'hi' ? ch.label_hi : ch.label_en}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">{t('form.prior_ref_label')}</label>
            <input
              type="text"
              value={priorRefNumber}
              onChange={(e) => setPriorRefNumber(e.target.value)}
              placeholder="E.g. CM181-8949102 / BMC-311-949"
              className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono"
            />
          </div>

          {/* Authority Name Override */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">
                {areaType === 'VILLAGE' ? 'Sarpanch / Pradhan Name' : 'Ward Corporator Name'}
              </label>
              <input
                type="text"
                value={authorityName}
                onChange={(e) => setAuthorityName(e.target.value)}
                placeholder="E.g. Rajesh Sharma"
                className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Designation</label>
              <input
                type="text"
                value={authorityDesig}
                onChange={(e) => setAuthorityDesig(e.target.value)}
                placeholder="E.g. Ward 45 Corporator / Sarpanch"
                className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs"
              />
            </div>
          </div>

          {/* Identity Reveal Toggle */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={revealIdentity}
                onChange={(e) => setRevealIdentity(e.target.checked)}
                className="w-4 h-4 text-saffron-600 rounded"
              />
              <span className="text-xs font-bold text-slate-800">{t('form.reveal_toggle')}</span>
            </label>

            {revealIdentity && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <input
                  type="text"
                  value={filerName}
                  onChange={(e) => setFilerName(e.target.value)}
                  placeholder="Your Full Name"
                  className="p-2.5 bg-white border border-slate-300 rounded-xl text-xs"
                />
                <input
                  type="text"
                  value={filerPhone}
                  onChange={(e) => setFilerPhone(e.target.value)}
                  placeholder="Your Phone Number"
                  className="p-2.5 bg-white border border-slate-300 rounded-xl text-xs"
                />
              </div>
            )}
          </div>

          <div className="flex items-center justify-between pt-4 border-t">
            <button
              type="button"
              onClick={() => setStep(3)}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl flex items-center gap-1"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
            <button
              type="button"
              onClick={handleNextStep}
              className="px-6 py-2.5 bg-saffron-600 hover:bg-saffron-700 text-white text-xs font-bold rounded-xl flex items-center gap-2 shadow"
            >
              <span>Next: Final Review</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 5: Final Review & Submission */}
      {step === 5 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="space-y-1">
            <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-600" />
              {t('form.step_preview')}
            </h3>
            <p className="text-xs text-slate-500">
              Review your complaint docket before public broadcast. Evidence will be signed and hashed server-side.
            </p>
          </div>

          {/* Preview Docket Summary */}
          <div className="bg-slate-50 p-4 sm:p-5 rounded-xl border border-slate-200 space-y-3 text-xs">
            <div className="flex items-center justify-between border-b pb-2">
              <span className="font-bold text-slate-500">Area & Governance</span>
              <span className="font-bold text-slate-900">{areaType} • {subLocation}</span>
            </div>

            <div className="space-y-1">
              <span className="font-bold text-slate-500">Title:</span>
              <h4 className="font-bold text-sm text-slate-900">{title}</h4>
            </div>

            <div className="space-y-1">
              <span className="font-bold text-slate-500">Description:</span>
              <p className="text-slate-700 leading-relaxed">{description}</p>
            </div>

            <div className="flex items-center justify-between pt-2 border-t">
              <span className="font-bold text-slate-500">Identity:</span>
              <span className="font-bold text-emerald-700">
                {revealIdentity ? `${filerName} (${filerPhone})` : '100% Anonymous'}
              </span>
            </div>

            {/* Evidence Thumbnail */}
            {mediaProof && (
              <div className="pt-2 border-t">
                <span className="font-bold text-slate-500 block mb-2">Live Proof Attachment:</span>
                <img 
                  src={mediaProof.dataUrl} 
                  alt="Proof preview" 
                  className="w-32 h-20 object-cover rounded-lg border shadow-sm"
                />
              </div>
            )}
          </div>

          <div className="flex items-center justify-between pt-4 border-t">
            <button
              type="button"
              onClick={() => setStep(4)}
              disabled={submitting}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl flex items-center gap-1"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="px-8 py-3 bg-gradient-to-r from-saffron-600 to-amber-600 hover:from-saffron-700 hover:to-amber-700 text-white text-sm font-extrabold rounded-xl flex items-center gap-2 shadow-lg hover:scale-105 transition-all"
            >
              <UploadCloud className="w-5 h-5" />
              <span>{submitting ? t('form.btn_submitting') : t('form.btn_submit')}</span>
            </button>
          </div>
        </div>
      )}

      {/* Duplicate Warning Modal */}
      <DuplicateWarningModal
        isOpen={showDupeModal}
        duplicates={duplicates}
        onClose={() => setShowDupeModal(false)}
        onProceedNew={() => {
          setShowDupeModal(false);
          setStep(3);
        }}
        onSelectExisting={(id) => {
          setShowDupeModal(false);
          onSelectExisting(id);
        }}
      />

    </div>
  );
}
