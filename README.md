# 🎓 GamuX LMS - AI-Powered Campus Study Assistant

A comprehensive Learning Management System powered by AI that helps students study smarter with intelligent document processing, RAG-based Q&A, quiz generation, flashcards, and personalized study plans.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248.svg)
![Qdrant](https://img.shields.io/badge/Qdrant-Cloud-000000.svg)

---

## 🌟 Features

### 📄 Document Management
- **PDF Upload & Processing** - Upload lecture notes, textbooks, study materials
- **Automatic Text Extraction** - Intelligent chunking with overlap for better context
- **Vector Storage** - FastEmbed (BAAI/bge-small-en-v1.5) for semantic search
- **Subject Organization** - Organize documents by subject/topic

### 💬 RAG-Based Q&A System
- **Ask Questions** - Get answers from uploaded documents
- **Semantic Search** - FastEmbed 384-dimensional embeddings
- **Beautiful Formatting** - Auto-formatted answers with headings, steps, formulas
- **Source Attribution** - See which documents and pages were used
- **Confidence Scores** - Know how reliable the answer is

### 📝 Quiz Generation
- **3 Question Types:**
  - **MCQ** - Multiple choice with 4 options
  - **Short Answer** - 2-4 sentence responses
  - **Long Answer** - Detailed paragraph explanations
- **Adaptive Generation** - Retry logic for complete quiz sets
- **LLM Evaluation** - Smart grading for text answers
- **Topic Performance** - Track strong and weak topics
- **Detailed Results** - See correct answers and explanations

### 🎴 Smart Flashcards
- **3 Flashcard Types:**
  - **Key Points (50%)** - Concise 3-5 bullet points for quick revision
  - **Concepts (30%)** - Simple explanations in ≤40 words
  - **Comparisons (20%)** - Side-by-side concept differences
- **Adaptive Learning** - Prioritizes weak topics from quiz results
- **No Storage** - Generated on-the-fly for revision
- **Beautiful UI** - Card navigation with progress tracking

### 📊 Study Plan Generator
- **Personalized Plans** - Based on uploaded documents and goals
- **Time Management** - Daily schedules with specific topics
- **Revision Cycles** - Spaced repetition built-in
- **Goal-Oriented** - Customize for exams, certifications, or general learning

### 📈 Analytics Dashboard
- **Learning Progress** - Track documents, quizzes, flashcards
- **Subject Performance** - See which subjects need more attention
- **Study Streak** - Monitor consistency
- **Time Analysis** - Understand study patterns

---

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** MongoDB Atlas (Document storage)
- **Vector DB:** Qdrant Cloud (Semantic search)
- **LLM:** Groq (Llama 3.3 70B)
- **Embeddings:** FastEmbed (BAAI/bge-small-en-v1.5, 384-dim)
- **PDF Processing:** LangChain + PyPDF
- **Authentication:** JWT with bcrypt

### Frontend
- **Framework:** React 18
- **Styling:** Custom CSS with dark theme
- **HTTP Client:** Axios
- **Icons:** Lucide React
- **State Management:** React Context (Auth)

### Infrastructure
- **Cloud Storage:** MongoDB Atlas
- **Vector Storage:** Qdrant Cloud
- **API:** Groq API (Fast LLM inference)

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 16+ and npm
- MongoDB Atlas account
- Qdrant Cloud account
- Groq API key

### 1. Clone Repository
```bash
git clone <repository-url>
cd AI_helper
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd backend
python -m venv venv_new
venv_new\Scripts\activate  # Windows
# source venv_new/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

#### Configure Environment
Create `backend/.env` file:
```env
# MongoDB Atlas
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/
MONGO_DB_NAME=AI_Helper

# Qdrant Cloud
QDRANT_URL=https://xxxxxxxx.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=study_documents

# JWT
SECRET_KEY=your_secret_key_here_use_secrets.token_urlsafe(32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Groq API
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=10
SIMILARITY_THRESHOLD=0.0
```

#### Initialize Vector Database
```bash
python reset_qdrant.py
```

#### Start Backend
```bash
python start_backend_no_reload.py
```

Backend runs on: `http://localhost:8000`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend-react
npm install
```

#### Configure API URL
Update `src/services/api.js` if needed:
```javascript
const API_URL = 'http://localhost:8000/api/v1';
```

#### Start Frontend
```bash
npm start
```

Frontend runs on: `http://localhost:3000`

---

## 🚀 Quick Start

1. **Start Backend:**
   ```bash
   cd backend
   venv_new\Scripts\activate
   python start_backend_no_reload.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend-react
   npm start
   ```

3. **Access Application:**
   - Open browser: `http://localhost:3000`
   - Register a new account
   - Upload your first PDF document
   - Start studying!

---

## 📖 Usage Guide

### Uploading Documents
1. Go to **Upload** page
2. Select PDF file (max 50MB)
3. Enter subject name
4. Click "Upload Document"
5. Wait for processing (embeddings are generated)

### Asking Questions
1. Go to **Ask a Question** page
2. Select document or search all
3. Type your question
4. Get formatted answer with sources

### Generating Quizzes
1. Go to **Generate Quiz** page
2. Select document
3. Choose question types (MCQ, Short, Long)
4. Click "Generate Quiz"
5. Take quiz with Next/Previous navigation
6. View detailed results with correct answers

### Creating Flashcards
1. Go to **Flashcards** page
2. Select document
3. Choose number of cards (5-10)
4. View key points, concepts, and comparisons
5. Navigate with Next/Previous
6. Perfect for quick revision!

### Generating Study Plans
1. Go to **Study Plan** page
2. Select documents
3. Set study goal and deadline
4. Get personalized daily schedule

### Viewing Analytics
1. Go to **Analytics** page
2. See learning progress
3. Identify weak topics
4. Track study streaks

---

## 🎨 Features Deep Dive

### FastEmbed Integration
- **Model:** BAAI/bge-small-en-v1.5
- **Dimensions:** 384
- **Benefits:** Better semantic understanding vs TF-IDF
- **Speed:** ~50ms per embedding
- **Accuracy:** Significantly improved relevance scores

### Adaptive Quiz System
- **Multi-attempt generation:** Retries up to 3 times for complete sets
- **Smart parsing:** Handles various LLM response formats
- **Text evaluation:** LLM-powered concept checking (not word-for-word)
- **Topic tracking:** Identifies strong (≥80%) and weak (<50%) topics

### Intelligent Flashcards
- **Key Points:** 3-5 bullets per topic, max 20 words each
- **Concepts:** Simple explanations, max 40 words
- **Comparisons:** Side-by-side for confused concepts
- **Adaptive:** Prioritizes weak topics when provided

### Beautiful UI
- **Dark Theme:** Easy on the eyes for long study sessions
- **Formatted Answers:** Auto-detects headings, formulas, code
- **Card Navigation:** Progress dots, Next/Previous buttons
- **Responsive:** Works on desktop, tablet, mobile

---

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)

```python
# Vector Search
QDRANT_VECTOR_SIZE = 384  # FastEmbed dimensions
TOP_K_RETRIEVAL = 10      # Chunks to retrieve
SIMILARITY_THRESHOLD = 0.0  # No threshold (filter in app)

# PDF Processing
CHUNK_SIZE = 1000         # Characters per chunk
CHUNK_OVERLAP = 200       # Overlap between chunks

# LLM
GROQ_MODEL = "llama-3.3-70b-versatile"  # Or llama-3.1-8b-instant for speed
```

### Tuning for Better Results

**For longer documents:**
- Increase `CHUNK_SIZE` to 1500
- Increase `CHUNK_OVERLAP` to 300

**For better quiz quality:**
- Adjust temperature in `quiz_service.py` (0.7-0.9)
- Increase `max_tokens` for longer questions

**For faster responses:**
- Use `llama-3.1-8b-instant` model
- Reduce `TOP_K_RETRIEVAL` to 5

---

## 🗂️ Project Structure

```
AI_helper/
├── backend/
│   ├── api/              # FastAPI routes
│   │   ├── auth/         # Authentication
│   │   ├── documents/    # Document management
│   │   ├── quiz/         # Quiz generation
│   │   ├── flashcard/    # Flashcard generation
│   │   ├── rag/          # Q&A system
│   │   ├── summary/      # Summaries
│   │   ├── learning/     # Study plans
│   │   └── analytics/    # Analytics
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   │   ├── auth/
│   │   ├── documents/
│   │   ├── quiz/
│   │   ├── flashcard/
│   │   ├── rag/          # FastEmbed + RAG
│   │   ├── pdf/          # PDF processing
│   │   ├── summary/
│   │   └── learning/
│   ├── database/         # MongoDB + Qdrant
│   ├── config.py         # Configuration
│   ├── main.py           # FastAPI app
│   └── requirements.txt
│
├── frontend-react/
│   ├── public/
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── context/      # React context (auth)
│   │   ├── pages/        # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Upload.jsx
│   │   │   ├── AskQuestion.jsx
│   │   │   ├── GenerateQuiz.jsx
│   │   │   ├── TakeQuiz.jsx
│   │   │   ├── Flashcards.jsx
│   │   │   ├── StudyPlan.jsx
│   │   │   └── Analytics.jsx
│   │   ├── services/     # API client
│   │   ├── App.js
│   │   └── App.css
│   └── package.json
│
└── README.md
```

---

## 🔐 Security

- **Password Hashing:** bcrypt with SHA256 pre-hashing
- **JWT Authentication:** Secure token-based auth
- **API Key Protection:** Environment variables
- **CORS:** Configured for frontend origin
- **Input Validation:** Pydantic models

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest  # If tests are set up
```

### Manual Testing
1. Upload a sample PDF
2. Ask questions about its content
3. Generate a quiz
4. Create flashcards
5. View analytics

---

## 📊 Performance

- **Document Upload:** ~5-15 seconds (depends on size)
- **Question Answering:** ~2-4 seconds
- **Quiz Generation:** ~15-30 seconds (5-10 questions)
- **Flashcard Generation:** ~10-20 seconds (5-10 cards)
- **Backend Startup:** ~5 seconds (with FastEmbed loading)

---

## 🐛 Troubleshooting

### Backend Issues

**MongoDB Connection Failed:**
- Check `MONGO_URI` in `.env`
- Verify network access in MongoDB Atlas
- Whitelist IP address in MongoDB Atlas

**Qdrant Connection Failed:**
- Check `QDRANT_URL` and `QDRANT_API_KEY`
- Verify Qdrant Cloud cluster is running
- Run `python reset_qdrant.py` to recreate collection

**"Vector dimension error":**
```bash
python reset_qdrant.py  # Recreate collection with 384 dimensions
```
Then re-upload documents.

**"No chunks found":**
- Ensure document was uploaded successfully
- Check Qdrant collection: `python verify_embeddings.py` (if available)
- Re-upload the document

### Frontend Issues

**"Network Error":**
- Ensure backend is running on port 8000
- Check CORS configuration in `backend/main.py`

**Dependencies Error:**
```bash
cd frontend-react
rm -rf node_modules package-lock.json
npm install
```

---

## 🔄 Updates & Maintenance

### Updating Dependencies

**Backend:**
```bash
cd backend
pip install --upgrade -r requirements.txt
```

**Frontend:**
```bash
cd frontend-react
npm update
```

### Database Maintenance

**Reset Qdrant (if embeddings are corrupted):**
```bash
cd backend
python reset_qdrant.py
```

**Backup MongoDB:**
Use MongoDB Atlas backup features or mongodump.

---

## 📝 API Documentation

API documentation available at: `http://localhost:8000/docs` (Swagger UI)

### Key Endpoints

```
POST   /api/v1/auth/register          # Register user
POST   /api/v1/auth/login             # Login user
POST   /api/v1/documents/upload       # Upload document
GET    /api/v1/documents/             # List documents
POST   /api/v1/rag/ask                # Ask question
POST   /api/v1/quiz/generate          # Generate quiz
POST   /api/v1/quiz/submit            # Submit quiz
POST   /api/v1/flashcard/generate     # Generate flashcards
POST   /api/v1/summary/generate       # Generate summary
POST   /api/v1/learning/generate      # Generate study plan
GET    /api/v1/analytics/dashboard    # Get analytics
```

---

## 🎯 Roadmap

### Planned Features
- [ ] Multi-language support
- [ ] Voice-based Q&A
- [ ] Collaborative study groups
- [ ] Mobile app (React Native)
- [ ] Video lecture processing
- [ ] Spaced repetition algorithm
- [ ] Export study materials (PDF, Markdown)
- [ ] Integration with Google Drive, Dropbox
- [ ] Real-time collaboration
- [ ] Gamification (badges, leaderboards)

---

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - UI library
- **MongoDB Atlas** - Cloud database
- **Qdrant Cloud** - Vector database
- **Groq** - Fast LLM inference
- **FastEmbed** - Lightweight embedding library
- **LangChain** - LLM application framework

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

---

**Built with ❤️ for students worldwide** 🎓
