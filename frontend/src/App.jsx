import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import FeedPage from './pages/FeedPage';
import NewComplaintPage from './pages/NewComplaintPage';
import ComplaintDetailPage from './pages/ComplaintDetailPage';
import MyComplaintsPage from './pages/MyComplaintsPage';
import ModerationPortalPage from './pages/ModerationPortalPage';
import AboutPage from './pages/AboutPage';
import { SessionProvider } from './context/SessionContext';

export default function App() {
  const [activeTab, setActiveTab] = useState('feed'); // 'feed', 'new_complaint', 'detail', 'my_complaints', 'moderation', 'about'
  const [selectedComplaintId, setSelectedComplaintId] = useState(null);

  const handleSelectComplaint = (id) => {
    setSelectedComplaintId(id);
    setActiveTab('detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleComplaintCreated = (created) => {
    setSelectedComplaintId(created.id);
    setActiveTab('detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <SessionProvider>
      <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between">
        
        <Navbar 
          activeTab={activeTab} 
          setActiveTab={(tab) => {
            setActiveTab(tab);
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }} 
        />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8 flex-1 w-full">
          {activeTab === 'feed' && (
            <FeedPage
              onSelectComplaint={handleSelectComplaint}
              onNavigateNew={() => setActiveTab('new_complaint')}
            />
          )}

          {activeTab === 'new_complaint' && (
            <NewComplaintPage
              onComplaintCreated={handleComplaintCreated}
              onCancel={() => setActiveTab('feed')}
              onSelectExisting={handleSelectComplaint}
            />
          )}

          {activeTab === 'detail' && (
            <ComplaintDetailPage
              complaintId={selectedComplaintId}
              onBack={() => setActiveTab('feed')}
              onSelectOther={handleSelectComplaint}
            />
          )}

          {activeTab === 'my_complaints' && (
            <MyComplaintsPage
              onSelectComplaint={handleSelectComplaint}
              onNavigateNew={() => setActiveTab('new_complaint')}
            />
          )}

          {activeTab === 'moderation' && (
            <ModerationPortalPage
              onSelectComplaint={handleSelectComplaint}
            />
          )}

          {activeTab === 'about' && (
            <AboutPage />
          )}
        </main>

        <Footer setActiveTab={setActiveTab} />

      </div>
    </SessionProvider>
  );
}
