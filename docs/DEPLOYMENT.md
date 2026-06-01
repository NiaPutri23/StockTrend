# StockTrend Dashboard - Deployment Guide (Public Access)

Panduan lengkap untuk membuat aplikasi StockTrend Dashboard dapat diakses oleh publik secara online.

## 📋 Daftar Isi

- [Opsi Deployment](#opsi-deployment)
- [Streamlit Cloud (Recommended)](#streamlit-cloud-recommended)
- [Heroku Deployment](#heroku-deployment)
- [AWS EC2 Deployment](#aws-ec2-deployment)
- [Google Cloud Platform](#google-cloud-platform)
- [Domain & DNS Setup](#domain--dns-setup)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🌐 Opsi Deployment

| Platform | Cost | Setup Time | Ease | Best For |
|----------|------|-----------|------|----------|
| **Streamlit Cloud** | Free | 5 min | ⭐⭐⭐⭐⭐ | Quick public demo |
| **Heroku** | Free/Paid | 15 min | ⭐⭐⭐⭐ | Small projects |
| **AWS EC2** | Paid | 30 min | ⭐⭐⭐ | Production scale |
| **GCP Cloud Run** | Free tier | 20 min | ⭐⭐⭐⭐ | Scalable, serverless |
| **DigitalOcean** | $5/mo | 15 min | ⭐⭐⭐⭐ | Affordable VPS |
| **PythonAnywhere** | Free/Paid | 10 min | ⭐⭐⭐⭐ | Python-focused |

---

## 🚀 Streamlit Cloud (Recommended)

**Kelebihan:**
- ✅ Gratis untuk public app
- ✅ Auto-deploy dari GitHub
- ✅ HTTPS included
- ✅ 1-click deployment
- ✅ Managed infrastructure

**Kekurangan:**
- ❌ Public hanya (tidak private)
- ❌ Memory terbatas (1GB)
- ❌ Tidak bisa run background jobs
- ❌ Tidak bisa simpan data permanent

### Step 1: Persiapkan Repository di GitHub

**1a. Create GitHub Account**
- Go to https://github.com/signup
- Complete registration

**1b. Create New Repository**
- Click "+" → "New repository"
- Repository name: `stockTrend-dashboard`
- Description: "Indonesian Stock Screener Dashboard"
- Public (wajib untuk free tier)
- Click "Create repository"

**1c. Push Code ke GitHub**

```bash
# Buka terminal di project folder
cd c:\Project\stockTrend-dashboard

# Initialize git (jika belum)
git init
git add .
git commit -m "Initial commit - StockTrend Dashboard"

# Tambahkan remote
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stockTrend-dashboard.git

# Push ke GitHub
git push -u origin main
```

**Ganti `YOUR_USERNAME` dengan username GitHub Anda**

### Step 2: Deploy ke Streamlit Cloud

**2a. Connect GitHub ke Streamlit Cloud**
- Go to https://streamlit.io/cloud
- Click "Sign up"
- Click "Continue with GitHub"
- Authorize Streamlit

**2b. Deploy App**
- Click "New app"
- Select repository: `stockTrend-dashboard`
- Select branch: `main`
- Select main file path: `app.py`
- Click "Deploy"

**Setup akan berjalan ~2-3 menit**

### Step 3: Configure App Settings

**3a. Access Settings**
- Click menu (hamburger icon) → Settings
- Jika diminta, authorize GitHub

**3b. Configure App Settings**

```yaml
# Advanced settings
[client]
showErrorDetails = false

[server]
port = 8501
headless = true
```

**3c. Set Memory & Resources** (Optional)
- Default: 1GB RAM, 30 menit timeout
- Cukup untuk screening 50-100 ticker

### Step 4: Access Your App

**App akan tersedia di:**
```
https://stocktrend-dashboard.streamlit.app
```

**Bagikan URL ini ke publik!**

### Step 5: Update & Auto-Deploy

**Setiap kali push ke GitHub:**
```bash
# Edit file
# ...

# Commit & push
git add .
git commit -m "Update screening logic"
git push origin main
```

**Streamlit akan auto-redeploy dalam 1-2 menit**

### Troubleshooting Streamlit Cloud

**Problem: "FileNotFoundError"**
```python
# ❌ WRONG - Absolute path won't work
with open("C:\data\prices.csv"):
    pass

# ✅ CORRECT - Relative path
import os
from pathlib import Path

data_dir = Path(__file__).parent / "data"
```

**Problem: "Requirements not found"**
- Ensure `requirements.txt` di root folder
- Check file is named exactly `requirements.txt` (case-sensitive)

**Problem: "App exceeds memory limit"**
- Reduce data period: `period="1mo"` instead of `"3mo"`
- Implement database untuk caching
- Limit max tickers: `MAX_TICKERS = 50`

---

## 💻 Heroku Deployment

**Setup time: ~15 menit**

### Step 1: Prepare for Heroku

**1a. Create Heroku Account**
- Go to https://www.heroku.com
- Sign up & verify email

**1b. Install Heroku CLI**
```bash
# Download dari https://devcenter.heroku.com/articles/heroku-cli
# Atau dengan chocolatey:
choco install heroku-cli

# Verify installation
heroku --version
```

**1c. Create Procfile**
Create file `Procfile` di root folder:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**1d. Create setup.sh**
Create file `setup.sh` di root folder:

```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = \$PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

### Step 2: Deploy to Heroku

**2a. Login ke Heroku**
```bash
heroku login
# Browser akan terbuka untuk login
```

**2b. Create Heroku App**
```bash
# Di project folder
heroku create stocktrend-dashboard

# Verify
heroku apps:list
```

**2c. Deploy**
```bash
git push heroku main
```

**Deployment akan berjalan ~3-5 menit**

### Step 3: Access App

```
https://stocktrend-dashboard.herokuapp.com
```

### Step 4: Setup Auto-Deploy (Optional)

```bash
# Enable auto-deploy dari GitHub
heroku pipelines:create stocktrend-dashboard

# Atau manual deploy setiap kali push
git push heroku main
```

---

## ☁️ AWS EC2 Deployment

**Setup time: ~30 menit**
**Cost: Free tier (12 bulan) atau $0.0116/jam**

### Step 1: Create EC2 Instance

**1a. Go to AWS Console**
- https://console.aws.amazon.com
- Go to EC2 dashboard

**1b. Launch Instance**
- Click "Launch Instance"
- Select: Ubuntu Server 22.04 LTS (Free tier eligible)
- Instance type: t2.micro (Free)
- Click "Next: Configure Instance Details"

**1c. Configure Security**
- Go to "6. Configure Security Group"
- Add rules:
  - HTTP (80) - anywhere (0.0.0.0/0)
  - HTTPS (443) - anywhere
  - SSH (22) - your IP
- Launch instance

**1d. Download Key Pair**
- Save `.pem` file securely
- Permissions: `chmod 400 your-key.pem`

### Step 2: Connect to Instance

```bash
# SSH ke instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Atau gunakan EC2 Instance Connect di AWS Console
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & pip
sudo apt install -y python3-pip python3-venv

# Install git
sudo apt install -y git

# Clone repository
git clone https://github.com/YOUR_USERNAME/stockTrend-dashboard.git
cd stockTrend-dashboard
```

### Step 4: Setup Application

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install gunicorn & streamlit server
pip install gunicorn streamlit
```

### Step 5: Create Systemd Service

Create file `/etc/systemd/system/stocktrend.service`:

```ini
[Unit]
Description=StockTrend Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/stockTrend-dashboard
ExecStart=/home/ubuntu/stockTrend-dashboard/venv/bin/streamlit run app.py --server.port=80
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Enable & start service
sudo systemctl enable stocktrend
sudo systemctl start stocktrend
sudo systemctl status stocktrend
```

### Step 6: Setup Reverse Proxy (Nginx)

```bash
# Install Nginx
sudo apt install -y nginx

# Create config file
sudo nano /etc/nginx/sites-available/stocktrend
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/stocktrend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Setup SSL (HTTPS)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com

# Auto-renew
sudo systemctl enable certbot.timer
```

---

## 🌩️ Google Cloud Platform (Cloud Run)

**Setup time: ~20 menit**
**Cost: Free tier (2M requests/bulan)**

### Step 1: Prepare Docker

Create `Dockerfile` di root folder:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080"]
```

Create `.dockerignore`:

```
venv/
__pycache__/
*.pyc
.git/
.gitignore
```

### Step 2: Deploy to Cloud Run

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

gcloud init
gcloud config set project YOUR_PROJECT_ID

# Deploy
gcloud run deploy stocktrend-dashboard \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated
```

**App akan tersedia di:**
```
https://stocktrend-dashboard-xxxx-as.a.run.app
```

---

## 🌐 Domain & DNS Setup

### Register Domain

Pilih registrar (cheap options):
- Namecheap: $0.88/year (promo)
- Google Domains: $12/year
- GoDaddy: $1/year (promo)

### Point Domain ke App

**Untuk Streamlit Cloud:**
- Domain registrar → DNS settings
- Add CNAME record:
  ```
  Host: @ (atau www)
  Type: CNAME
  Value: stocktrend-dashboard.streamlit.app
  TTL: 3600
  ```

**Untuk AWS/GCP:**
- Get public IP dari instance
- Add A record:
  ```
  Host: @
  Type: A
  Value: YOUR_PUBLIC_IP
  TTL: 3600
  ```

### Setup Custom Domain (Streamlit)

```bash
# Di Streamlit dashboard
Settings → General → Custom domain

# Enter your domain
stocktrend.example.com
```

---

## 📊 Monitoring & Maintenance

### Setup Uptime Monitoring

**Using Uptime Robot (Free):**
1. Go to https://uptimerobot.com
2. Sign up
3. Add monitor:
   - URL: https://your-app-url
   - Check interval: 5 minutes
   - Alert email: your-email
4. Get alerts jika app down

### View Logs

**Streamlit Cloud:**
- Dashboard → App logs

**Heroku:**
```bash
heroku logs --tail
```

**AWS EC2:**
```bash
sudo journalctl -u stocktrend -f
```

### Performance Monitoring

**Add telemetry (Optional):**

```python
# app.py
import streamlit as st
from datetime import datetime

# Log screening execution time
import time

start_time = time.time()
# ... screening code ...
elapsed_time = time.time() - start_time

# Log ke file
with open("metrics.log", "a") as f:
    f.write(f"{datetime.now()},{elapsed_time:.2f}s\n")
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

```python
# ❌ BAD
API_KEY = "abc123secret"

# ✅ GOOD
import os
API_KEY = os.getenv("API_KEY")
```

Create `.env` file (local only):
```
API_KEY=your_secret_key
```

Add to `.gitignore`:
```
.env
```

### 2. Restrict Access (Optional)

```python
# app.py - Require password
import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""
    
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if st.session_state.password_correct:
        return True
    
    # Not yet logged in, show inputs for login.
    with st.form("credentials_form"):
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if password == "secret_password":
                st.session_state.password_correct = True
                return True
            else:
                st.error("😕 password incorrect")
                return False
    
    return False

if not check_password():
    st.stop()

# Rest of app only visible if logged in
render_dashboard()
```

### 3. Rate Limiting

```python
# Prevent abuse
import time
from functools import wraps

MAX_REQUESTS_PER_MINUTE = 10
request_times = []

def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global request_times
        now = time.time()
        
        # Remove old requests
        request_times = [t for t in request_times if now - t < 60]
        
        if len(request_times) >= MAX_REQUESTS_PER_MINUTE:
            st.error("⚠️ Too many requests. Please wait.")
            return None
        
        request_times.append(now)
        return func(*args, **kwargs)
    
    return wrapper

@rate_limit
def run_screening():
    # Screening code
    pass
```

---

## 📈 Scaling untuk Traffic Tinggi

Jika aplikasi dapat traffic tinggi:

### 1. Gunakan Database

```python
# Ganti in-memory caching dengan database
import sqlite3

@st.cache_data(ttl=3600)
def get_stock_data_cached(ticker):
    conn = sqlite3.connect('stock_data.db')
    
    # Check if data exists in database
    query = f"SELECT * FROM stocks WHERE ticker = '{ticker}'"
    df = pd.read_sql(query, conn)
    
    if len(df) > 0:
        return df
    
    # Fetch dari API jika tidak ada
    df = yf.download(ticker, period="3mo")
    df.to_sql('stocks', conn, if_exists='append')
    
    return df
```

### 2. Implement Queue System

```python
# Gunakan Celery untuk background jobs
from celery import Celery

app = Celery('stocktrend')

@app.task
def screen_stocks_background(tickers, n_days):
    # Long-running screening
    results = screen_stocks(tickers, n_days)
    save_to_database(results)
    send_email_notification(results)
```

### 3. CDN untuk Static Files

```bash
# Upload static files ke CloudFront/CloudFlare
# Serve dari CDN untuk faster access
```

---

## 🆘 Troubleshooting Deployment

### Problem: App crashes after 5 minutes

**Solution:**
- Increase timeout: `--client.maxMessageSize=200`
- Reduce data period
- Implement streaming results

### Problem: "Module not found" error

**Solution:**
```bash
# Ensure all dependencies di requirements.txt
pip freeze > requirements.txt

# Push & redeploy
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Problem: "Out of memory" error

**Solution:**
- Reduce cache: `@st.cache_data(ttl=600)` (10 min)
- Limit tickers: `MAX_TICKERS = 50`
- Upgrade instance type

### Problem: Slow performance

**Solution:**
- Enable caching
- Implement batch processing
- Use database instead of API

---

## 📊 Deployment Comparison Table

| Aspect | Streamlit Cloud | Heroku | AWS EC2 |
|--------|-----------------|--------|---------|
| **Setup Time** | 5 min | 15 min | 30 min |
| **Cost** | Free | Free/Paid | Free tier/Paid |
| **Ease** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Scalability** | Limited | Medium | High |
| **Auto Deploy** | ✅ | ✅ | Manual |
| **Custom Domain** | ✅ | ✅ | ✅ |
| **SSL/HTTPS** | ✅ | ✅ | Need setup |
| **Public Access** | ✅ | ✅ | ✅ |
| **Private Option** | ✅ | ✅ | ✅ |

---

## ✅ Post-Deployment Checklist

- [ ] App accessible di public URL
- [ ] GitHub repo linked
- [ ] Auto-deploy working
- [ ] Custom domain configured
- [ ] SSL/HTTPS enabled
- [ ] Uptime monitoring active
- [ ] Error logging configured
- [ ] Performance acceptable (< 5s load)
- [ ] Mobile responsive
- [ ] Share URL dengan users/investors

---

## 📞 Quick Links

- **Streamlit Cloud**: https://streamlit.io/cloud
- **Heroku**: https://www.heroku.com/
- **AWS**: https://aws.amazon.com/ec2/
- **GCP**: https://cloud.google.com/run
- **GitHub**: https://github.com

---

**Aplikasi Anda sekarang PUBLIC dan dapat diakses siapa saja! 🌍**

Last Updated: June 2026
