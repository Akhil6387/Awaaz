import React from 'react';
import { useTranslation } from 'react-i18next';
import { Megaphone, PlusCircle, BookmarkCheck, ShieldCheck, MapPin, Globe, HelpCircle } from 'lucide-react';
import { useSession } from '../context/SessionContext';

export default function Navbar({ activeTab, setActiveTab }) {
  const { t, i18n } = useTranslation();
  const { myComplaints } = useSession();

  const toggleLanguage = () => {
    const nextLang = i18n.language === 'hi' ? 'en' : 'hi';
    i18n.changeLanguage(nextLang);
    localStorage.setItem('awaaz_lang', nextLang);
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div 
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => setActiveTab('feed')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-saffron-600 to-amber-500 flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform">
              <Megaphone className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-slate-900 group-hover:text-saffron-600 transition-colors">
                  आवाज़ <span className="text-saffron-600 text-sm font-semibold tracking-normal">Awaaz</span>
                </span>
                <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-bold tracking-wider uppercase bg-emerald-100 text-emerald-800 rounded-full">
                  {t('brand.badge')}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 leading-none hidden sm:block">
                {t('brand.tagline')}
              </p>
            </div>
          </div>

          {/* Nav Links */}
          <nav className="flex items-center gap-1 sm:gap-2">
            <button
              onClick={() => setActiveTab('feed')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'feed'
                  ? 'bg-slate-100 text-slate-900 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              {t('nav.feed')}
            </button>

            <button
              onClick={() => setActiveTab('my_complaints')}
              className={`relative px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === 'my_complaints'
                  ? 'bg-slate-100 text-slate-900 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <BookmarkCheck className="w-4 h-4 text-emerald-600" />
              <span>{t('nav.my_complaints')}</span>
              {myComplaints.length > 0 && (
                <span className="ml-1 px-1.5 py-0.2 bg-emerald-600 text-white text-[10px] font-bold rounded-full">
                  {myComplaints.length}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('moderation')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors hidden md:flex items-center gap-1.5 ${
                activeTab === 'moderation'
                  ? 'bg-slate-100 text-slate-900 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <ShieldCheck className="w-4 h-4 text-indigo-600" />
              <span>{t('nav.moderation')}</span>
            </button>

            <button
              onClick={() => setActiveTab('about')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors hidden lg:flex items-center gap-1.5 ${
                activeTab === 'about'
                  ? 'bg-slate-100 text-slate-900 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <HelpCircle className="w-4 h-4 text-slate-500" />
              <span>{t('nav.about')}</span>
            </button>
          </nav>

          {/* Action CTAs */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors border border-slate-200"
              title="Change Language"
            >
              <Globe className="w-3.5 h-3.5 text-slate-600" />
              <span>{t('nav.language')}</span>
            </button>

            <button
              onClick={() => setActiveTab('new_complaint')}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-saffron-600 to-amber-600 hover:from-saffron-700 hover:to-amber-700 text-white rounded-xl text-xs sm:text-sm font-bold shadow-sm hover:shadow transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{t('nav.new_complaint')}</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
