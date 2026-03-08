# Smart Security Tag with Tamper Detection and QR Payment Unlock

## 📌 Project Overview

The **Smart Security Tag** is an IoT-based security system designed to prevent theft of valuable items in retail environments. The system uses an **ESP32 microcontroller** with a **tamper detection mechanism** and a **QR code payment simulation system**.

If the security wire loop is broken, the system immediately triggers a **buzzer alarm** indicating tampering. After a successful payment simulation through a web interface, the backend server sends a signal to the ESP32 to **unlock the tag using a servo motor**.

This project integrates **IoT hardware with a web-based payment interface** using Flask and SQLite.

---

## 🎯 Objectives

* Design a smart retail security tag.
* Detect tampering using a wire-loop mechanism.
* Trigger an alarm when tampering occurs.
* Simulate QR-based payment verification.
* Unlock the tag automatically after successful payment.

---

## ⚙️ Hardware Components

* ESP32 Microcontroller
* Servo Motor
* Buzzer
* Breadboard
* Jumper Wires
* Tamper Detection Wire Loop

---

## 💻 Software Technologies

* Python (Flask Framework)
* SQLite3 Database
* HTML
* CSS
* JavaScript
* Arduino IDE (ESP32 Firmware)

---

## 🏗 System Architecture

Mobile Device
↓
QR Payment Page (HTML Interface)
↓
Flask Backend Server
↓
Payment Verification
↓
Signal Sent to ESP32
↓
Servo Unlocks Security Tag

Tamper Detection runs continuously on ESP32 and triggers the buzzer if the wire loop is disconnected.

---

## 🔑 Features

* Tamper detection using a wire loop
* Alarm buzzer for security breach
* QR code payment simulation
* Web-based payment interface
* ESP32 controlled servo unlocking
* SQLite database for transaction tracking

---

## 📂 Project Structure

```
smart-security-tag
│
├── firmware
│   └── esp32_code.ino
│
├── backend
│   ├── app.py
│   ├── database.db
│   └── requirements.txt
│
├── frontend
│   ├── templates
│   │   └── payment.html
│   └── static
│       ├── style.css
│       └── script.js
│
├── docs
│   └── architecture.png
│
├── README.md
└── .gitignore
```

---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository

```
git clone https://github.com/jeevasivaa/smart-security-tag.git
```

### 2️⃣ Navigate to Project Folder

```
cd smart-security-tag
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Run Flask Server

```
python app.py
```

### 5️⃣ Upload ESP32 Firmware

Upload the ESP32 code using **Arduino IDE**.

---

## 🔐 Tamper Detection Logic

* A wire loop is connected between two ESP32 GPIO pins.
* If the wire is cut or disconnected:

  * Circuit breaks
  * ESP32 detects the interruption
  * Buzzer alarm is activated

---

## 💳 Payment Simulation

1. User scans a QR code.
2. Payment page opens on mobile.
3. User clicks **Pay Now**.
4. Flask verifies the payment.
5. Backend sends unlock signal to ESP32.
6. Servo motor releases the security tag.

---

## 📸 Future Improvements

* Real QR code generation
* Integration with real payment APIs
* Cloud database
* Mobile application
* Secure communication using tokens

---

## 👨‍💻 Author

**Jeeva S**

Computer Science Engineering Student
Interested in IoT, Embedded Systems, and Backend Development

---

## 📜 License

This project is licensed under the **MIT License**.
