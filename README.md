# 🚀 Clinic Platform

Clinic Platform is a modern **Electronic Health Record (EHR) and Clinic Management System** designed to optimize clinic operations, patient record-keeping, and appointment scheduling. Built with **Django**, it empowers healthcare professionals with seamless, efficient, and secure management of their practice.

---

## 🌟 Features

✅ **Patient Management** - Maintain detailed records, including medical history & treatment plans.  
✅ **Appointment Scheduling** - Hassle-free patient appointment booking & automated reminders.  
✅ **Medical Records** - Secure storage & easy retrieval of patient medical history.  
✅ **User Authentication** - Role-based access control for security.  
✅ **Interactive API Docs** - Explore API endpoints via **Swagger UI**.  

---

## 🎯 Live Demo

🔗 **[Clinic Platform](https://clinic-platform.up.railway.app/)** *(Deployed on Railway.app)*  

---

## 🛠️ Tech Stack

🚀 **Backend**: Django, Django REST Framework  
💾 **Database**: PostgreSQL / SQLite  
🌐 **Frontend**: HTML, CSS (Admin Dashboard)  
📡 **Deployment**: Railway.app, Gunicorn  
🔐 **Authentication**: Django Authentication System   
📨 **Asynchronous Tasks**: Celery, Redis (Used for background tasks like email notifications)  

---

## 📁 Project Structure

📂 **accounts/** - Handles user authentication & profiles.  
📂 **appointments/** - Manages patient appointment scheduling.  
📂 **clinic360/** - Core application integrating all modules.  
📂 **records/** - Manages patient medical records.  

---

## ⚙️ Installation

### 🔹 Setup Locally

1️⃣ **Clone the Repository**:
```bash
git clone https://github.com/debojit11/Clinic360_platform.git
cd Clini_platform
```

2️⃣ **Create & Activate Virtual Environment**:
```bash
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

3️⃣ **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4️⃣ **Apply Migrations**:
```bash
python manage.py migrate
```

5️⃣ **Run Development Server**:
```bash
python manage.py runserver
```
🌍 **Visit:** `http://127.0.0.1:8000/`

---

## 🔌 API Access

🛠️ **Interactive API Documentation:** [Clinic Platform API](https://clinic-platform.up.railway.app/api/docs/)  

---

## 🚀 Deployment

The project is deployed using **Railway.app**. Before deployment, ensure all required environment variables are set.

### 🔹 Procfile

A **Procfile** is used to define the command for running the application in production:
```bash
web: python manage.py collectstatic --noinput && gunicorn clinic360.wsgi:application
worker: celery -A clinic360 worker --loglevel=info
```
Ensure the `Procfile` is included in the root directory for smooth deployment.

---

## 🤝 Contributing

💡 **Want to contribute? Follow these steps!**

1️⃣ **Fork the repository**  
2️⃣ **Create a new branch**: `git checkout -b feature-branch-name`  
3️⃣ **Make your changes & commit**: `git commit -m 'Add new feature'`  
4️⃣ **Push to your branch**: `git push origin feature-branch-name`  
5️⃣ **Submit a pull request**  

---

## 📜 License

This project is **open-source** under the **MIT License**. Check the `LICENSE` file for details.

---

💻 **Developed & Maintained by:** [@debojit11](https://github.com/debojit11)  
🚀 **GitHub Repository:** [Clinic Platform](https://github.com/debojit11/Clinic360_platform)