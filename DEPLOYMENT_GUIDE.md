# 🌐 How to Take Awaaz (आवाज़) Live into Production

This guide covers everything you need to deploy **Awaaz** to the internet so citizens on smartphones and computers across India can access it.

---

## ⚠️ Crucial Requirement for Live Citizen Access (HTTPS / SSL)

> [!IMPORTANT]
> **HTTPS is mandatory in production.**  
> Modern mobile web browsers (Chrome, Safari, Firefox, Brave) **block in-browser Camera and Microphone access** (`getUserMedia`) and **GPS Geolocation** on unencrypted HTTP connections (except `localhost`).  
> **You must deploy Awaaz over HTTPS / SSL** so users on smartphones in villages and cities can take live photos and voice-notes.

---

## 🚀 Option 1: Free & Fast Cloud Deployment (Recommended for Quick Launch)

You can host both the frontend and backend with **free HTTPS and global CDN** in under 10 minutes:

### 1. Backend on Render.com (or Railway.app / Fly.io)
1. Push your repository to **GitHub**.
2. Go to [Render.com](https://render.com) and create a **New Web Service**:
   - Connect your GitHub repo.
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py seed_awaaz_data`
   - Start Command: `gunicorn awaaz_backend.wsgi:application --bind 0.0.0.0:$PORT`
3. In **Environment Variables**:
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(Generate a secure random string)*
   - `ALLOWED_HOSTS`: `*` (or your Render domain `your-backend.onrender.com`)
   - `CORS_ALLOW_ALL_ORIGINS`: `True` (or your frontend domain)
4. Click **Deploy**. Render gives you a live HTTPS URL (e.g. `https://awaaz-api.onrender.com`).

---

### 2. Frontend on Vercel (or Cloudflare Pages / Netlify)
1. Go to [Vercel.com](https://vercel.com) and click **Add New Project**.
2. Connect your GitHub repository.
3. Configure Project Settings:
   - Root Directory: `frontend`
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Add Environment Variable:
   - `VITE_API_BASE`: `https://awaaz-api.onrender.com/api/v1` *(Replace with your backend Render URL)*
5. Click **Deploy**. Vercel will build and assign you a free HTTPS custom domain (e.g. `https://awaaz.vercel.app`).

---

## 🐳 Option 2: 1-Click Production VPS Deployment (Docker Compose)

For complete control and low latency in India (e.g. **AWS Mumbai `ap-south-1`**, **DigitalOcean Bangalore**, or **Hetzner**):

### 1. Provision a VPS
- Ubuntu 22.04 / 24.04 LTS ($4–$6/month droplet).
- Install Docker & Docker Compose:
  ```bash
  sudo apt update && sudo apt install -y docker.io docker-compose git
  ```

### 2. Clone and Launch
```bash
git clone <your-repo-url> awaaz
cd awaaz

# Run the complete stack (PostgreSQL + Django Gunicorn + Vite Nginx)
docker-compose up -d --build
```

### 3. Add Free SSL Certificate with Certbot / Let's Encrypt
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.in -d www.yourdomain.in
```

---

## 📱 Verifying Live Citizen Experience
Once live:
1. Open the URL on your mobile phone (`https://yourdomain.in` or `https://awaaz.vercel.app`).
2. Click **"Report Problem"** (`समस्या दर्ज करें`).
3. Allow camera and microphone permissions when prompted.
4. Snap a photo of a real-world issue, pin the location, and hit **Submit**!
