import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FileText, Copy, Printer, CheckCircle2, Globe, X, Download } from 'lucide-react';
import { generateEscalationLetter } from '../services/api';

export default function EscalationLetterModal({ complaintId, isOpen, onClose }) {
  const { t } = useTranslation();
  const [lang, setLang] = useState('hi');
  const [letterData, setLetterData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen && complaintId) {
      setLoading(true);
      generateEscalationLetter(complaintId, lang)
        .then(data => {
          setLetterData(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [isOpen, complaintId, lang]);

  if (!isOpen) return null;

  const copyToClipboard = () => {
    if (!letterData) return;
    navigator.clipboard.writeText(letterData.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="p-4 sm:p-5 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-saffron-600 flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-extrabold text-base sm:text-lg">
                {t('escalation.title')}
              </h3>
              <p className="text-xs text-slate-400">
                {t('escalation.subtitle')}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Language Switch */}
            <button
              onClick={() => setLang(prev => prev === 'hi' ? 'en' : 'hi')}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-lg border border-slate-700 flex items-center gap-1 text-slate-200"
            >
              <Globe className="w-3.5 h-3.5" />
              <span>{lang === 'hi' ? 'Switch to English' : 'हिंदी में देखें'}</span>
            </button>

            <button 
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Letter Preview Body */}
        <div className="p-4 sm:p-6 overflow-y-auto flex-1 bg-slate-50">
          {loading ? (
            <div className="py-20 text-center text-slate-500 text-sm">
              Generating formatted escalation document...
            </div>
          ) : letterData ? (
            <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-300 shadow-sm font-serif text-slate-900 leading-relaxed text-sm whitespace-pre-wrap selection:bg-amber-100">
              {letterData.content}
            </div>
          ) : (
            <div className="py-20 text-center text-red-500 text-sm">
              Failed to generate document.
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div className="p-4 bg-white border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-slate-500">
            Docket ID: <span className="font-mono font-bold text-slate-700">{letterData?.public_id}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={copyToClipboard}
              className={`px-4 py-2 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-colors ${
                copied ? 'bg-emerald-600 text-white' : 'bg-slate-100 hover:bg-slate-200 text-slate-800'
              }`}
            >
              {copied ? <CheckCircle2 className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? t('escalation.copied') : t('escalation.copy_btn')}</span>
            </button>

            <button
              type="button"
              onClick={handlePrint}
              className="px-4 py-2 bg-saffron-600 hover:bg-saffron-700 text-white text-xs font-bold rounded-xl flex items-center gap-1.5 shadow"
            >
              <Printer className="w-4 h-4" />
              <span>{t('escalation.print_btn')}</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
