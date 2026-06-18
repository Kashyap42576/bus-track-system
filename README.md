# 🚌 Fleet OS - Bus Record Tracker System

A lightweight, real-time fleet management and bus tracking system. Built with Python and Flask, this application uses Google Sheets as a live, serverless database to track bus movements, passenger loads, and operator actions through native QR code scanning.

## ✨ Features

* **📱 Native QR Code Scanning:** Scanners can instantly read vehicle QR codes through any mobile or desktop browser without needing an app store download.
* **🔒 Role-Based Access Control (RBAC):** Distinct permissions for Scanners, Fleet Admins, Operations Admins, Audit Admins, and Super Admins.
* **📊 Live Command Dashboard:** Real-time visibility into active fleet status, recent movement logs (IN/OUT, passenger load, KM readings), and system audit trails.
* **🗄️ Serverless Database:** Completely integrated with Google Sheets via the modern Google Cloud IAM Auth API for zero-cost, highly visible data storage.
* **📥 One-Click CSV Exports:** Operations and Report admins can instantly export live movement data for external reporting.
* **🎨 Modern UI/UX:** Built with Tailwind CSS, featuring glassmorphism elements, responsive mobile-first design, and seamless modal interactions.

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask, Gunicorn
* **Database:** Google Sheets (`gspread`, `google-auth`)
* **Frontend:** HTML5, Tailwind CSS (via CDN)
* **Utilities:** `html5-qrcode` (Scanner), `qrcode.js` (Generator)
* **Deployment:** Ready for Render / Heroku

## 📋 Prerequisites

To run this project locally, you will need:
* Python 3.x installed
* A Google Cloud Project with the **Google Sheets API** and **Google Drive API** enabled.
* A Google Service Account with a generated JSON key (`credentials.json`).
* A Google Sheet structured with the following tabs: `Users`, `Buses`, `Scan_Records`, and `Audit_Logs`.

## 🚀 Local Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ayushpatel2007/bus-track-system.git]
