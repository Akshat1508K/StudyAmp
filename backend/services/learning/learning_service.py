from typing import Optional, List, Dict
import logging
from bson import ObjectId
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from models.learning import (
    StudyPlanResponse, StudyPlanInDB,
    TopicPerformance, StudyPlanDay
)
from database.mongodb import get_database
from config import settings

logger = logging.getLogger(__name__)


class LearningService:
    def __init__(self):
        self.db = get_database()
        self.study_plans_collection = self.db.study_plans
        self.results_collection = self.db.results
        
        # Initialize ChatGroq LLM
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.7,
            max_tokens=2048
        )
        
        # Setup LangChain chains
        self._setup_study_plan_chain()
    
    def _setup_study_plan_chain(self):
        """Setup LangChain chain for study plan generation"""
        study_plan_prompt = PromptTemplate(
            input_variables=["weak_topics", "moderate_topics"],
            template="""You are an adaptive learning assistant. Generate a personalized study plan.

Weak Topics (Need Focus): {weak_topics}
Moderate Topics (Need Reinforcement): {moderate_topics}

Create a day-by-day study plan with specific recommendations for each topic.
Format each day as:
Day X: [Topic]
Description: [What to focus on]
Resources: [Suggested resources]
---

Generate the study plan:"""
        )
        self.study_plan_chain = LLMChain(llm=self.llm, prompt=study_plan_prompt, verbose=False)
    
    async def generate_study_plan(
        self,
        user_id: str
    ) -> Optional[StudyPlanResponse]:
        """Generate personalized study plan based on quiz performance"""
        try:
            # Get all quiz results for user
            cursor = self.results_collection.find({"user_id": user_id}).sort("attempted_at", -1)
            results = await cursor.to_list(length=100)
            
            if not results:
                logger.warning(f"No quiz results found for user: {user_id}")
                return None
            
            # Analyze topic performance
            topic_stats = {}
            
            for result in results:
                for detail in result.get("detailed_results", []):
                    topic = detail.get("topic", "General")
                    if topic not in topic_stats:
                        topic_stats[topic] = {"correct": 0, "total": 0}
                    
                    topic_stats[topic]["total"] += 1
                    if detail.get("is_correct", False):
                        topic_stats[topic]["correct"] += 1
            
            # Calculate topic performance
            weak_topics = []
            strong_topics = []
            moderate_topics = []
            
            for topic, stats in topic_stats.items():
                accuracy = stats["correct"] / stats["total"]
                attempts = stats["total"]
                
                perf = TopicPerformance(
                    topic=topic,
                    accuracy=round(accuracy, 2),
                    attempts=attempts,
                    status="weak" if accuracy < 0.6 else "strong" if accuracy >= 0.8 else "moderate"
                )
                
                if accuracy < 0.6:
                    weak_topics.append(perf)
                elif accuracy >= 0.8:
                    strong_topics.append(perf)
                else:
                    moderate_topics.append(perf)
            
            # Sort by accuracy
            weak_topics.sort(key=lambda x: x.accuracy)
            strong_topics.sort(key=lambda x: x.accuracy, reverse=True)
            
            # Generate study plan
            study_plan = await self._generate_study_plan_days(weak_topics, moderate_topics)
            
            # Generate revision roadmap
            revision_roadmap = self._generate_revision_roadmap(weak_topics, moderate_topics, strong_topics)
            
            # Save study plan
            plan_dict = {
                "user_id": user_id,
                "weak_topics": [t.dict() for t in weak_topics],
                "strong_topics": [t.dict() for t in strong_topics],
                "study_plan": [day.dict() for day in study_plan],
                "revision_roadmap": revision_roadmap,
                "created_at": datetime.utcnow()
            }
            
            result = await self.study_plans_collection.insert_one(plan_dict)
            plan_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"Study plan generated for user: {user_id}")
            
            return StudyPlanResponse(**plan_dict)
            
        except Exception as e:
            logger.error(f"Error generating study plan: {e}")
            return None
    
    async def _generate_study_plan_days(
        self,
        weak_topics: List[TopicPerformance],
        moderate_topics: List[TopicPerformance]
    ) -> List[StudyPlanDay]:
        """Generate day-by-day study plan"""
        plan_days = []
        day = 1
        
        # Focus on weak topics first
        for topic in weak_topics:
            plan_days.append(StudyPlanDay(
                day=day,
                topic=topic.topic,
                description=f"Focus on understanding {topic.topic}. Review fundamentals and practice problems.",
                resources=["Review notes", "Practice questions", "Watch tutorial videos"]
            ))
            day += 1
            
            # Add practice day
            plan_days.append(StudyPlanDay(
                day=day,
                topic=f"{topic.topic} - Practice",
                description=f"Practice problems and take quiz on {topic.topic}",
                resources=["Solve practice problems", "Take quiz", "Review mistakes"]
            ))
            day += 1
        
        # Then moderate topics
        for topic in moderate_topics:
            plan_days.append(StudyPlanDay(
                day=day,
                topic=topic.topic,
                description=f"Reinforce your understanding of {topic.topic}. Focus on advanced concepts.",
                resources=["Advanced notes", "Practice questions", "Real-world examples"]
            ))
            day += 1
        
        # Add final revision days
        all_topics = [t.topic for t in weak_topics + moderate_topics]
        if all_topics:
            plan_days.append(StudyPlanDay(
                day=day,
                topic="Comprehensive Revision",
                description="Review all weak and moderate topics. Take comprehensive quiz.",
                resources=["Review all notes", "Flashcards", "Comprehensive quiz"]
            ))
        
        return plan_days
    
    def _generate_revision_roadmap(
        self,
        weak_topics: List[TopicPerformance],
        moderate_topics: List[TopicPerformance],
        strong_topics: List[TopicPerformance]
    ) -> Dict[str, List[str]]:
        """Generate revision roadmap"""
        roadmap = {
            "Week 1": [t.topic for t in weak_topics[:3]] if len(weak_topics) >= 3 else [t.topic for t in weak_topics],
            "Week 2": [t.topic for t in weak_topics[3:6]] if len(weak_topics) > 3 else [t.topic for t in moderate_topics[:3]],
            "Week 3": [t.topic for t in moderate_topics],
            "Week 4": ["Comprehensive revision of all topics", "Mock tests", "Final preparation"]
        }
        
        return roadmap
    
    async def get_latest_study_plan(
        self,
        user_id: str
    ) -> Optional[StudyPlanResponse]:
        """Get latest study plan for user"""
        try:
            plan = await self.study_plans_collection.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            )
            
            if not plan:
                return None
            
            plan["_id"] = str(plan["_id"])
            return StudyPlanResponse(**plan)
            
        except Exception as e:
            logger.error(f"Error getting study plan: {e}")
            return None
    
    async def get_user_progress(
        self,
        user_id: str
    ) -> Dict:
        """Get user's learning progress"""
        try:
            # Get all results
            cursor = self.results_collection.find({"user_id": user_id}).sort("attempted_at", 1)
            results = await cursor.to_list(length=1000)
            
            if not results:
                return {
                    "total_quizzes": 0,
                    "average_score": 0,
                    "improvement_trend": "No data",
                    "total_questions_attempted": 0
                }
            
            total_quizzes = len(results)
            total_score = sum(r["score"] for r in results)
            average_score = total_score / total_quizzes
            total_questions = sum(r["total_questions"] for r in results)
            
            # Calculate improvement trend
            if total_quizzes >= 3:
                recent_avg = sum(r["score"] for r in results[-3:]) / 3
                older_avg = sum(r["score"] for r in results[:3]) / 3
                improvement = recent_avg - older_avg
                
                if improvement > 10:
                    trend = "Improving significantly"
                elif improvement > 0:
                    trend = "Improving steadily"
                elif improvement > -10:
                    trend = "Stable"
                else:
                    trend = "Needs more practice"
            else:
                trend = "Insufficient data"
            
            return {
                "total_quizzes": total_quizzes,
                "average_score": round(average_score, 2),
                "improvement_trend": trend,
                "total_questions_attempted": total_questions
            }
            
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            return {}
