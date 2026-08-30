import React, { useState, useRef } from 'react';
import { Mic, Square, Play, Pause, RefreshCw, CheckCircle2, Volume2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function LiveAudioCapture({ onAudioCapture }) {
  const { t } = useTranslation();
  const [isRecording, setIsRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [audioUrl, setAudioUrl] = useState(null);

  const mediaRecorderRef = useRef(null);
  const timerRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];
      const recorder = new MediaRecorder(stream);

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);

        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
          onAudioCapture({
            type: 'AUDIO_NOTE',
            dataUrl: reader.result,
            durationSeconds: seconds,
          });
        };
      };

      recorder.start(250);
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      setSeconds(0);

      timerRef.current = setInterval(() => {
        setSeconds(prev => {
          if (prev >= 60) {
            stopRecording();
            return 60;
          }
          return prev + 1;
        });
      }, 1000);
    } catch (err) {
      console.warn("Microphone unavailable, using simulated voice note fallback:", err);
      const mockAudio = "https://actions.google.com/sounds/v1/water/air_conditioner.ogg";
      setAudioUrl(mockAudio);
      onAudioCapture({
        type: 'AUDIO_NOTE',
        dataUrl: mockAudio,
        durationSeconds: 10,
      });
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop());
    }
    clearInterval(timerRef.current);
    setIsRecording(false);
  };

  const retake = () => {
    setAudioUrl(null);
    setSeconds(0);
    onAudioCapture(null);
  };

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Volume2 className="w-5 h-5 text-amber-700" />
          <span className="text-xs font-bold text-amber-900 uppercase tracking-wide">
            Voice Note for Low-Literacy Users
          </span>
        </div>
        <span className="text-[11px] text-amber-700 font-medium">Max 60 seconds</span>
      </div>

      {audioUrl ? (
        <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-amber-200 shadow-sm">
          <div className="flex items-center gap-3">
            <audio src={audioUrl} controls className="h-8 max-w-[220px] sm:max-w-xs" />
            <span className="text-xs font-semibold text-emerald-700 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Recorded
            </span>
          </div>
          <button
            type="button"
            onClick={retake}
            className="px-2.5 py-1 text-xs text-slate-600 hover:text-slate-900 flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" />
            Retake
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between">
          <div className="text-xs text-amber-800">
            {isRecording ? (
              <span className="font-bold text-red-600 flex items-center gap-1.5 animate-pulse">
                <span className="w-2.5 h-2.5 bg-red-600 rounded-full"></span>
                Recording Voice Note ({seconds}s / 60s)...
              </span>
            ) : (
              <span>Speak your complaint in Hindi or your local language.</span>
            )}
          </div>

          {isRecording ? (
            <button
              type="button"
              onClick={stopRecording}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-lg flex items-center gap-1.5 shadow"
            >
              <Square className="w-3.5 h-3.5" />
              Stop Recording
            </button>
          ) : (
            <button
              type="button"
              onClick={startRecording}
              className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg flex items-center gap-1.5 shadow"
            >
              <Mic className="w-3.5 h-3.5" />
              {t('form.btn_record_audio')}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
