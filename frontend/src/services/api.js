const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api/v1';

export async function fetchBootstrapConfig() {
  const res = await fetch(`${API_BASE}/config/bootstrap/`);
  if (!res.ok) throw new Error('Failed to fetch platform config');
  return res.json();
}

export async function fetchAdministrativeUnits(params = {}) {
  const query = new URLSearchParams(params).toString();
  const url = query ? `${API_BASE}/admin-units/?${query}` : `${API_BASE}/admin-units/`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch administrative units');
  return res.json();
}

export async function suggestUnitByCoords(lat, lng, areaType) {
  const res = await fetch(`${API_BASE}/admin-units/suggest_by_coords/?lat=${lat}&lng=${lng}&area_type=${areaType || ''}`);
  if (!res.ok) return null;
  return res.json();
}

export async function fetchComplaints(params = {}) {
  const query = new URLSearchParams(params).toString();
  const url = query ? `${API_BASE}/complaints/?${query}` : `${API_BASE}/complaints/`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch complaints');
  return res.json();
}

export async function fetchComplaintDetail(id) {
  const res = await fetch(`${API_BASE}/complaints/${id}/`);
  if (!res.ok) throw new Error('Failed to fetch complaint detail');
  return res.json();
}

export async function checkDuplicates(lat, lng, categoryId, radius = 500) {
  const res = await fetch(`${API_BASE}/complaints/check-duplicates/?lat=${lat}&lng=${lng}&category_id=${categoryId || ''}&radius=${radius}`);
  if (!res.ok) return { duplicates: [], count: 0 };
  return res.json();
}

export async function submitComplaint(formData) {
  const res = await fetch(`${API_BASE}/complaints/`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.description?.[0] || errorData.title?.[0] || 'Failed to submit complaint');
  }
  return res.json();
}

export async function coSignComplaint(complaintId, sessionId, comment = '') {
  const res = await fetch(`${API_BASE}/complaints/${complaintId}/co_sign/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ anonymous_session_id: sessionId, comment }),
  });
  if (!res.ok) throw new Error('Failed to co-sign complaint');
  return res.json();
}

export async function generateEscalationLetter(complaintId, lang = 'hi') {
  const res = await fetch(`${API_BASE}/escalation/generate_letter/?complaint_id=${complaintId}&lang=${lang}`);
  if (!res.ok) throw new Error('Failed to generate escalation letter');
  return res.json();
}

export async function flagComplaint(complaintId, reason, explanation, sessionId) {
  const res = await fetch(`${API_BASE}/moderation/flag_complaint/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      complaint_id: complaintId,
      reason,
      explanation,
      anonymous_session_id: sessionId
    }),
  });
  if (!res.ok) throw new Error('Failed to flag complaint');
  return res.json();
}

export async function fetchModerationQueue(status = 'PENDING') {
  const res = await fetch(`${API_BASE}/moderation/queue/?status=${status}`);
  if (!res.ok) throw new Error('Failed to fetch moderation queue');
  return res.json();
}

export async function reviewModerationComplaint(complaintId, action, notes, moderatorName) {
  const res = await fetch(`${API_BASE}/moderation/${complaintId}/review_action/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, notes, moderator_name: moderatorName }),
  });
  if (!res.ok) throw new Error('Failed to review complaint');
  return res.json();
}
