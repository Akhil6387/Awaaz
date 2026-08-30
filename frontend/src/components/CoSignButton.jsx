import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Users, CheckCircle2 } from 'lucide-react';
import { useSession } from '../context/SessionContext';
import { coSignComplaint } from '../services/api';

export default function CoSignButton({ complaintId, initialCount = 0, onSuccess, size = "md" }) {
  const { t } = useTranslation();
  const { sessionId, trackCoSign, hasCoSigned } = useSession();
  const [count, setCount] = useState(initialCount);
  const [loading, setLoading] = useState(false);
  const cosigned = hasCoSigned(complaintId);

  const handleCoSign = async (e) => {
    e.stopPropagation();
    if (cosigned || loading) return;

    setLoading(true);
    try {
      const res = await coSignComplaint(complaintId, sessionId);
      setCount(res.co_sign_count);
      trackCoSign(complaintId);
      if (onSuccess) onSuccess(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const isSmall = size === "sm";

  return (
    <button
      type="button"
      onClick={handleCoSign}
      disabled={cosigned || loading}
      className={`inline-flex items-center gap-1.5 rounded-xl font-bold transition-all ${
        cosigned
          ? 'bg-emerald-50 text-emerald-800 border border-emerald-300 cursor-default'
          : 'bg-gradient-to-r from-saffron-600 to-amber-600 hover:from-saffron-700 hover:to-amber-700 text-white shadow-sm hover:scale-[1.02] active:scale-[0.98]'
      } ${
        isSmall ? 'px-2.5 py-1 text-xs' : 'px-4 py-2 text-sm'
      }`}
    >
      {cosigned ? (
        <CheckCircle2 className={isSmall ? "w-3.5 h-3.5 text-emerald-600" : "w-4 h-4 text-emerald-600"} />
      ) : (
        <Users className={isSmall ? "w-3.5 h-3.5" : "w-4 h-4"} />
      )}
      <span>{cosigned ? t('detail.cosigned_badge') : t('detail.cosign_btn')}</span>
      <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
        cosigned ? 'bg-emerald-200 text-emerald-900' : 'bg-black/20 text-white'
      }`}>
        {count}
      </span>
    </button>
  );
}
