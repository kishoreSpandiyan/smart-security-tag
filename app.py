"""
Smart Security Tag System — Flask Backend
Routes, APIs, and serial communication with ESP32.

Run: python app.py
Open: http://127.0.0.1:5000
"""

import sqlite3
import threading
import time
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify

# ---------------------------------------------------------------------------
# Try to import pyserial — graceful fallback if not installed or no device
# ---------------------------------------------------------------------------
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("[WARN] pyserial not installed. Running in DEMO mode (no ESP32).")

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

# ---------------------------------------------------------------------------
# System State (thread-safe via GIL for simple dict updates)
# ---------------------------------------------------------------------------
system_status = {
    "esp_connected": False,
    "lock_state": "LOCKED",
    "tamper_state": "SAFE",
    "last_tamper": None
}

esp = None  # Global serial connection


# ---------------------------------------------------------------------------
# Database Helper
# ---------------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Serial Connection
# ---------------------------------------------------------------------------
def connect_serial(port="COM3", baud=115200):
    """Connect to ESP32 via serial. Returns serial object or None."""
    global esp
    if not SERIAL_AVAILABLE:
        print("[WARN] pyserial not available. Skipping serial connection.")
        return None
    try:
        esp = serial.Serial(port, baud, timeout=1)
        time.sleep(2)  # Wait for ESP32 boot reset
        system_status["esp_connected"] = True
        print(f"[OK] Connected to ESP32 on {port} at {baud} baud")
        return esp
    except Exception as e:
        print(f"[FAIL] Serial connection failed: {e}")
        system_status["esp_connected"] = False
        return None


# ---------------------------------------------------------------------------
# Background Serial Reader (daemon thread)
# ---------------------------------------------------------------------------
def serial_reader():
    """Continuously read ESP32 serial output and update system state."""
    global esp
    while True:
        if esp is None or not system_status["esp_connected"]:
            time.sleep(1)
            continue
        try:
            if esp.in_waiting > 0:
                line = esp.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                print(f"[ESP32] {line}")
                now = datetime.now().isoformat()

                db = get_db()

                if "[ALERT]" in line:
                    system_status["tamper_state"] = "TAMPERED"
                    system_status["last_tamper"] = now
                    db.execute(
                        "INSERT INTO tamper_logs (event_type, message) VALUES (?, ?)",
                        ("TAMPER", line)
                    )
                    db.commit()

                elif "UNLOCKED" in line and "RE-LOCKED" not in line:
                    system_status["lock_state"] = "UNLOCKED"
                    db.execute(
                        "INSERT INTO tamper_logs (event_type, message) VALUES (?, ?)",
                        ("UNLOCK", line)
                    )
                    db.commit()

                elif "RE-LOCKED" in line:
                    system_status["lock_state"] = "LOCKED"
                    system_status["tamper_state"] = "SAFE"
                    db.execute(
                        "INSERT INTO tamper_logs (event_type, message) VALUES (?, ?)",
                        ("LOCK", line)
                    )
                    db.commit()

                elif "ready" in line.lower() or "Smart Security Tag" in line:
                    system_status["lock_state"] = "LOCKED"
                    system_status["tamper_state"] = "SAFE"

                db.close()

        except Exception as e:
            print(f"[Serial Error] {e}")
            system_status["esp_connected"] = False
            time.sleep(2)
            # Try to reconnect
            connect_serial()

        time.sleep(0.05)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def dashboard():
    """Main dashboard — live status, logs, history."""
    return render_template("dashboard.html")


@app.route("/payment")
def payment():
    """Payment simulation form."""
    return render_template("payment.html")


@app.route("/pay", methods=["POST"])
def pay():
    """Process payment, send unlock command to ESP32."""
    product_name = request.form.get("product_name", "Unknown Product")
    amount = request.form.get("amount", 0)

    try:
        amount = int(amount)
    except ValueError:
        amount = 0

    # Insert payment record
    db = get_db()
    db.execute(
        "INSERT INTO payments (product_name, amount, status) VALUES (?, ?, ?)",
        (product_name, amount, "PAID")
    )
    db.commit()
    db.close()

    # Send unlock command to ESP32
    if esp and system_status["esp_connected"]:
        try:
            system_status["lock_state"] = "UNLOCKING"
            esp.write(b"unlock\n")
            print("[Flask] Sent 'unlock' command to ESP32")
        except Exception as e:
            print(f"[Flask] Failed to send unlock: {e}")
    else:
        print("[Flask] ESP32 not connected — simulating unlock")
        system_status["lock_state"] = "UNLOCKING"
        # Simulate unlock cycle in demo mode
        def simulate_unlock():
            time.sleep(0.5)
            system_status["lock_state"] = "UNLOCKED"
            time.sleep(5)
            system_status["lock_state"] = "LOCKED"
        threading.Thread(target=simulate_unlock, daemon=True).start()

    return render_template("success.html", product_name=product_name, amount=amount)


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.route("/api/status")
def api_status():
    """Return current system status as JSON."""
    return jsonify(system_status)


@app.route("/api/tamper-logs")
def api_tamper_logs():
    """Return recent tamper log entries."""
    db = get_db()
    logs = db.execute(
        "SELECT * FROM tamper_logs ORDER BY timestamp DESC LIMIT 50"
    ).fetchall()
    db.close()
    return jsonify([dict(row) for row in logs])


@app.route("/api/payments")
def api_payments():
    """Return recent payments."""
    db = get_db()
    payments = db.execute(
        "SELECT * FROM payments ORDER BY created_at DESC LIMIT 20"
    ).fetchall()
    db.close()
    return jsonify([dict(row) for row in payments])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Connect to ESP32
    connect_serial()

    # Start background serial reader
    reader_thread = threading.Thread(target=serial_reader, daemon=True)
    reader_thread.start()

    print("[OK] Starting Flask server on http://127.0.0.1:5000")
    # use_reloader=False prevents Flask from spawning a second process
    # that would steal the serial port
    app.run(debug=True, use_reloader=False)
