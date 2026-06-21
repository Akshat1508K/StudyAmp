# Requirements Document

## Introduction

The Campus Study Assistant is an AI-powered adaptive learning platform designed for college students. The system enables students to upload study materials (PDFs, notes, PowerPoint presentations) and provides personalized learning experiences through RAG-based question answering, automated quiz generation, flashcard creation, performance analytics, and adaptive study plans. The platform uses local LLM inference (Ollama with Qwen 2.5 3B), vector search (Qdrant), and document storage (MongoDB) to deliver a privacy-focused, production-ready learning solution.

## Glossary

- **System**: The Campus Study Assistant platform
- **Authentication_Service**: JWT-based user authentication and authorization component
- **Document_Processor**: Component that extracts, chunks, and embeds uploaded documents
- **RAG_Engine**: Retrieval-Augmented Generation pipeline using LangChain, Qdrant, and Ollama
- **Quiz_Generator**: Component that generates quiz questions from uploaded materials
- **Quiz_Evaluator**: Component that scores quizzes and analyzes performance
- **Adaptive_Engine**: Component that analyzes performance data and generates personalized study plans
- **Flashcard_Generator**: Component that creates question-answer flashcard pairs
- **Analytics_Engine**: Component that computes performance metrics and trends
- **Vector_Store**: Qdrant vector database storing document embeddings
- **Document_Store**: MongoDB database storing user data, documents, quizzes, and results
- **User**: A registered college student using the platform
- **Document**: An uploaded study material (PDF, notes, or presentation)
- **Chunk**: A text segment from a document with associated metadata
- **Weak_Topic**: A subject area where the User scored below 60% accuracy
- **Strong_Topic**: A subject area where the User scored above 80% accuracy
- **Study_Plan**: A day-by-day revision schedule targeting weak topics
- **Embedding_Model**: The nomic-embed-text model for converting text to vectors
- **LLM**: The Ollama qwen2.5:3b language model

## Requirements

### Requirement 1: User Registration and Authentication

**User Story:** As a college student, I want to register and log in securely, so that my study materials and progress remain private and accessible only to me.

#### Acceptance Criteria

1. WHEN a User submits registration details (name, email, password), THE Authentication_Service SHALL hash the password using bcrypt and store the user record in the Document_Store
2. WHEN a User attempts to register with an existing email, THE Authentication_Service SHALL return an error indicating the email is already registered
3. WHEN a User submits valid login credentials, THE Authentication_Service SHALL generate a JWT access token with user_id and email claims
4. WHEN a User submits invalid login credentials, THE Authentication_Service SHALL return an authentication error
5. WHEN a User accesses protected endpoints without a valid JWT token, THE Authentication_Service SHALL return an unauthorized error
6. THE Authentication_Service SHALL store user records with fields: _id, name, email, password_hash, and created_at timestamp

### Requirement 2: Document Upload and Metadata Storage

**User Story:** As a User, I want to upload my study materials (PDFs, notes, presentations), so that the System can process them for learning activities.

#### Acceptance Criteria

1. WHEN a User uploads a PDF file, THE System SHALL accept files with .pdf extension
2. WHEN a User uploads a document, THE System SHALL store metadata in the Document_Store with fields: _id, user_id, file_name, upload_date, total_pages, and subject_name
3. WHEN a User provides a subject name during upload, THE System SHALL associate that subject with all chunks extracted from the document
4. WHEN a document upload fails, THE System SHALL return a descriptive error message indicating the failure reason
5. THE System SHALL extract the total page count from uploaded PDFs and store it in the metadata

### Requirement 3: Document Processing Pipeline

**User Story:** As a User, I want my uploaded documents to be automatically processed, so that I can ask questions and generate quizzes from them.

#### Acceptance Criteria

1. WHEN a document is uploaded, THE Document_Processor SHALL extract text using PyPDFLoader
2. WHEN text is extracted, THE Document_Processor SHALL split the text into chunks using RecursiveCharacterTextSplitter
3. WHEN chunks are created, THE Document_Processor SHALL generate embeddings for each chunk using the Embedding_Model
4. WHEN embeddings are generated, THE Document_Processor SHALL store each chunk in the Vector_Store with metadata: user_id, document_id, chunk_id, and subject
5. IF text extraction fails, THEN THE Document_Processor SHALL log the error and return a failure status to the User
6. THE Document_Processor SHALL process each document chunk with a maximum size of 1000 characters and 200 character overlap

### Requirement 4: RAG-Based Question Answering

**User Story:** As a User, I want to ask questions about my uploaded materials, so that I can quickly find information without manually searching through documents.

#### Acceptance Criteria

