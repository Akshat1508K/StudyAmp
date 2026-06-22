# Campus Study Assistant - React Frontend

Modern React frontend for the Campus Study Assistant LMS with dark theme UI.

## Features

- ✅ Modern dark theme UI inspired by StudyAmp AI
- ✅ React with TypeScript
- ✅ JWT Authentication
- ✅ Document Upload & Management
- ✅ RAG-based Q&A System
- ✅ Summary Generation
- ✅ Quiz Generation & Taking
- ✅ Flashcards
- ✅ Study Plan Generation
- ✅ Analytics Dashboard
- ✅ Responsive Design

## Tech Stack

- **React 18** with TypeScript
- **React Router** for navigation
- **Axios** for API calls
- **Recharts** for data visualization
- **Lucide React** for icons

## Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and set your backend URL (default: `http://localhost:8000`). Keep `.env` local and do not commit it to Git.

3. Start the development server:
```bash
npm start
```

The app will run on `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The optimized production build will be in the `build/` directory.

## Project Structure

```
frontend-react/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── Layout.tsx          # Main layout with sidebar
│   ├── contexts/
│   │   └── AuthContext.tsx     # Authentication context
│   ├── pages/
│   │   ├── Login.tsx           # Login page
│   │   ├── Register.tsx        # Registration page
│   │   ├── Dashboard.tsx       # Dashboard
│   │   ├── UploadDocuments.tsx # Document upload
│   │   ├── AskQuestion.tsx     # RAG Q&A
│   │   ├── GenerateSummary.tsx # Summary generation
│   │   ├── GenerateQuiz.tsx    # Quiz generation
│   │   ├── TakeQuiz.tsx        # Quiz taking
│   │   ├── Flashcards.tsx      # Flashcards
│   │   ├── StudyPlan.tsx       # Study plan
│   │   └── Analytics.tsx       # Analytics
│   ├── services/
│   │   └── api.ts              # API client
│   ├── App.tsx                 # Main app component
│   ├── App.css                 # Global styles
│   ├── index.tsx               # Entry point
│   └── index.css               # Root styles
├── package.json
├── tsconfig.json
└── README.md
```

## API Integration

The frontend communicates with the FastAPI backend through the API client in `src/services/api.ts`.

All API calls include JWT authentication automatically.

## Theming

The app uses CSS custom properties for theming. The dark theme is defined in `src/index.css`:

```css
:root {
  --bg-primary: #0f1218;
  --bg-secondary: #1a1d25;
  --accent-blue: #3b82f6;
  --accent-purple: #8b5cf6;
  --accent-green: #10b981;
  --accent-yellow: #f59e0b;
  --accent-red: #ef4444;
  /* ... */
}
```

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (⚠️ one-way operation)

## Backend Setup

Make sure the FastAPI backend is running on the port specified in `.env`.

Backend default: `http://localhost:8000`

See backend README for setup instructions.
