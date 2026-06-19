import os
import datetime
import io
import csv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = "super_secret_secure_key_for_bus_tracker"

# --- TIMEZONE FIX FOR INDIA (IST) ---
def get_ist_now():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now + datetime.timedelta(hours=5, minutes=30)

def generate_id(prefix):
    return f"{prefix}-{int(get_ist_now().timestamp())}"

# --- GOOGLE SHEETS SETUP ---
def get_sheet():
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)
    client = gspread.authorize(creds)
    sheet_url = "https://docs.google.com/spreadsheets/d/10eMYLJPoN0VYySX2yeMuNhqF9zquGS7_oYtyKv-WSGM/edit"
    return client.open_by_url(sheet_url)

# --- LOGIN & ROUTING ---
@app.route("/")
def home():
    if "user" in session:
        if session["role"] == "Scanner":
            return redirect(url_for("scanner_dashboard"))
        else:
            return redirect(url_for("admin_dashboard"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    
    try:
        sheet = get_sheet()
        users_sheet = sheet.worksheet("Users")
        all_users = users_sheet.get_all_records()
        
        user_match = next((u for u in all_users if str(u["Username"]) == username and str(u["Password"]) == password), None)
        
        if user_match:
            session["user"] = user_match["Username"]
            session["role"] = user_match["Role"]
            
            try:
                sheet.worksheet("Audit_Logs").append_row([
                    generate_id("LOG"), get_ist_now().strftime("%Y-%m-%d %H:%M:%S"), session["user"], "Login", f"Logged in as {session['role']}"
                ])
            except:
                pass 
            
            return redirect(url_for("scanner_dashboard") if session["role"] == "Scanner" else url_for("admin_dashboard"))
        else:
            return render_template("login.html", error="Invalid Username or Password")
    except Exception as e:
        return render_template("login.html", error=f"Database error: {str(e)}")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# --- SCANNER API ---
@app.route("/scanner")
def scanner_dashboard():
    if "user" not in session or session["role"] != "Scanner":
        return redirect(url_for("home"))
    return render_template("scanner.html")

@app.route("/submit-scan", methods=["POST"])
def submit_scan():
    if "user" not in session or session["role"] != "Scanner":
        return jsonify({"success": False, "message": "Unauthorized"}), 403
        
    data = request.json
    try:
        sheet = get_sheet()
        record_id = generate_id("REC")
        timestamp = get_ist_now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ADDED ROUTE TO THE DATA ROW
        sheet.worksheet("Scan_Records").append_row([
            record_id, timestamp, data.get("bus_number").strip().upper(),
            data.get("direction"), data.get("load"), data.get("route", "Regular"), data.get("km", ""), session["user"]
        ])
        return jsonify({"success": True, "message": "Saved successfully!"})
    except Exception as e:
        if "200" in str(e):
            return jsonify({"success": True, "message": "Saved successfully!"})
        return jsonify({"success": False, "message": str(e)}), 500

# --- ADMIN API ---
@app.route("/admin")
def admin_dashboard():
    if "user" not in session or session["role"] == "Scanner":
        return redirect(url_for("home"))
    try:
        sheet = get_sheet()
        records = sheet.worksheet("Scan_Records").get_all_records()
        buses = sheet.worksheet("Buses").get_all_records()
        
        audit_logs = []
        if session["role"] in ["Super_Admin", "Audit_Admin"]:
            audit_logs = sheet.worksheet("Audit_Logs").get_all_records()
            
        return render_template("admin.html", 
                               role=session["role"], 
                               records=records, 
                               buses=buses,
                               audit_logs=audit_logs)
    except Exception as e:
        return f"Error loading admin: {str(e)}"

@app.route("/admin/add-bus", methods=["POST"])
def add_bus():
    if "user" in session and session["role"] in ["Super_Admin", "Fleet_Admin", "Operations_Admin"]:
        bus_number = request.form.get("bus_number").strip().upper()
        vehicle_type = request.form.get("vehicle_type", "").strip()
        if not vehicle_type:
            vehicle_type = "N/A"
            
        try:
            sheet = get_sheet()
            bus_id = generate_id("BUS")
            sheet.worksheet("Buses").append_row([bus_id, bus_number, "Active", vehicle_type])
            
            try:
                sheet.worksheet("Audit_Logs").append_row([
                    generate_id("LOG"), get_ist_now().strftime("%Y-%m-%d %H:%M:%S"), session["user"], "Add Bus", f"Added {bus_number} ({vehicle_type})"
                ])
            except:
                pass
        except Exception:
            pass
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/export")
def export_data():
    if "user" not in session or session["role"] not in ["Super_Admin", "Operations_Admin", "Report_Admin"]:
        return redirect(url_for("admin_dashboard"))
        
    try:
        sheet = get_sheet()
        records = sheet.worksheet("Scan_Records").get_all_records()
        
        si = io.StringIO()
        cw = csv.writer(si)
        
        if records:
            cw.writerow(records[0].keys())
            for r in records:
                cw.writerow(r.values())
                
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=fleet_export_{int(get_ist_now().timestamp())}.csv"
        output.headers["Content-type"] = "text/csv"
        
        try:
            sheet.worksheet("Audit_Logs").append_row([
                generate_id("LOG"), get_ist_now().strftime("%Y-%m-%d %H:%M:%S"), session["user"], "Data Export", "Exported Scan_Records to CSV"
            ])
        except:
            pass
            
        return output
    except Exception as e:
        return f"Error exporting data: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
