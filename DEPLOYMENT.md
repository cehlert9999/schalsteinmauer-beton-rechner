# 🚀 Deployment Guide - MauerPlaner Online bringen

## Option 1: Streamlit Cloud (EMPFOHLEN - Kostenlos!)

### Vorteile
- ✅ Komplett kostenlos für öffentliche Apps
- ✅ Automatisches Deployment aus GitHub
- ✅ SSL/HTTPS inklusive
- ✅ Keine Server-Verwaltung nötig
- ✅ Automatische Updates bei Git-Push

### Schritt-für-Schritt Anleitung

#### 1. GitHub Repository erstellen

**A) Neues Repository auf GitHub:**
```
1. Gehe zu https://github.com
2. Klicke auf "New Repository"
3. Name: z.B. "betonkalk"
4. Public (für kostenloses Hosting)
5. Create Repository
```

**B) Code hochladen:**
```bash
cd "C:\Users\cehle\Documents\python\schalsteinmauer beton rechner"

# Git initialisieren (falls noch nicht geschehen)
git init

# Alle Dateien hinzufügen
git add .

# Commit erstellen
git commit -m "Initial commit - MauerPlaner by LEANOFY"

# Mit GitHub verbinden (ersetze USERNAME und REPO-NAME)
git remote add origin https://github.com/USERNAME/mauerplaner.git

# Hochladen
git branch -M main
git push -u origin main
```

#### 2. Streamlit Cloud Deployment

**A) Bei Streamlit Cloud anmelden:**
1. Gehe zu https://share.streamlit.io
2. "Sign up" mit GitHub-Account
3. Autorisiere Streamlit

**B) App deployen:**
1. Klicke "New app"
2. Wähle dein Repository: `USERNAME/mauerplaner`
3. Branch: `main`
4. Main file path: `app.py`
5. App URL wählen (z.B. `mauerplaner`)
6. Klicke "Deploy!"

**C) Fertig!**
- Deine App ist jetzt online unter: `https://mauerplaner.streamlit.app`
- Automatische Updates bei jedem Git-Push

#### 3. Custom Domain einrichten (Subdomain)

**A) DNS bei deinem Provider (z.B. bei LEANOFY-Hosting):**
```
Typ: CNAME
Name: mauerplaner (oder dein Subdomain-Name)
Ziel: mauerplaner.streamlit.app
TTL: 3600
```

**B) In Streamlit Cloud (App Settings):**
1. Öffne deine App auf Streamlit Cloud
2. Klicke auf "⚙️ Settings"
3. Gehe zu "Custom domains"
4. Füge hinzu: `mauerplaner.leanofy.de`
5. Folge den Anweisungen zur Verifizierung

**Ergebnis:** App läuft unter `https://mauerplaner.leanofy.de` 🎉

---

## Option 2: Eigener Server (VPS/Cloud)

### Wenn du mehr Kontrolle brauchst

#### A) Mit Docker (Empfohlen)

**1. Erstelle Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**2. Docker Compose (optional):**
```yaml
# docker-compose.yml
version: '3.8'

services:
  mauerplaner:
    build: .
    ports:
      - "8501:8501"
    restart: unless-stopped
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
```

**3. Deployen:**
```bash
# Bauen
docker build -t mauerplaner .

# Starten
docker run -d -p 8501:8501 --name mauerplaner mauerplaner

# Oder mit Docker Compose
docker-compose up -d
```

**4. Nginx Reverse Proxy (für HTTPS):**
```nginx
server {
    listen 80;
    server_name mauerplaner.leanofy.de;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mauerplaner.leanofy.de;

    ssl_certificate /etc/letsencrypt/live/mauerplaner.leanofy.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mauerplaner.leanofy.de/privkey.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### B) Direkt auf Linux VPS

**1. Server vorbereiten:**
```bash
# Updates
sudo apt update && sudo apt upgrade -y

# Python und Dependencies
sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx -y

# Projekt hochladen
cd /var/www
sudo git clone https://github.com/USERNAME/mauerplaner.git
cd mauerplaner

# Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Systemd Service erstellen:**
```ini
# /etc/systemd/system/mauerplaner.service
[Unit]
Description=MauerPlaner Streamlit App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/mauerplaner
Environment="PATH=/var/www/mauerplaner/venv/bin"
ExecStart=/var/www/mauerplaner/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

**3. Service starten:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable mauerplaner
sudo systemctl start mauerplaner
```

**4. SSL mit Let's Encrypt:**
```bash
sudo certbot --nginx -d mauerplaner.leanofy.de
```

---

## Option 3: Cloud-Plattformen

### Heroku (Einfach, aber kostenpflichtig)

**1. Procfile erstellen:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**2. Deployen:**
```bash
heroku login
heroku create mauerplaner
git push heroku main
heroku open
```

### Railway.app (Günstig)

1. Gehe zu https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Wähle Repository
4. Railway erkennt automatisch Streamlit
5. Custom Domain in Settings hinzufügen

### Render.com (Kostenlos für Start)

1. Gehe zu https://render.com
2. "New Web Service"
3. Verbinde GitHub
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `streamlit run app.py --server.port=10000 --server.address=0.0.0.0`

---

## 🔒 Sicherheits-Checkliste

Vor dem Online-Gehen:

- [ ] **Admin-Passwort ändern** in `pages/1_⚙️_Admin.py`
- [ ] **Secrets auslagern** (kein Passwort im Code)
- [ ] **HTTPS aktiviert** (SSL-Zertifikat)
- [ ] **Rate Limiting** (gegen Missbrauch)
- [ ] **Backups** der config.yaml einrichten
- [ ] **Monitoring** (Uptime-Check)
- [ ] **Analytics** (optional, z.B. Google Analytics)

### Admin-Passwort sichern

**Mit Streamlit Secrets:**
```toml
# .streamlit/secrets.toml (NICHT in Git!)
admin_password = "IhrSicheresPasswort123!"
```

**In Admin-Seite anpassen:**
```python
import streamlit as st

# Passwort aus Secrets
admin_password = st.secrets.get("admin_password", "admin123")

if password == admin_password:
    st.session_state.admin_authenticated = True
```

---

## 📊 Nach dem Deployment

### Monitoring & Analytics

**1. Uptime-Monitoring:**
- https://uptimerobot.com (kostenlos)
- Prüft alle 5 Min ob App erreichbar ist

**2. Analytics (optional):**
```python
# In app.py ganz oben
import streamlit.components.v1 as components

# Google Analytics
components.html("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", height=0)
```

**3. Fehler-Tracking:**
- Sentry.io für Error-Tracking
- Streamlit Cloud hat eingebautes Logging

### Performance-Optimierung

**1. Caching nutzen:**
```python
@st.cache_data
def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)
```

**2. Lazy Loading für 3D:**
- 3D-Visualisierung nur bei Bedarf laden
- Schon implementiert ✅

---

## 🎯 Empfohlener Workflow

### Für LEANOFY:

1. **Jetzt:** Streamlit Cloud (kostenlos, schnell)
2. **Code auf GitHub:** Öffentlich oder privat
3. **Subdomain:** `betonkalk.leanofy.de` via CNAME
4. **Updates:** Einfach Git-Push → Automatisches Update
5. **Admin:** Passwort in Streamlit Secrets

### Domain-Setup bei LEANOFY:

```
DNS-Einträge für mauerplaner.leanofy.de:

CNAME: mauerplaner → mauerplaner.streamlit.app
```

---

## 🚀 Quick-Start (5 Minuten)

```bash
# 1. GitHub Repository erstellen
# 2. Code hochladen
cd "C:\Users\cehle\Documents\python\schalsteinmauer beton rechner"
git init
git add .
git commit -m "MauerPlaner by LEANOFY"
git remote add origin https://github.com/LEANOFY/mauerplaner.git
git push -u origin main

# 3. Streamlit Cloud
# → https://share.streamlit.io
# → New app → mauerplaner → Deploy!

# 4. Fertig!
# → App läuft online 🎉
```

---

## 📞 Support

Bei Problemen:
1. Streamlit Docs: https://docs.streamlit.io
2. Streamlit Forum: https://discuss.streamlit.io
3. GitHub Issues erstellen

---

**Viel Erfolg mit dem Deployment! 🚀**

*MauerPlaner by LEANOFY - Professionelle Betonbedarfsberechnung*

