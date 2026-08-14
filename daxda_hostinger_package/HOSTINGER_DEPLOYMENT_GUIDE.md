# DAXDA V11.4 Hostinger Deployment Guide

This guide walks you through deploying the **DAXDA V11.4 Clifford Algebra Cl(4,1) Reasoning Engine & Web Dashboard** on **Hostinger Web Hosting (hPanel)** or **Hostinger VPS**.

---

## 📦 Package Contents

The deployment ZIP package contains:
- `passenger_wsgi.py` & `.htaccess` — Hostinger hPanel Python App (Phusion Passenger) entry point and URL rewrite configuration.
- `app.py` — High-tech Web UI Dashboard & REST API backend (`/api/evaluate`, `/api/preflight`, `/api/health`).
- Core Engine Modules: `daxda_engine_aglm_opt.py`, `daxda_engine_v11_4.py`, `cl41_fast.py`, `clifford_algebra.py`, `adaptive_rotor.py`, `authority_gate.py`, etc.
- `requirements.txt` — Python dependencies (`flask`, `gunicorn`, `fpdf2`).
- `install_hostinger.sh` — Automated setup script for Hostinger SSH terminal.
- Preflight dataset and verification tools (`run_preflight.py`, `03_REBUILD_TOOLS/`).

---

## 🚀 Quick Deployment Methods

### Method 1: Hostinger hPanel "Setup Python App" (Recommended for Shared/Cloud Hosting)

1. **Log in to Hostinger hPanel**:
   Navigate to [Hostinger Control Panel](https://hpanel.hostinger.com).

2. **Upload Package Files**:
   - Open **File Manager**.
   - Navigate to `public_html/` (or your domain folder).
   - Upload `daxda_v11.4_hostinger_deployment.zip` and **Extract** all contents directly into the target directory.

3. **Configure Python Application**:
   - In hPanel search, click **Setup Python App** (or **Advanced > Python**).
   - Click **Create Application**.
   - Select **Python Version**: `3.9` or `3.10` or `3.11`.
   - Set **Application Root**: `public_html` (or your subfolder).
   - Set **Application URL**: `https://yourdomain.com` (or your subfolder path).
   - Set **Application Startup File**: `passenger_wsgi.py`.
   - Set **Application Entry Point**: `application`.
   - Click **Create**.

4. **Install Dependencies**:
   - Under the created application details in hPanel, find **Configuration File** section.
   - Enter `requirements.txt` and click **Run Pip Install**.

5. **Restart & Launch**:
   - Click **Restart Application**.
   - Visit `https://yourdomain.com` in your browser to launch the DAXDA Interactive Web Dashboard!

---

### Method 2: Hostinger SSH / Terminal Installation

1. **Connect via SSH**:
   ```bash
   ssh u123456789@yourdomain.com -p 65002
   ```

2. **Navigate to App Directory & Extract**:
   ```bash
   cd ~/public_html
   unzip daxda_v11.4_hostinger_deployment.zip
   ```

3. **Run Automated Installer**:
   ```bash
   chmod +x install_hostinger.sh
   ./install_hostinger.sh
   ```

---

## 📡 REST API Endpoint Reference

Once deployed, DAXDA exposes the following REST API endpoints:

### 1. Evaluate Input Prompt (`POST /api/evaluate`)
**Request Body**:
```json
{
  "input_text": "Verify quantum system security protocol.",
  "engine": "AGLM-OPT",
  "case_id": "REQ-1001"
}
```

**Response**:
```json
{
  "case_id": "REQ-1001",
  "protocol": "DAXDA-AGLM-OPT",
  "version": "AGLM-1.0.0",
  "disposition": "RELEASE",
  "semantic_profile": {
    "trust": 0.85,
    "factual": 0.60,
    "logical": 0.50,
    "adversarial": 0.0,
    "deception": 0.0
  },
  "feedback": {
    "final_coherence": 1.0,
    "converged": true
  },
  "transport": {
    "residual": 0.0,
    "integrity": true
  },
  "latency_ms": 1.42,
  "receipt_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

### 2. Preflight Benchmark Test (`GET /api/preflight`)
Executes preflight validation across test cases and returns verification status.

### 3. Health Check (`GET /api/health`)
Returns live node health status.

---

## 🔍 Troubleshooting

- **500 Internal Server Error**:
  Ensure `passenger_wsgi.py` permissions are set to `644` or `755`. Check hPanel error logs under **Analytics & Logs > Error Logs**.
- **ModuleNotFoundError: No module named 'flask'**:
  Ensure you clicked **Run Pip Install** in hPanel with `requirements.txt`.
- **404 Not Found**:
  Verify `.htaccess` is present in `public_html` and `PassengerEnabled on` is enabled.
