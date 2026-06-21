from typing import Optional, List, Dict
import logging
from bson import ObjectId
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json
import re

from models.quiz import (
    QuizResponse, QuizInDB, QuizGenerateRequest,
    QuizSubmission, QuizResult, QuizResultInDB,
    QuizQuestion
)
from database.mongodb import get_database
from database.qdrant_client import get_qdrant_client
from config import settings

logger = logging.getLogger(__name__)


class QuizService:
    def __init__(self):
        self.db = get_database()
        self.quizzes_collection = self.db.quizzes
        self.results_collection = self.db.results
        self.documents_collection = self.db.documents
        
        # Initialize ChatGroq LLM
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.8,  # Higher for more varied questions
            max_tokens=4000  # Increased for multiple questions
        )
        
        # Setup quiz generation chains
        self._setup_quiz_chains()
    
    def _setup_quiz_chains(self):
        """Setup LangChain chains for quiz generation"""
        
        # MCQ Generation Chain with JSON output
        mcq_prompt = PromptTemplate(
            input_variables=["text", "num_questions"],
            template="""You are a teacher creating multiple choice questions from study material.

IMPORTANT: Generate EXACTLY {num_questions} questions. Each question must be separated by === on its own line.

For each question, follow this EXACT format:

QUESTION: [Your question here]
A) [First option]
B) [Second option]
C) [Third option]
D) [Fourth option]
CORRECT: [Letter A, B, C, or D]
TOPIC: [Topic name]
===

Rules:
1. Generate EXACTLY {num_questions} questions
2. Each question MUST end with ===
3. Questions should test understanding, not just memory
4. Each question must have exactly 4 options (A, B, C, D)
5. Only ONE option should be correct
6. Make incorrect options plausible but clearly wrong

Study Material:
{text}

Now generate EXACTLY {num_questions} multiple choice questions following the format above:"""
        )
        self.mcq_chain = LLMChain(llm=self.llm, prompt=mcq_prompt, verbose=False)
        
        # Short Answer Chain
        short_prompt = PromptTemplate(
            input_variables=["text", "num_questions"],
            template="""You are a teacher creating short answer questions from study material.

Generate exactly {num_questions} short answer questions from the following text.

Rules:
1. Questions should require 2-4 sentence answers
2. Focus on "What", "Why", "How", "Explain" type questions
3. Provide concise model answers
4. Cover different topics

Format each question EXACTLY like this:
QUESTION: [Clear question requiring short explanation]
ANSWER: [2-4 sentence model answer]
TOPIC: [Topic name]
===

Study Material:
{text}

Generate {num_questions} short answer questions now:"""
        )
        self.short_chain = LLMChain(llm=self.llm, prompt=short_prompt, verbose=False)
        
        # Long Answer Chain
        long_prompt = PromptTemplate(
            input_variables=["text", "num_questions"],
            template="""You are a teacher creating long answer questions from study material.

Generate exactly {num_questions} long answer questions from the following text.

Rules:
1. Questions should require detailed explanations (1-2 paragraphs)
2. Ask "Discuss", "Analyze", "Compare", "Describe in detail" type questions
3. Provide comprehensive model answers
4. Cover major concepts

Format each question EXACTLY like this:
QUESTION: [Complex question requiring detailed explanation]
ANSWER: [Comprehensive 1-2 paragraph model answer]
TOPIC: [Topic name]
===

Study Material:
{text}

Generate {num_questions} long answer questions now:"""
        )
        self.long_chain = LLMChain(llm=self.llm, prompt=long_prompt, verbose=False)
        
        # Answer Evaluation Chain
        eval_prompt = PromptTemplate(
            input_variables=["question", "model_answer", "student_answer"],
            template="""You are evaluating a student's answer.

Question: {question}

Model Answer: {model_answer}

Student's Answer: {student_answer}

Evaluate if the student's answer covers the key concepts from the model answer.

Rules:
1. The answer doesn't need to be word-for-word identical
2. Check if main concepts and key points are covered
3. Ignore minor wording differences
4. Be fair but maintain standards

Respond with ONLY ONE WORD:
- "CORRECT" if the student covered the key concepts (60%+ match)
- "INCORRECT" if major concepts are missing

Evaluation:"""
        )
        self.eval_chain = LLMChain(llm=self.llm, prompt=eval_prompt, verbose=False)
    
    async def generate_quiz(
        self,
        request: QuizGenerateRequest,
        user_id: str
    ) -> Optional[QuizResponse]:
        """Generate quiz from document"""
        try:
            logger.info(f"Generating quiz: {request.num_mcq} MCQ, {request.num_short} short, {request.num_long} long")
            
            # Verify document exists and user owns it
            document = await self.documents_collection.find_one({
                "_id": ObjectId(request.document_id),
                "user_id": user_id
            })
            
            if not document:
                logger.warning(f"Document not found or access denied: {request.document_id}")
                return None
            
            # Get document text from Qdrant
            text_content = await self._get_document_text(request.document_id, user_id)
            
            if not text_content:
                logger.warning(f"No content found for document: {request.document_id}")
                return None
            
            # Limit text to prevent token overflow (keep first 5000 chars for better context)
            if len(text_content) > 5000:
                text_content = text_content[:5000]
            
            logger.info(f"Using {len(text_content)} characters of content")
            
            # Generate questions
            all_questions = []
            
            # Generate MCQs
            if request.num_mcq > 0:
                logger.info(f"Generating {request.num_mcq} MCQs...")
                mcqs = await self._generate_mcqs(text_content, request.num_mcq)
                all_questions.extend(mcqs)
                logger.info(f"Generated {len(mcqs)} MCQs")
            
            # Generate Short Answer Questions
            if request.num_short > 0:
                logger.info(f"Generating {request.num_short} short answer questions...")
                short_questions = await self._generate_short_questions(text_content, request.num_short)
                all_questions.extend(short_questions)
                logger.info(f"Generated {len(short_questions)} short answer questions")
            
            # Generate Long Answer Questions
            if request.num_long > 0:
                logger.info(f"Generating {request.num_long} long answer questions...")
                long_questions = await self._generate_long_questions(text_content, request.num_long)
                all_questions.extend(long_questions)
                logger.info(f"Generated {len(long_questions)} long answer questions")
            
            if not all_questions:
                logger.error("Failed to generate any questions")
                return None
            
            # Save quiz to database
            quiz_dict = {
                "user_id": user_id,
                "document_id": request.document_id,
                "questions": [q.dict() for q in all_questions],
                "generated_at": datetime.utcnow()
            }
            
            result = await self.quizzes_collection.insert_one(quiz_dict)
            quiz_id = str(result.inserted_id)
            quiz_dict["_id"] = quiz_id
            
            logger.info(f"Quiz saved with ID {quiz_id}, total questions: {len(all_questions)}")
            
            return QuizResponse(**quiz_dict)
            
        except Exception as e:
            logger.error(f"Error generating quiz: {e}", exc_info=True)
            return None
    
    async def _get_document_text(self, document_id: str, user_id: str) -> Optional[str]:
        """Get document text from Qdrant"""
        try:
            client = get_qdrant_client()
            
            # Scroll through all chunks for this document
            chunks, next_page = client.scroll(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                scroll_filter={
                    "must": [
                        {"key": "document_id", "match": {"value": document_id}},
                        {"key": "user_id", "match": {"value": user_id}}
                    ]
                },
                limit=100  # Get up to 100 chunks
            )
            
            if not chunks:
                logger.warning(f"No chunks found for document {document_id}")
                return None
            
            # Extract and combine text
            texts = [chunk.payload.get("text", "") for chunk in chunks]
            full_text = "\n\n".join(texts)
            
            logger.info(f"Retrieved {len(chunks)} chunks, total length: {len(full_text)}")
            return full_text
            
        except Exception as e:
            logger.error(f"Error retrieving document text: {e}")
            return None
    
    async def _generate_mcqs(self, text: str, num_questions: int) -> List[QuizQuestion]:
        """Generate MCQ questions with retry logic"""
        all_questions = []
        max_attempts = 3
        
        try:
            for attempt in range(1, max_attempts + 1):
                # Calculate how many more questions we need
                needed = num_questions - len(all_questions)
                if needed <= 0:
                    break
                
                logger.info(f"Attempt {attempt}/{max_attempts}: Generating {needed} MCQs...")
                
                # Generate questions using LLM
                response = self.mcq_chain.run(text=text, num_questions=needed)
                
                # Log the raw response for debugging
                if attempt == 1:
                    logger.debug(f"LLM Response (first 800 chars): {response[:800]}")
                
                # Parse response
                questions = self._parse_mcq_response(response)
                
                logger.info(f"Attempt {attempt}: Parsed {len(questions)} MCQs")
                
                # Add new questions (avoid duplicates)
                for q in questions:
                    # Check if question already exists
                    if not any(existing.question == q.question for existing in all_questions):
                        all_questions.append(q)
                
                # If we got enough questions, stop
                if len(all_questions) >= num_questions:
                    logger.info(f"✓ Successfully generated {len(all_questions)} MCQs")
                    break
                
                # If first attempt failed badly, log the full response
                if attempt == 1 and len(questions) < needed // 2:
                    logger.warning(f"First attempt only generated {len(questions)}/{needed} questions")
                    logger.debug(f"Full LLM response: {response}")
            
            if len(all_questions) < num_questions:
                logger.warning(f"After {max_attempts} attempts: Generated {len(all_questions)}/{num_questions} MCQs")
            
            return all_questions[:num_questions]  # Return exactly num_questions
            
        except Exception as e:
            logger.error(f"Error generating MCQs: {e}", exc_info=True)
            return all_questions  # Return what we have
    
    def _parse_mcq_response(self, response: str) -> List[QuizQuestion]:
        """Parse MCQ response from LLM with improved flexibility"""
        questions = []
        
        try:
            # Split by === separator
            blocks = [b.strip() for b in response.split("===") if b.strip()]
            
            logger.info(f"Found {len(blocks)} question blocks to parse")
            
            for idx, block in enumerate(blocks, 1):
                if not block:
                    continue
                
                # Check if block contains question (case-insensitive)
                if "QUESTION:" not in block.upper() and "Q:" not in block.upper():
                    logger.debug(f"Block {idx} doesn't contain QUESTION marker")
                    continue
                
                try:
                    # Extract question - more flexible pattern
                    question_patterns = [
                        r'QUESTION:\s*(.+?)(?=\n[A-D][\):\.])',
                        r'Q:\s*(.+?)(?=\n[A-D][\):\.])',
                        r'QUESTION:\s*(.+?)(?=\nA[\):\.])'
                    ]
                    
                    question_text = None
                    for pattern in question_patterns:
                        match = re.search(pattern, block, re.IGNORECASE | re.DOTALL)
                        if match:
                            question_text = match.group(1).strip()
                            # Clean up newlines within question
                            question_text = ' '.join(question_text.split('\n')).strip()
                            break
                    
                    if not question_text:
                        logger.debug(f"Block {idx}: Could not extract question")
                        continue
                    
                    # Extract options - try multiple formats
                    options = []
                    for letter in ['A', 'B', 'C', 'D']:
                        # Try A), A., A:, or just A followed by space
                        patterns = [
                            rf'{letter}\)\s*(.+?)(?=\n[B-D][\):\.]|CORRECT|ANSWER|TOPIC|$)',
                            rf'{letter}\.\s*(.+?)(?=\n[B-D][\):\.]|CORRECT|ANSWER|TOPIC|$)',
                            rf'{letter}:\s*(.+?)(?=\n[B-D][\):\.]|CORRECT|ANSWER|TOPIC|$)',
                            rf'{letter}\s+(.+?)(?=\n[B-D][\):\.\s]|CORRECT|ANSWER|TOPIC|$)'
                        ]
                        
                        option_text = None
                        for pattern in patterns:
                            match = re.search(pattern, block, re.IGNORECASE | re.DOTALL)
                            if match:
                                option_text = match.group(1).strip()
                                # Clean up newlines within option
                                option_text = ' '.join(option_text.split('\n')).strip()
                                # Remove any trailing CORRECT/ANSWER/TOPIC text
                                option_text = re.sub(r'(CORRECT|ANSWER|TOPIC).*$', '', option_text, flags=re.IGNORECASE).strip()
                                break
                        
                        if option_text:
                            options.append(f"{letter}) {option_text}")
                    
                    if len(options) != 4:
                        logger.debug(f"Block {idx}: Found {len(options)} options, need 4")
                        continue
                    
                    # Extract correct answer
                    correct_patterns = [
                        r'CORRECT:\s*([A-D])',
                        r'ANSWER:\s*([A-D])',
                        r'CORRECT\s+ANSWER:\s*([A-D])'
                    ]
                    
                    correct_answer = None
                    for pattern in correct_patterns:
                        match = re.search(pattern, block, re.IGNORECASE)
                        if match:
                            correct_answer = match.group(1).strip().upper()
                            break
                    
                    if not correct_answer:
                        logger.debug(f"Block {idx}: Could not extract correct answer")
                        continue
                    
                    # Extract topic
                    topic_match = re.search(r'TOPIC:\s*(.+?)(?=\n|$)', block, re.IGNORECASE)
                    topic = topic_match.group(1).strip() if topic_match else "General"
                    
                    # Create question
                    questions.append(QuizQuestion(
                        question=question_text,
                        question_type="mcq",
                        options=options,
                        correct_answer=correct_answer,
                        topic=topic
                    ))
                    
                    logger.debug(f"Block {idx}: ✓ Successfully parsed MCQ")
                    
                except Exception as e:
                    logger.warning(f"Block {idx}: Failed to parse - {e}")
                    logger.debug(f"Block {idx} content preview: {block[:300]}...")
                    continue
            
            logger.info(f"✓ Successfully parsed {len(questions)} MCQs out of {len(blocks)} blocks")
            return questions
            
        except Exception as e:
            logger.error(f"Error parsing MCQ response: {e}", exc_info=True)
            return []
    
    async def _generate_short_questions(self, text: str, num_questions: int) -> List[QuizQuestion]:
        """Generate short answer questions"""
        try:
            response = self.short_chain.run(text=text, num_questions=num_questions)
            questions = self._parse_text_questions(response, "short_answer")
            
            if len(questions) < num_questions:
                logger.warning(f"Requested {num_questions} short questions but only generated {len(questions)}")
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating short questions: {e}")
            return []
    
    async def _generate_long_questions(self, text: str, num_questions: int) -> List[QuizQuestion]:
        """Generate long answer questions"""
        try:
            response = self.long_chain.run(text=text, num_questions=num_questions)
            questions = self._parse_text_questions(response, "long_answer")
            
            if len(questions) < num_questions:
                logger.warning(f"Requested {num_questions} long questions but only generated {len(questions)}")
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating long questions: {e}")
            return []
    
    def _parse_text_questions(self, response: str, question_type: str) -> List[QuizQuestion]:
        """Parse short/long answer questions"""
        questions = []
        
        try:
            # Split by === separator
            blocks = response.split("===")
            
            for block in blocks:
                block = block.strip()
                if not block or "QUESTION:" not in block:
                    continue
                
                try:
                    # Extract question
                    question_match = re.search(r'QUESTION:\s*(.+?)(?=\nANSWER:)', block, re.DOTALL)
                    if not question_match:
                        continue
                    question_text = question_match.group(1).strip()
                    
                    # Extract answer
                    answer_match = re.search(r'ANSWER:\s*(.+?)(?=\nTOPIC:|$)', block, re.DOTALL)
                    if not answer_match:
                        continue
                    answer_text = answer_match.group(1).strip()
                    
                    # Extract topic
                    topic_match = re.search(r'TOPIC:\s*(.+?)(?=\n|$)', block)
                    topic = topic_match.group(1).strip() if topic_match else "General"
                    
                    # Validate
                    if question_text and answer_text:
                        questions.append(QuizQuestion(
                            question=question_text,
                            question_type=question_type,
                            correct_answer=answer_text,
                            topic=topic
                        ))
                    
                except Exception as e:
                    logger.warning(f"Failed to parse text question block: {e}")
                    continue
            
            return questions
            
        except Exception as e:
            logger.error(f"Error parsing text questions: {e}")
            return []
    
    async def submit_quiz(
        self,
        submission: QuizSubmission,
        user_id: str
    ) -> Optional[QuizResult]:
        """Evaluate quiz submission"""
        try:
            logger.info(f"Evaluating quiz submission for quiz {submission.quiz_id}")
            logger.info(f"Received {len(submission.answers)} answers: {submission.answers}")
            
            # Get quiz
            quiz = await self.quizzes_collection.find_one({
                "_id": ObjectId(submission.quiz_id),
                "user_id": user_id
            })
            
            if not quiz:
                logger.warning(f"Quiz not found: {submission.quiz_id}")
                return None
            
            questions = quiz["questions"]
            total_questions = len(questions)
            correct_answers = 0
            topic_performance = {}
            detailed_results = []
            
            logger.info(f"Evaluating {total_questions} questions")
            
            # Evaluate each answer
            for idx, question in enumerate(questions):
                # Try both string and integer keys
                user_answer = submission.answers.get(str(idx)) or submission.answers.get(idx, "")
                user_answer = user_answer.strip() if user_answer else ""
                
                logger.debug(f"Q{idx}: key='{idx}', answer='{user_answer}'")
                
                # Skip if no answer provided
                if not user_answer:
                    is_correct = False
                elif question["question_type"] == "mcq":
                    # MCQ: exact match
                    is_correct = user_answer.upper() == question["correct_answer"].upper()
                    logger.debug(f"Q{idx} MCQ: '{user_answer}' vs '{question['correct_answer']}' = {is_correct}")
                else:
                    # Short/Long answer: use LLM evaluation
                    is_correct = await self._evaluate_text_answer(
                        question["question"],
                        user_answer,
                        question["correct_answer"]
                    )
                
                if is_correct:
                    correct_answers += 1
                
                # Track topic performance
                topic = question.get("topic", "General")
                if topic not in topic_performance:
                    topic_performance[topic] = {"correct": 0, "total": 0}
                
                topic_performance[topic]["total"] += 1
                if is_correct:
                    topic_performance[topic]["correct"] += 1
                
                # Store detailed result
                detailed_results.append({
                    "question_index": idx,
                    "question": question["question"],
                    "question_type": question["question_type"],
                    "user_answer": user_answer if user_answer else "[No answer provided]",
                    "correct_answer": question["correct_answer"],
                    "is_correct": is_correct,
                    "topic": topic
                })
            
            # Calculate score and accuracy
            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            accuracy = score / 100
            
            # Identify weak and strong topics
            weak_topics = []
            strong_topics = []
            
            for topic, perf in topic_performance.items():
                topic_accuracy = perf["correct"] / perf["total"] if perf["total"] > 0 else 0
                if topic_accuracy < 0.5:  # Less than 50%
                    weak_topics.append(topic)
                elif topic_accuracy >= 0.8:  # 80% or more
                    strong_topics.append(topic)
            
            # Save result
            result_dict = {
                "user_id": user_id,
                "quiz_id": submission.quiz_id,
                "score": round(score, 2),
                "accuracy": round(accuracy, 2),
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "weak_topics": weak_topics,
                "strong_topics": strong_topics,
                "attempted_at": datetime.utcnow(),
                "detailed_results": detailed_results
            }
            
            result = await self.results_collection.insert_one(result_dict)
            result_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"Quiz evaluated: {correct_answers}/{total_questions} correct ({score:.1f}%)")
            
            return QuizResult(**result_dict)
            
        except Exception as e:
            logger.error(f"Error submitting quiz: {e}", exc_info=True)
            return None
    
    async def _evaluate_text_answer(
        self,
        question: str,
        user_answer: str,
        model_answer: str
    ) -> bool:
        """Evaluate text answer using LLM"""
        try:
            # Use LLM to evaluate
            response = self.eval_chain.run(
                question=question,
                model_answer=model_answer,
                student_answer=user_answer
            )
            
            # Check if response contains "CORRECT"
            is_correct = "CORRECT" in response.upper() and "INCORRECT" not in response.upper()
            
            logger.debug(f"Answer evaluation: {is_correct}")
            return is_correct
            
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            # Default to incorrect if evaluation fails
            return False
    
    async def get_user_quiz(
        self,
        quiz_id: str,
        user_id: str
    ) -> Optional[QuizResponse]:
        """Get a specific quiz"""
        try:
            quiz = await self.quizzes_collection.find_one({
                "_id": ObjectId(quiz_id),
                "user_id": user_id
            })
            
            if not quiz:
                return None
            
            quiz["_id"] = str(quiz["_id"])
            return QuizResponse(**quiz)
            
        except Exception as e:
            logger.error(f"Error getting quiz: {e}")
            return None
    
    async def get_quiz_result(
        self,
        result_id: str,
        user_id: str
    ) -> Optional[QuizResult]:
        """Get quiz result"""
        try:
            result = await self.results_collection.find_one({
                "_id": ObjectId(result_id),
                "user_id": user_id
            })
            
            if not result:
                return None
            
            result["_id"] = str(result["_id"])
            return QuizResult(**result)
            
        except Exception as e:
            logger.error(f"Error getting result: {e}")
            return None
    
    async def get_user_quizzes(
        self,
        user_id: str,
        document_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[QuizResponse]:
        """Get all quizzes for a user"""
        try:
            query = {"user_id": user_id}
            if document_id:
                query["document_id"] = document_id
            
            cursor = self.quizzes_collection.find(query).sort("generated_at", -1).skip(skip).limit(limit)
            quizzes = await cursor.to_list(length=limit)
            
            for quiz in quizzes:
                quiz["_id"] = str(quiz["_id"])
            
            return [QuizResponse(**quiz) for quiz in quizzes]
            
        except Exception as e:
            logger.error(f"Error getting quizzes: {e}")
            return []
    
    async def get_user_results(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[QuizResult]:
        """Get all quiz results for a user"""
        try:
            cursor = self.results_collection.find({"user_id": user_id}).sort("attempted_at", -1).skip(skip).limit(limit)
            results = await cursor.to_list(length=limit)
            
            for result in results:
                result["_id"] = str(result["_id"])
            
            return [QuizResult(**result) for result in results]
            
        except Exception as e:
            logger.error(f"Error getting results: {e}")
            return []
