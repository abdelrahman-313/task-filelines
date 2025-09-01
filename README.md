
# 📂 Task Filelines

A Django 4.2 + Django REST Framework project for uploading `.txt` files and retrieving random or longest lines.  
This repo ships with **Docker Compose** for easy setup, Swagger API docs, and GitHub Actions CI/CD.

---

## 🚀 Features
- Upload `.txt` files via REST API
- Fetch a random line in JSON, XML, or plain text
- Reverse a random line
- Get the longest 100 lines across all uploaded files
- Get the longest 20 lines of a specific file
- Auto-generated API docs with Swagger & ReDoc
- GitHub Actions for testing & coverage

---

## 🛠 Tech Stack
- **Django** 4.2  
- **Django REST Framework** 3.14  
- **drf-spectacular** for API schema & Swagger UI  
- **Gunicorn** for production WSGI server  
- **Docker + Docker Compose** for containerization  
- **Pytest + Coverage** for testing  

---

## 📦 Installation (Docker Compose)

Follow these steps to get the project running locally:

### 1. Clone the repository
```bash
git clone https://github.com/abdelrahman-313/task-filelines.git
cd task-filelines
docker compose up --build
```
### 2. Access the application
- **App Home** → [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
- **Swagger UI** → [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)  
- **ReDoc** → [http://127.0.0.1:8000/api/schema/redoc/](http://127.0.0.1:8000/api/schema/redoc/)  
- **Django Admin** → [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)  


