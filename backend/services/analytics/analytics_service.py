from typing import Dict, List
import logging
from datetime import datetime, timedelta

from database.mongodb import get_database

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self):
        self.db = get_database()
        self.results_collection = self.db.results
        self.documents_collection = self.db.documents
    
    async def get_user_analytics(self, user_id: str) -> Dict:
        """Get comprehensive analytics for a user"""
        try:
            # Get all quiz results
            cursor = self.results_collection.find({"user_id": user_id}).sort("attempted_at", 1)
            results = await cursor.to_list(length=1000)
            
            if not results:
                return {
                    "overview": {
                        "total_quizzes": 0,
                        "average_score": 0,
                        "total_questions": 0,
                        "total_correct": 0
                    },
                    "performance_over_time": [],
                    "topic_mastery": {},
                    "frequently_incorrect_topics": [],
                    "improvement_rate": 0
                }
            
            # Overview statistics
            total_quizzes = len(results)
            total_questions = sum(r["total_questions"] for r in results)
            total_correct = sum(r["correct_answers"] for r in results)
            average_score = sum(r["score"] for r in results) / total_quizzes
            
            # Performance over time
            performance_over_time = [
                {
                    "date": r["attempted_at"].strftime("%Y-%m-%d"),
                    "score": r["score"],
                    "accuracy": r["accuracy"]
                }
                for r in results
            ]
            
            # Topic mastery
            topic_stats = {}
            for result in results:
                for detail in result.get("detailed_results", []):
                    topic = detail.get("topic", "General")
                    if topic not in topic_stats:
                        topic_stats[topic] = {"correct": 0, "total": 0}
                    
                    topic_stats[topic]["total"] += 1
                    if detail.get("is_correct", False):
                        topic_stats[topic]["correct"] += 1
            
            topic_mastery = {
                topic: {
                    "mastery": round((stats["correct"] / stats["total"]) * 100, 2),
                    "attempts": stats["total"]
                }
                for topic, stats in topic_stats.items()
            }
            
            # Frequently incorrect topics
            incorrect_topics = {}
            for result in results:
                for detail in result.get("detailed_results", []):
                    if not detail.get("is_correct", False):
                        topic = detail.get("topic", "General")
                        incorrect_topics[topic] = incorrect_topics.get(topic, 0) + 1
            
            frequently_incorrect = sorted(
                [{"topic": topic, "count": count} for topic, count in incorrect_topics.items()],
                key=lambda x: x["count"],
                reverse=True
            )[:5]
            
            # Calculate improvement rate
            if total_quizzes >= 5:
                recent_avg = sum(r["score"] for r in results[-5:]) / 5
                initial_avg = sum(r["score"] for r in results[:5]) / 5
                improvement_rate = round(recent_avg - initial_avg, 2)
            else:
                improvement_rate = 0
            
            return {
                "overview": {
                    "total_quizzes": total_quizzes,
                    "average_score": round(average_score, 2),
                    "total_questions": total_questions,
                    "total_correct": total_correct
                },
                "performance_over_time": performance_over_time,
                "topic_mastery": topic_mastery,
                "frequently_incorrect_topics": frequently_incorrect,
                "improvement_rate": improvement_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return {}
    
    async def get_dashboard_data(self, user_id: str) -> Dict:
        """Get dashboard data for user"""
        try:
            # Get document count
            document_count = await self.documents_collection.count_documents({"user_id": user_id})
            
            # Get quiz history (last 10)
            cursor = self.results_collection.find({"user_id": user_id}).sort("attempted_at", -1).limit(10)
            quiz_history = await cursor.to_list(length=10)
            
            quiz_history_formatted = [
                {
                    "id": str(r["_id"]),
                    "quiz_id": r["quiz_id"],
                    "score": r["score"],
                    "date": r["attempted_at"].strftime("%Y-%m-%d %H:%M")
                }
                for r in quiz_history
            ]
            
            # Get analytics summary
            analytics = await self.get_user_analytics(user_id)
            
            return {
                "total_documents": document_count,
                "quiz_history": quiz_history_formatted,
                "analytics_summary": analytics
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}