1. WHEN a User submits a question, THE RAG_Engine SHALL generate an embedding for the question using the Embedding_Model
2. WHEN a question embedding is generated, THE RAG_Engine SHALL retrieve the top 5 most similar chunks from the Vector_Store filtered by the User's user_id
3. WHEN relevant chunks are retrieved, THE RAG_Engine SHALL construct a prompt with the retrieved context and submit it to the LLM
4. WHEN the LLM generates a response, THE RAG_Engine SHALL return the answer to the User
5. IF no relevant chunks are found with similarity above 0.5, THEN THE RAG_Engine SHALL return "Information not found in uploaded notes."
6. THE RAG_Engine SHALL only retrieve chunks belonging to the requesting User

### Requirement 5: Summary Generation

**User Story:** As a User, I want to generate summaries of my study materials, so that I can quickly review key concepts before exams.

#### Acceptance Criteria

1. WHEN a User requests a short summary for a document, THE System SHALL generate a summary with maximum 500 words using the LLM
2. WHEN a User requests a detailed summary for a document, THE System SHALL generate a summary with maximum 2000 words using the LLM
3. WHEN a User requests an exam day summary for a document, THE System SHALL generate a concise bullet-point summary with maximum 300 words using the LLM
4. WHEN a summary is generated, THE System SHALL store the summary in the Document_Store with fields: _id, user_id, document_id, summary_type, summary_text, and generated_at timestamp
5. THE System SHALL retrieve document chunks from the Vector_Store before generating summaries

### Requirement 6: Quiz Question Generation

**User Story:** As a User, I want the System to generate quizzes from my study materials, so that I can test my knowledge and identify weak areas.

#### Acceptance Criteria

1. WHEN a User requests a quiz for a document, THE Quiz_Generator SHALL retrieve relevant chunks from the Vector_Store for that document
2. WHEN chunks are retrieved, THE Quiz_Generator SHALL generate multiple-choice questions (MCQs) with 4 options and one correct answer using the LLM
3. WHEN generating MCQs, THE Quiz_Generator SHALL also generate short answer questions requiring 2-3 sentence responses
4. WHEN generating quiz content, THE Quiz_Generator SHALL also generate long answer questions requiring detailed explanations
5. WHEN questions are generated, THE Quiz_Generator SHALL store the quiz in the Document_Store with fields: _id, user_id, document_id, questions array, and generated_at timestamp
6. THE Quiz_Generator SHALL generate at least 10 MCQs, 5 short answer questions, and 3 long answer questions per quiz

### Requirement 7: Quiz Evaluation and Performance Analysis

**User Story:** As a User, I want my quiz attempts to be evaluated automatically, so that I can see my score and understand my strengths and weaknesses.

#### Acceptance Criteria

1. WHEN a User submits a quiz attempt, THE Quiz_Evaluator SHALL compare MCQ answers against correct answers and calculate the score
2. WHEN a User submits short or long answers, THE Quiz_Evaluator SHALL use the LLM to evaluate answer quality and assign scores
3. WHEN scoring is complete, THE Quiz_Evaluator SHALL calculate overall accuracy as (correct_answers / total_questions) * 100
4. WHEN accuracy is calculated, THE Quiz_Evaluator SHALL identify topics with accuracy below 60% as Weak_Topics
5. WHEN accuracy is calculated, THE Quiz_Evaluator SHALL identify topics with accuracy above 80% as Strong_Topics
6. WHEN evaluation is complete, THE Quiz_Evaluator SHALL store results in the Document_Store with fields: _id, user_id, quiz_id, score, accuracy, weak_topics array, strong_topics array, and attempted_at timestamp

### Requirement 8: Adaptive Learning and Study Plan Generation

**User Story:** As a User, I want the System to create a personalized study plan based on my performance, so that I can focus on topics I need to improve.

#### Acceptance Criteria

1. WHEN quiz results are stored, THE Adaptive_Engine SHALL analyze the User's weak_topics across all quiz attempts
2. WHEN weak topics are identified, THE Adaptive_Engine SHALL prioritize topics with the lowest accuracy scores
3. WHEN topics are prioritized, THE Adaptive_Engine SHALL generate a day-by-day study plan with one topic per day
4. WHEN a study plan is generated, THE Adaptive_Engine SHALL allocate more days to topics with lower accuracy
5. THE Adaptive_Engine SHALL store study plans in the Document_Store with fields: _id, user_id, plan_items array (each with day_number, topic, and recommended_resources), and created_at timestamp
6. THE Adaptive_Engine SHALL generate study plans with a minimum of 7 days and maximum of 30 days

