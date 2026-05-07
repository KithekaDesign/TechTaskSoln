TechTaskSoln — Freelancing Platform with Blockchain Escrow

> A full-stack freelancing platform connecting clients and freelancers, secured by Ethereum smart contract escrow payments.

---

## 🔗 Live Demo
https://your-ngrok-link-here

---

## 👤 Developer
- Name: Daniel Kitheka  
- Registration No: CT203/109343/22  
- Course: CIT 3454 — Computer System Project (Implementation)  
- Institution: MERU University of Science & Technology 

---

📋 Project Overview

TechTaskSoln is a secure freelancing marketplace that allows:

- Clients to post projects and fund them via blockchain escrow  
- Freelancers to submit proposals and get paid securely  
- Admins to monitor activities, detect fraud, and manage the system  

---

✅ System Objectives & Implementation

1. User Registration & Authentication
- Email-based registration with OTP verification  
- JWT authentication  
- Role-based access (Client / Freelancer / Admin)  

---
2. Real-Time Project Tracking
- Project states: OPEN → IN_PROGRESS → COMPLETED  
- Real-time notifications  
- Live dashboard updates  

---

3. Blockchain Smart Contract Payment
- Ethereum smart contract (Solidity)  
- Deployed on Sepolia testnet  
- Escrow system using MetaMask  
- Funds released only after approval  

---

4. AI Fraud Detection
- Detects suspicious activity  
- Flags abnormal behavior  
- Admin monitoring dashboard  

---

### 5. Reports & Analytics
- Dashboard with charts  
- Earnings tracking  
- Proposal success rate  
- Performance insights  

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|-----------|
| Backend | Django, Django REST Framework |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| Auth | JWT |
| Blockchain | Solidity, Web3.py, MetaMask |
| Email | SendGrid |
| Real-time | Django Channels |
| Version Control | Git & GitHub |

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10+
- Git
- MetaMask

---

### Setup

```bash
git clone https://github.com/KithekaDesign/TechTaskSoln.git
cd TechTaskSoln/techtasksoln_backend

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
