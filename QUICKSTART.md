# ⚡ Quick Start Guide

Get GamuX LMS running in 5 minutes!

---

## 🚀 For Windows Users (Easiest)

### Step 1: Setup Backend (One-time)
```bash
cd backend
python -m venv venv_new
venv_new\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure
Edit `backend/.env` with your credentials:
- MongoDB URI
- Qdrant URL and API Key  
- Groq API Key
- JWT Secret Key

### Step 3: Initialize Database
```bash
python reset_qdrant.py
```
Type `yes` when prompted.

### Step 4: Start Application
Double-click:
- `START_BACKEND.bat` (starts backend)
- `START_FRONTEND.bat` (starts frontend)

**That's it!** 🎉

Open browser: `http://localhost:3000`

---

## 🐧 For Linux/Mac Users

### Terminal 1 (Backend):
```bash
cd backend
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt

# Configure .env file
# nano .env

# Initialize
python reset_qdrant.py

# Start
python start_backend.py
```

### Terminal 2 (Frontend):
```bash
cd frontend-react
npm install
npm start
```

---

## 📝 First Time Setup Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 16+ installed
- [ ] MongoDB Atlas account created
- [ ] Qdrant Cloud account created
- [ ] Groq API key obtained
- [ ] `.env` file configured
- [ ] Qdrant collection initialized
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Registered first user account

---

## 🎯 What to Do Next

1. **Register** - Create your account
2. **Upload** - Add your first PDF document
3. **Ask** - Try asking questions about it
4. **Quiz** - Generate a quiz to test yourself
5. **Study** - Create flashcards and study plans

---

## 🐛 Common Issues

### "Module not found"
```bash
cd backend
pip install -r requirements.txt
```

### "Port already in use"
Kill the process using port 8000 or 3000

### "Vector dimension error"
```bash
cd backend
python reset_qdrant.py
```
Then re-upload documents.

---

**Need help?** Check the full [README.md](README.md)