### Requirement 9: Flashcard Generation

**User Story:** As a User, I want to generate flashcards from my study materials, so that I can practice active recall and spaced repetition.

#### Acceptance Criteria

1. WHEN a User requests flashcards for a document, THE Flashcard_Generator SHALL retrieve document chunks from the Vector_Store
2. WHEN chunks are retrieved, THE Flashcard_Generator SHALL use the LLM to generate question-answer pairs
3. WHEN flashcards are generated, THE Flashcard_Generator SHALL create at least 20 flashcard pairs per document
4. THE Flashcard_Generator SHALL store flashcards in the Document_Store with fields: _id, user_id, document_id, flashcards array (each with question and answer), and generated_at timestamp
5. THE Flashcard_Generator SHALL ensure each flashcard question is concise (maximum 100 characters)

### Requirement 10: Student Performance Dashboard

**User Story:** As a User, I want to view my learning dashboard, so that I can track my progress and see recommendations.

#### Acceptance Criteria

1. WHEN a User accesses the dashboard, THE System SHALL display all uploaded documents with file names and upload dates
2. WHEN displaying the dashboard, THE System SHALL show quiz history with scores and dates
3. WHEN displaying the dashboard, THE System SHALL show performance trends with accuracy over time
4. WHEN displaying the dashboard, THE System SHALL list the User's current weak topics
5. WHEN displaying the dashboard, THE System SHALL list the User's current strong topics
6. WHEN displaying the dashboard, THE System SHALL show study progress as percentage of completed study plan days

### Requirement 11: Analytics and Performance Metrics

**User Story:** As a User, I want to see detailed analytics of my learning performance, so that I can understand my improvement over time and topic mastery.

#### Acceptance Criteria

1. WHEN a User accesses analytics, THE Analytics_Engine SHALL calculate average score across all quiz attempts
2. WHEN calculating analytics, THE Analytics_Engine SHALL compute topic-wise mastery as average accuracy per subject
3. WHEN calculating analytics, THE Analytics_Engine SHALL identify improvement trends by comparing scores across time periods
4. WHEN calculating analytics, THE Analytics_Engine SHALL identify the most frequently incorrect topics across all quizzes
5. THE Analytics_Engine SHALL display metrics with graphical visualizations showing trends over time

### Requirement 12: Data Isolation and Security

**User Story:** As a User, I want my data to be isolated from other users, so that my study materials and performance remain private.

#### Acceptance Criteria

1. WHEN any component retrieves data from the Vector_Store, THE System SHALL filter results by the requesting User's user_id
2. WHEN any component retrieves data from the Document_Store, THE System SHALL filter results by the requesting User's user_id
3. THE System SHALL validate JWT tokens on all protected endpoints before processing requests
4. THE System SHALL reject requests attempting to access resources belonging to other users
5. THE System SHALL log unauthorized access attempts for security monitoring

### Requirement 13: Error Handling and Logging

**User Story:** As a system administrator, I want comprehensive error handling and logging, so that I can diagnose issues and maintain system reliability.

#### Acceptance Criteria

1. WHEN any component encounters an error, THE System SHALL log the error with timestamp, component name, error type, and stack trace
2. WHEN the LLM or Embedding_Model is unavailable, THE System SHALL return a service unavailable error to the User
3. WHEN the Vector_Store or Document_Store is unavailable, THE System SHALL return a database connection error to the User
4. THE System SHALL validate all input parameters and return descriptive validation errors for invalid inputs
5. THE System SHALL implement retry logic with exponential backoff for transient failures in external services

### Requirement 14: Configuration and Environment Management

**User Story:** As a developer, I want configuration managed through environment variables, so that the System can be deployed across different environments securely.

#### Acceptance Criteria

1. THE System SHALL load database connection strings from environment variables
2. THE System SHALL load JWT secret keys from environment variables
3. THE System SHALL load Ollama endpoint URLs from environment variables
4. THE System SHALL load Qdrant connection parameters from environment variables
5. THE System SHALL validate that all required environment variables are present at startup and exit with descriptive errors if any are missing

### Requirement 15: API Documentation and Type Safety

**User Story:** As a developer, I want type-safe API endpoints with automatic documentation, so that the System is maintainable and easy to integrate with.

#### Acceptance Criteria

1. THE System SHALL use Pydantic models for all request and response schemas
2. THE System SHALL generate OpenAPI documentation automatically from endpoint definitions
3. THE System SHALL include Python type hints in all function signatures
4. THE System SHALL validate request payloads against Pydantic schemas and return validation errors for invalid requests
5. THE System SHALL document all API endpoints with descriptions, parameter explanations, and example responses
