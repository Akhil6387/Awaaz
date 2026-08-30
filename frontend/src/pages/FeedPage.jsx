import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Search, SlidersHorizontal, Map, LayoutGrid, PlusCircle, 
  TrendingUp, Users, CheckCircle2, AlertCircle, Building2, Trees
} from 'lucide-react';
import ComplaintCard from '../components/ComplaintCard';
import ComplaintMapView from '../components/ComplaintMapView';
import { fetchComplaints, fetchBootstrapConfig } from '../services/api';

export default function FeedPage({ onSelectComplaint, onNavigateNew }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;

  const [complaints, setComplaints] = useState([]);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'map'

  // Filters
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedAreaType, setSelectedAreaType] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [sortBy, setSortBy] = useState('recent'); // 'recent' or 'cosigns'

  useEffect(() => {
    fetchBootstrapConfig()
      .then(cfg => setConfig(cfg))
      .catch(err => console.error(err));
  }, []);

  const loadComplaints = () => {
    setLoading(true);
    const params = {};
    if (search) params.search = search;
    if (selectedCategory) params.category = selectedCategory;
    if (selectedAreaType) params.area_type = selectedAreaType;
    if (selectedStatus) params.status = selectedStatus;

    fetchComplaints(params)
      .then(data => {
        let sorted = [...data];
        if (sortBy === 'cosigns') {
          sorted.sort((a, b) => b.co_sign_count - a.co_sign_count);
        } else {
          sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        }
        setComplaints(sorted);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadComplaints();
  }, [search, selectedCategory, selectedAreaType, selectedStatus, sortBy]);

  // Total stats
  const totalComplaints = complaints.length;
  const totalCoSigns = complaints.reduce((sum, c) => sum + (c.co_sign_count || 0), 0);
  const totalResolved = complaints.filter(c => c.status === 'RESOLVED').length;

  return (
    <div className="space-y-8 pb-12">
      
      {/* Hero Banner */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-950 to-navy-900 text-white p-6 sm:p-10 shadow-xl border border-slate-800">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-saffron-600/20 border border-saffron-500/30 text-saffron-400 text-xs font-bold">
            <span className="w-2 h-2 rounded-full bg-saffron-500 animate-ping"></span>
            <span>{t('brand.badge')} • Live Citizen Accountability</span>
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight leading-tight">
            <span>{t('hero.title_part1')} </span>
            <span className="text-saffron-500">{t('hero.title_part2')} </span>
            <span>{t('hero.title_part3')}</span>
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
            {t('hero.subtitle')}
          </p>

          {/* Hero CTAs */}
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={onNavigateNew}
              className="px-5 py-3 bg-gradient-to-r from-saffron-600 to-amber-600 hover:from-saffron-700 hover:to-amber-700 text-white font-bold rounded-xl text-sm shadow-lg hover:shadow-saffron-500/20 flex items-center gap-2 transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{t('hero.cta_file')}</span>
            </button>

            <button
              onClick={() => setViewMode('map')}
              className="px-5 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-xl text-sm border border-slate-700 flex items-center gap-2 transition-colors"
            >
              <Map className="w-4 h-4 text-emerald-400" />
              <span>{t('feed.switch_map')}</span>
            </button>
          </div>

          {/* Quick Counter Stats */}
          <div className="pt-6 grid grid-cols-3 gap-3 sm:gap-6 border-t border-slate-800/80">
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-white">5+</div>
              <div className="text-xs text-slate-400 font-medium">{t('hero.stat_filed')}</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-saffron-400">156+</div>
              <div className="text-xs text-slate-400 font-medium">{t('hero.stat_corroborations')}</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-emerald-400">100%</div>
              <div className="text-xs text-slate-400 font-medium">SHA-256 Hashed</div>
            </div>
          </div>
        </div>

        {/* Subtle decorative glow */}
        <div className="absolute right-0 top-0 w-96 h-96 bg-saffron-600/10 rounded-full blur-3xl pointer-events-none"></div>
      </section>

      {/* Filter & View Control Bar */}
      <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-sm space-y-4">
        
        {/* Row 1: Search & View Switcher */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="relative w-full sm:max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t('feed.search_placeholder')}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-saffron-500/20 focus:border-saffron-500"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-end">
            {/* Sort Dropdown */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700"
            >
              <option value="recent">{t('feed.sort_recent')}</option>
              <option value="cosigns">{t('feed.sort_cosigns')}</option>
            </select>

            {/* Grid vs Map Switcher */}
            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
              <button
                onClick={() => setViewMode('grid')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  viewMode === 'grid'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <LayoutGrid className="w-3.5 h-3.5" />
                <span>{t('feed.switch_feed')}</span>
              </button>
              <button
                onClick={() => setViewMode('map')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  viewMode === 'map'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Map className="w-3.5 h-3.5" />
                <span>{t('feed.switch_map')}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Row 2: Area Type & Category Filter Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
          
          {/* Area Type Filter Tabs */}
          <div className="flex items-center gap-1 bg-slate-50 p-1 rounded-xl border border-slate-200">
            <button
              onClick={() => setSelectedAreaType('')}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                selectedAreaType === '' ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-200/60'
              }`}
            >
              {t('feed.all_areas')}
            </button>
            <button
              onClick={() => setSelectedAreaType('VILLAGE')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold ${
                selectedAreaType === 'VILLAGE' ? 'bg-emerald-700 text-white' : 'text-slate-600 hover:bg-slate-200/60'
              }`}
            >
              <Trees className="w-3 h-3" />
              <span>Village (ग्रामीण)</span>
            </button>
            <button
              onClick={() => setSelectedAreaType('CITY')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold ${
                selectedAreaType === 'CITY' ? 'bg-blue-700 text-white' : 'text-slate-600 hover:bg-slate-200/60'
              }`}
            >
              <Building2 className="w-3 h-3" />
              <span>City (नगर निगम)</span>
            </button>
          </div>

          {/* Category Dropdown */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700"
          >
            <option value="">{t('feed.all_categories')}</option>
            {config?.categories?.map((cat) => (
              <option key={cat.id} value={cat.slug}>
                {lang === 'hi' ? cat.name_hi : cat.name_en}
              </option>
            ))}
          </select>

          {/* Status Dropdown */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700"
          >
            <option value="">{t('feed.all_statuses')}</option>
            <option value="FILED">Filed</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="RESOLVED">Resolved</option>
          </select>

          {/* Active Filter Clear */}
          {(selectedCategory || selectedAreaType || selectedStatus || search) && (
            <button
              onClick={() => {
                setSelectedCategory('');
                setSelectedAreaType('');
                setSelectedStatus('');
                setSearch('');
              }}
              className="text-xs text-saffron-600 hover:underline font-bold px-2"
            >
              Reset Filters
            </button>
          )}

        </div>

      </div>

      {/* Main Content Area: Grid or Map */}
      {loading ? (
        <div className="py-24 text-center space-y-3">
          <div className="w-10 h-10 border-4 border-saffron-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs text-slate-500">Loading verified civic complaints...</p>
        </div>
      ) : viewMode === 'map' ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-700">
              Interactive Geo-Map ({complaints.length} active locations)
            </span>
            <span className="text-xs text-slate-500">
              Click on pins to view live evidence & co-sign
            </span>
          </div>
          <ComplaintMapView 
            complaints={complaints}
            onSelectComplaint={onSelectComplaint}
          />
        </div>
      ) : complaints.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 space-y-3">
          <AlertCircle className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="font-bold text-base text-slate-800">
            {t('feed.no_complaints')}
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Be the first citizen to report a problem in this area with tamper-evident proof.
          </p>
          <button
            onClick={onNavigateNew}
            className="px-4 py-2 bg-saffron-600 text-white rounded-xl text-xs font-bold shadow"
          >
            {t('hero.cta_file')}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {complaints.map((c) => (
            <ComplaintCard
              key={c.id}
              complaint={c}
              onSelect={onSelectComplaint}
              onCoSignSuccess={loadComplaints}
            />
          ))}
        </div>
      )}

    </div>
  );
}
