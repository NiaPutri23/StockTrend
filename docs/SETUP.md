# StockTrend Dashboard - Setup & Installation Guide

Panduan lengkap untuk setup dan menjalankan aplikasi StockTrend Dashboard secara lokal.

## 📋 Daftar Isi

- [System Requirements](#system-requirements)
- [Quick Start (5 Menit)](#quick-start-5-menit)
- [Instalasi Detail](#instalasi-detail)
- [Troubleshooting](#troubleshooting)
- [Tips & Tricks](#tips--tricks)

---

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Windows 7+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.11 atau lebih tinggi
- **RAM**: 4GB (2GB minimum)
- **Storage**: 1GB untuk project + dependencies
- **Internet**: Koneksi internet untuk download data

### Recommended Setup
- **OS**: Windows 10+, macOS 12+, Linux (Ubuntu 20.04+)
- **Python**: 3.11 atau 3.12 (latest stable)
- **RAM**: 8GB atau lebih
- **Storage**: SSD dengan 2GB space kosong
- **Network**: Koneksi internet stabil (broadband)

### Check Python Version
```bash
python --version
# atau
python3 --version
```

---

## 🚀 Quick Start (5 Menit)

Langkah termudah untuk langsung menjalankan aplikasi:

### 1. Download/Clone Project
```bash
# Jika menggunakan git
git clone https://github.com/NiaPutri23/StockTrend.git
cd stockTrend-dashboard

# Atau jika download sebagai ZIP
# Extract folder dan buka di terminal/command prompt
cd path/to/stockTrend-dashboard
```

### 2. Setup Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Setelah activated, prompt terminal akan berubah menjadi:
```
(venv) C:\Project\stockTrend-dashboard>
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Proses ini akan install semua library yang diperlukan. Tunggu hingga selesai (~2-3 menit tergantung internet).

### 4. Run Aplikasi
```bash
streamlit run app.py
```

**Output yang diharapkan:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 5. Akses Aplikasi
Aplikasi akan otomatis membuka di browser di `http://localhost:8501`

Jika tidak otomatis terbuka, buka manual: **http://localhost:8501**

---

## 📦 Instalasi Detail

### Step 1: Persiapan Awal

#### Clone Repository
```bash
# Menggunakan git
git clone https://github.com/NiaPutri23/StockTrend.git

# Atau jika belum punya git
# Download ZIP dari GitHub dan extract
```

#### Buka Terminal/Command Prompt
- **Windows**: Win + R → ketik `cmd` → Enter
- **macOS**: Command + Space → ketik `terminal` → Enter
- **Linux**: Ctrl + Alt + T

#### Navigasi ke Project Folder
```bash
# Windows
cd C:\path\to\stockTrend-dashboard

# macOS/Linux
cd /path/to/stockTrend-dashboard

# List files untuk verify
# Windows: dir
# macOS/Linux: ls
```

---

### Step 2: Setup Python Virtual Environment

Virtual environment adalah folder terpisah untuk project-specific dependencies.

#### Create Virtual Environment
```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

**Output:**
Folder `venv` akan terbuat di project folder.

#### Activate Virtual Environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux (Bash/Zsh):**
```bash
source venv/bin/activate
```

**Verify activation:**
Prompt terminal harus menampilkan `(venv)` di awal:
```
(venv) C:\Project\stockTrend-dashboard>
```

---

### Step 3: Install Python Packages

Semua dependencies dalam satu command:

```bash
pip install -r requirements.txt
```

**Packages yang akan diinstall:**
- streamlit - Web framework
- pandas - Data processing
- numpy - Numerical computing
- yfinance - Yahoo Finance API
- plotly - Interactive charts
- python-dateutil - Date utilities

**Expected output:**
```
Successfully installed streamlit-1.28.1 pandas-2.1.3 numpy-1.24.3 ...
```

**Verify installation:**
```bash
pip list
```

Harus menampilkan semua packages yang baru diinstall.

---

### Step 4: Run Application

#### Start Streamlit Server
```bash
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

  Appetite comes with Streamlit!

Press CTRL+C to quit
```

#### Access Application
- Browser akan otomatis membuka http://localhost:8501
- Jika tidak, buka manual di browser

---

### Step 5: Usage

#### Sidebar Controls
1. **Input Ticker**: Paste ticker saham (1 per baris)
   - Format: BBCA.JK, BBRI.JK, dll
   - Max 100 ticker

2. **Jumlah Hari Turun**: Ubah dengan slider (default 5)
   - Range: 2-30 hari

3. **Minimal Drawdown %**: Set filter minimum (default 0%)
   - Range: 0-100%

4. **Run Screening**: Klik untuk mulai screening

#### View Results
- Tabel hasil screening akan ditampilkan
- Click pada ticker untuk lihat detail chart dan data

#### Export Data
- Klik "Download CSV" untuk export hasil ke file CSV

---

### Step 6: Stop Application

**Untuk menghentikan aplikasi:**
```bash
# Di terminal/command prompt
Ctrl + C
```

---

## 🔧 Troubleshooting

### Issue 1: Python tidak ditemukan

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solusi:**
- Install Python dari https://www.python.org/
- Pastikan "Add Python to PATH" di-check saat install
- Restart terminal setelah install
- Gunakan `python3` di macOS/Linux

---

### Issue 2: Virtual Environment tidak bisa activate

**Error:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solusi (Windows PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Atau gunakan Command Prompt biasa (bukan PowerShell)

---

### Issue 3: pip install error

**Error:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solusi:**
```bash
# Update pip
python -m pip install --upgrade pip

# Try install again
pip install -r requirements.txt
```

---

### Issue 4: Connection error ke Yahoo Finance

**Error:**
```
Failed to connect to Yahoo Finance
```

**Solusi:**
- Periksa koneksi internet
- Coba refresh/run screening lagi
- Yahoo Finance mungkin sedang maintenance
- Cek apakah firewall/VPN memblok akses

---

### Issue 5: Port 8501 sudah digunakan

**Error:**
```
Address already in use
```

**Solusi:**
```bash
# Kill process di port 8501
# Windows: taskkill /PID [PID] /F
# macOS/Linux: kill -9 [PID]

# Atau gunakan port lain:
streamlit run app.py --server.port 8502
```

---

### Issue 6: Browser tidak auto-open

**Solusi:**
- Buka manual: http://localhost:8501
- Atau copy-paste "Local URL" dari terminal ke browser

---

### Issue 7: Ticker tidak ditemukan

**Error:**
```
⚠️ Ticker XXXX.JK invalid
```

**Solusi:**
- Pastikan format ticker benar: XXXX.JK atau XXXXX.JK
- Check daftar ticker BEI: https://www.idx.co.id/
- Ticker case-insensitive (boleh besar/kecil)

---

### Issue 8: Data tidak tersedia

**Error:**
```
Data tidak tersedia untuk ticker
```

**Solusi:**
- Ticker mungkin baru atau sudah delisted
- Coba ticker lain untuk verify koneksi
- Check ticker di Yahoo Finance: https://finance.yahoo.com/

---

## 💡 Tips & Tricks

### 1. Cache Data untuk Offline

Data di-cache otomatis, jadi akses kedua lebih cepat. Cache expired dalam 1 jam.

```bash
# Clear cache manual
# Klik tombol "Clear Cache" di sidebar
```

### 2. Eksekusi Default Tickers

Edit default value di sidebar untuk ticker yang sering digunakan:

```python
# Di app.py, ubah baris ini:
value="BBCA.JK\nBBRI.JK\nBMRI.JK\nTLKM.JK\nASII.JK",

# Menjadi ticker favorit Anda
value="BBCA.JK\nBMRI.JK\nASII.JK",
```

### 3. Bulk Testing Tickers

Untuk testing banyak ticker sekaligus, buat file `tickers.txt`:

```
BBCA.JK
BBRI.JK
BMRI.JK
TLKM.JK
ASII.JK
...
```

Kemudian load di aplikasi.

### 4. Export untuk Analysis

Export CSV hasil screening dan import ke Excel/Google Sheets untuk analisis lebih lanjut.

### 5. Daily Routine

Buat scheduled task untuk run screening setiap hari:

**Windows (Task Scheduler):**
```batch
# Buat batch file: run_screening.bat
cd C:\Project\stockTrend-dashboard
venv\Scripts\activate
streamlit run app.py
```

**macOS/Linux (Cron):**
```bash
0 9 * * 1-5 cd /path/to/stockTrend-dashboard && source venv/bin/activate && streamlit run app.py
```

---

## 🌐 Alternative: Cloud Deployment

### Streamlit Cloud (Recommended & Free)

1. Push code ke GitHub
2. Go to https://streamlit.io/cloud
3. Sign in dengan GitHub account
4. Select repository
5. App akan live di streamlit.app

**Keuntungan:**
- Free tier tersedia
- Auto-deploy dari GitHub
- HTTPS included
- Accessible dari mana saja

**Kekurangan:**
- Memory limited
- Public (tidak private)
- Cannot use credential files

---

## 📞 Perlu Bantuan?

Jika mengalami issue yang tidak tersebut di atas:

1. **Check Documentation**: Baca README.md dan PLANNING.md
2. **GitHub Issues**: https://github.com/NiaPutri23/StockTrend/issues
3. **Email**: nia.putri@email.com
4. **Stack Overflow**: Tag `streamlit` dan `python`

---

## ✅ Checklist Setup

Gunakan checklist ini untuk memastikan setup sudah benar:

- [ ] Python 3.11+ installed (verify dengan `python --version`)
- [ ] Git installed (optional, jika clone dari GitHub)
- [ ] Project folder downloaded/cloned
- [ ] Virtual environment created
- [ ] Virtual environment activated (prompt shows `(venv)`)
- [ ] Requirements installed (`pip list` shows all packages)
- [ ] Streamlit runs without error (`streamlit run app.py`)
- [ ] Browser opens at http://localhost:8501
- [ ] Dashboard loads and displays sidebar
- [ ] Can input ticker dan run screening
- [ ] Results display correctly
- [ ] Can download CSV

---

**Setup Complete! 🎉**

Sekarang Anda siap menggunakan StockTrend Dashboard untuk screening saham Indonesia.

Untuk info lebih lanjut tentang penggunaan, baca [README.md](README.md)

---

Last Updated: June 2026
