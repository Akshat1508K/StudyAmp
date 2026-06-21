import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import UploadDocuments from './pages/UploadDocuments';
import AskQuestion from './pages/AskQuestion';
import GenerateSummary from './pages/GenerateSummary';
import GenerateQuiz from './pages/GenerateQuiz';
import TakeQuiz from './pages/TakeQuiz';
import Flashcards from './pages/Flashcards';
import StudyPlan from './pages/StudyPlan';
import Analytics from './pages/Analytics';
import Layout from './components/Layout';
import './App.css';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="upload" element={<UploadDocuments />} />
            <Route path="ask" element={<AskQuestion />} />
            <Route path="summary" element={<GenerateSummary />} />
            <Route path="quiz/generate" element={<GenerateQuiz />} />
            <Route path="quiz/take" element={<TakeQuiz />} />
            <Route path="flashcards" element={<Flashcards />} />
            <Route path="study-plan" element={<StudyPlan />} />
            <Route path="analytics" element={<Analytics />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
