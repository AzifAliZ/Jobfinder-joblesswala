# Job Finder & Professional Networking Portal  
### (Django + DRF + React + MySQL)

A full-stack job search and professional networking platform similar to **LinkedIn + Naukri**, supporting both **individual users** and **companies**.  
Built using **Django REST Framework** for backend APIs, **MySQL** as the database, and **React.js** for the frontend.

---

# 🚀 Features Overview

## 👤 Authentication & Accounts
### User Registration
- Create a job seeker account  
- Fields: username, email, password, confirm password  
- Role is automatically set as "user"  
- Can create profile, connect, message, apply for jobs  

### Company Registration
- Create company accounts  
- Fields: company name, username, email, password, confirm password  
- Role is automatically set as "company"  
- Can post jobs, view applicants, approve candidates  

### Login System
- JWT Authentication  
- Redirects based on role  
- Stores token in frontend  

---

# 🧑‍💼 Job Portal Features

## 📝 Job Posting (Company)
- Companies can create job posts  
- Fields include title, description, salary range, location, job type, experience  
- Companies can edit or delete job posts  
- Job posts stored in MySQL table  

## 📥 Apply for Jobs (Users)
- Users can apply for any job  
- Company sees list of applicants for each job  
- User can upload resume  
- Prevent multiple applications for same job  

## ✔ Approve Applicants (Company)
- Company can:
  - Approve  
  - Reject  
  - Shortlist candidates  
- Status automatically updates on both sides  

## 🔍 Job Filters
Users can filter jobs by:
- Job title  
- Company  
- Location  
- Salary  
- Experience  
- Job type (Full-time, Part-time, Remote)  

---

# 🌐 Networking & Social Features

## 🔗 Connect (Like LinkedIn)
- Users can send connection requests  
- Accept / Reject requests  
- See connections list  
- Companies can also connect with users  

## 💬 Messaging System
- Send/receive messages between connected users  
- Real-time conversation layout  
- Message timestamps  
- Chat list sorted by latest message  

## 👥 Search Users
- Search users by username  
- View profile, experience, skills  
- Send connect request from search results  

---

# 🗄 Database (MySQL)

The project uses **MySQL database** with PyMySQL connector.

### 📌 Tables include:
- `accounts_account` – Users & companies  
- `job_posts` – Job listings  
- `applications` – Job applicants  
- `connections` – Network relations  
- `messages` – Chat system  
- `notifications` – Alerts for connections, approvals, messages  

---

# 🛠 Tech Stack

## Backend
- Django 5  
- Django REST Framework  
- MySQL  
- SimpleJWT  
- PyMySQL  

## Frontend
- React  
- React Router  
- Axios  
- Context API / Redux (optional)  

---

# 📦 Installation Guide

## ⚙ Backend Setup

### 1. Clone Repo
```bash
git clone https://github.com/yourusername/jobportal
cd jobportal
2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows

3. Install Requirements
pip install -r requirements.txt

4. Install PyMySQL
pip install pymysql

5. Configure MySQL

Create database:

CREATE DATABASE jobportal_db;


Add in jobportal/__init__.py:

import pymysql
pymysql.install_as_MySQLdb()


Add in settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jobportal_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

6. Run Migrations
python manage.py makemigrations
python manage.py migrate

7. Start Backend Server
python manage.py runserver

🎨 Frontend Setup (React)
1. Enter frontend folder
cd jobportal-frontend

2. Install dependencies
npm install

3. Run App
npm start

📁 Project Structure

jobportal/
│── backend/
│   ├── jobportal/ (settings)
│   ├── accounts/ (authentication)
│   ├── jobs/ (job posting + applications)
│   ├── messaging/ (chat system)
│   ├── network/ (connections)
│   └── notifications/
│
└── jobportal-frontend/
    └── src/
        ├── components/
        ├── pages/
        │   ├── Login.js
        │   ├── RegisterUser.js
        │   ├── RegisterCompany.js
        │   ├── Jobs.js
        │   ├── ApplyJob.js
        │   ├── Network.js
        │   ├── Messages.js
        │   ├── Search.js
        │   └── Home.js

📡 API Endpoints Summary

Authentication
Method	Endpoint	Description
POST	/api/accounts/register/	Register user/company
POST	/api/accounts/login/	JWT Login
Jobs
Method	Endpoint	Description
POST	/api/jobs/create/	Create job
GET	/api/jobs/	List jobs (with filters)
GET	/api/jobs/<id>/	Job details
Applications
Method	Endpoint	Description
POST	/api/jobs/apply/<job_id>/	Apply for job
GET	/api/company/applicants/<job_id>/	View applicants
PUT	/api/company/approve/<applicant_id>/	Approve applicant
Networking
Method	Endpoint	Description
POST	/api/connect/send/<user_id>/	Send connection request
POST	/api/connect/accept/<request_id>/	Accept request
GET	/api/connect/list/	View connections
Messaging
Method	Endpoint	Description
GET	/api/messages/<user_id>/	Get chat
POST	/api/messages/send/	Send message
🔮 Future Enhancements

Real-time chat with WebSockets

Push notifications

AI-based job recommendations

Resume parsing

Video call interviews

⭐ Support This Project

If you like the project, give a star ⭐ on GitHub!


