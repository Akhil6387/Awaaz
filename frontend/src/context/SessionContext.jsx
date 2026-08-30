import React, { createContext, useContext, useState, useEffect } from 'react';

const SessionContext = createContext();

export function SessionProvider({ children }) {
  const [sessionId, setSessionId] = useState('');
  const [myComplaints, setMyComplaints] = useState([]);
  const [myCoSigns, setMyCoSigns] = useState([]);

  useEffect(() => {
    let currentSession = localStorage.getItem('awaaz_anon_id');
    if (!currentSession) {
      currentSession = 'anon_' + crypto.randomUUID();
      localStorage.setItem('awaaz_anon_id', currentSession);
    }
    setSessionId(currentSession);

    const filed = JSON.parse(localStorage.getItem('awaaz_my_filed') || '[]');
    setMyComplaints(filed);

    const cosigned = JSON.parse(localStorage.getItem('awaaz_my_cosigns') || '[]');
    setMyCoSigns(cosigned);
  }, []);

  const trackFiledComplaint = (complaint) => {
    const updated = [complaint, ...myComplaints.filter(c => c.public_id !== complaint.public_id)];
    setMyComplaints(updated);
    localStorage.setItem('awaaz_my_filed', JSON.stringify(updated));
  };

  const trackCoSign = (complaintId) => {
    if (!myCoSigns.includes(complaintId)) {
      const updated = [...myCoSigns, complaintId];
      setMyCoSigns(updated);
      localStorage.setItem('awaaz_my_cosigns', JSON.stringify(updated));
    }
  };

  const hasCoSigned = (complaintId) => {
    return myCoSigns.includes(complaintId);
  };

  return (
    <SessionContext.Provider value={{
      sessionId,
      myComplaints,
      myCoSigns,
      trackFiledComplaint,
      trackCoSign,
      hasCoSigned
    }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  return useContext(SessionContext);
}
