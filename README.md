# 📢 Awaaz (आवाज़) — Civic Complaint & Public Accountability Layer

> **"Your Voice. Live Proof. Public Accountability."**  
> *A no-login, evidence-first civic grievance platform bridging rural Gram Panchayats and urban Municipal Corporations.*

---

## 🌟 Overview & Philosophy

**Awaaz** is designed from first principles as an open public evidence and accountability layer sitting on top of existing government grievance systems (such as Nagar Nigam 311 portals, CM Helpline 181, and Panchayat channels). It solves the three fundamental barriers citizens face when reporting civic issues in India:

1. **Retribution & Privacy Fear (100% No-Login Required)**:
   Citizens can report and track complaints completely anonymously without creating an account or providing phone/email upfront. Client-side cryptographic UUID sessions (`awaaz_anon_id`) keep personal tracking seamless in the browser.
2. **Disinformation & Fake Claims (Live Camera/Audio Proof Only)**:
   Gallery uploads are disabled. Citizens capture live photos, videos, and voice notes directly via in-browser `getUserMedia`. Every submission is stamped with server-side computed **SHA-256 cryptographic hashes** and immutable GPS timestamps.
3. **Rural & Urban Parity**:
   Gram Panchayats (Sarpanch/Sachiv/Panch) and Urban Municipalities (Ward Corporator/Mayor/Zone Engineer) are treated as equal first-class citizens with config-driven administrative hierarchies.

---

## 🚀 Key Features

- **Anonymous Complaint Filing**: 5-step intuitive wizard with live photo/voice-note capture, GPS pin-drop, and optional identity reveal.
- **Duplicate & Proximity Detection**: Spatial Haversine distance bounding-box search prompts citizens to co-sign existing nearby issues rather than fragmenting community focus.
- **"I Face This Too" Co-Signing**: Pressure counter mechanism with anonymous session deduplication.
- **Tamper-Evident Dossiers**: Public dockets (`AWZ-2026-XXXX`) display SHA-256 evidence integrity badges and verified timestamps.
- **Bilingual Interface**: Full Hindi (हिंदी) and English support out of the box with one-click toggling.
- **Interactive Geo-Map**: Leaflet-powered visual map with status/category pins and cluster inspection.
- **Automatic RTI & Grievance Petition Generator**: Generates formal bilingual grievance letters with legal references and verified co-signer numbers.
- **Community Moderation Desk**: Review queue for monitoring official conduct claims, filtering defamation, and approving public feed entries.
- **Transparent Audit Trail**: Immutable log of every status transition (`FILED` → `UNDER_REVIEW` → `ACKNOWLEDGED` → `IN_PROGRESS` → `RESOLVED`).

---

## 🏗️ Architecture

```
awaaz/
├── backend/                  # Django 5.x + Django REST Framework + CORS
│   ├── awaaz_backend/        # Project settings, root URL routing, WSGI/ASGI
│   ├── apps/
│   │   ├── core/             # Utility functions (SHA-256 hashing, Haversine spatial math)
│   │   ├── config_engine/    # Dynamic categories, area types, durations, channels
│   │   ├── authorities/      # States, Districts, Administrative Units & Public Authorities
│   │   ├── complaints/       # Complaints, Live Evidence, Co-Signs, Audit Trails, Tests
│   │   ├── moderation/       # Flagging system, Moderation Review Desk
│   │   ├── escalation/       # Formal Grievance & RTI petition text generators
│   │   └── seed/             # Pilot seed data command (Bhopal/Sehore pilot region)
│   └── manage.py
│
└── frontend/                 # Vite + React 18 + Tailwind CSS + Lucide Icons + Leaflet
    ├── src/
    │   ├── components/       # CameraCapture, AudioCapture, MapPicker, ComplaintCard, etc.
    │   ├── context/          # SessionContext (Zero-auth UUID local tracker)
    │   ├── i18n/             # en.json, hi.json, i18n configuration
    │   ├── pages/            # FeedPage, NewComplaintPage, DetailPage, MyComplaints, Moderation
    │   ├── services/         # API client layer for backend endpoints
    │   ├── App.jsx           # Main tab navigation and view orchestration
    │   └── main.jsx
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.js
```

---

## ⚡ Quickstart & Running Locally

### 1. Backend Setup (Django)

```bash
cd backend

# Run migrations
python manage.py migrate

# Seed realistic pilot data (Categories, Units, pilot complaints, evidence)
python manage.py seed_awaaz_data

# Run Django development server (Port 8000)
python manage.py runserver 8000
```

*Django Admin & Superuser Credentials:*
- URL: `http://127.0.0.1:8000/admin/`
- Username: `admin`
- Password: `admin123`

---

### 2. Frontend Setup (React + Vite)

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server (Port 5173)
npm run dev
```

Open your browser at: `http://localhost:5173/`

---

## 🧪 Automated Test Suite

Run the comprehensive backend test suite verifying SHA-256 hashing, Haversine geospatial proximity, anonymous filing, co-signing idempotency, and RTI generation:

```bash
cd backend
python manage.py test
```

---

## 🛡️ Moderation & Legal Policy

- **Physical Infrastructure Focus**: Complaints about broken roads, contaminated water, lack of electricity, uncollected trash, or defunct government schools are auto-fast-tracked.
- **Defamation Safeguard**: Grievances naming individuals or alleging bribery undergo mandatory reviewer verification before public broadcast.
- **Evidentiary Standard**: SHA-256 checksums and UTC timestamps ensure dossiers are suitable for submission to District Collectors, RTI Petitions, or High Court PILs.
