"""
AI Services Module for Career Platform
Handles integrations with free AI APIs including Hugging Face and OpenAI
"""
import os
import time
import logging
import requests
from typing import List, Dict, Optional, Any
from functools import wraps
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self) -> bool:
        """Check if we can make another API call"""
        now = time.time()
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record that an API call was made"""
        self.calls.append(time.time())

def with_fallback(fallback_func):
    """Decorator to provide fallback functionality when AI APIs fail"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"AI API call failed: {e}. Using fallback.")
                return fallback_func(*args, **kwargs)
        return wrapper
    return decorator

class HuggingFaceClient:
    """Client for Hugging Face Inference API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"
        self.rate_limiter = RateLimiter(max_calls=100, time_window=3600)  # 100 calls per hour
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else None,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, model_name: str, payload: Dict) -> Dict:
        """Make a request to Hugging Face API with rate limiting"""
        if not self.rate_limiter.can_make_call():
            raise Exception("Rate limit exceeded for Hugging Face API")
        
        url = f"{self.base_url}/{model_name}"
        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        self.rate_limiter.record_call()
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")
    
    @with_fallback(lambda self, text: {"embeddings": [0.0] * 384})
    def get_embeddings(self, text: str) -> Dict:
        """Get text embeddings using sentence transformers"""
        payload = {"inputs": text}
        return self._make_request("sentence-transformers/all-MiniLM-L6-v2", payload)
    
    @with_fallback(lambda self, text: [{"label": "TECHNOLOGY", "score": 0.5}])
    def classify_skills(self, text: str) -> List[Dict]:
        """Classify skills into categories"""
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": [
                    "TECHNOLOGY", "COMMUNICATION", "LEADERSHIP", 
                    "ANALYTICAL", "CREATIVE", "MANAGEMENT"
                ]
            }
        }
        return self._make_request("facebook/bart-large-mnli", payload)
    
    @with_fallback(lambda self, profile_text: [{"career": "Software Developer", "confidence": 0.5}])
    def analyze_career_fit(self, profile_text: str) -> List[Dict]:
        """Analyze career fit based on profile text"""
        payload = {
            "inputs": profile_text,
            "parameters": {
                "candidate_labels": [
                    "Software Developer", "Data Scientist", "Product Manager",
                    "Business Analyst", "Marketing Specialist", "Sales Representative",
                    "Mechanical Engineer", "Civil Engineer", "Electrical Engineer",
                    "Financial Analyst", "Human Resources", "Operations Manager"
                ]
            }
        }
        result = self._make_request("facebook/bart-large-mnli", payload)
        
        # Convert to expected format
        if isinstance(result, dict) and 'labels' in result:
            return [
                {"career": label, "confidence": score}
                for label, score in zip(result['labels'], result['scores'])
            ]
        return [{"career": "Software Developer", "confidence": 0.5}]

class OpenAIClient:
    """Client for OpenAI API (free tier)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.rate_limiter = RateLimiter(max_calls=20, time_window=3600)  # Conservative for free tier
        
        # Only import openai if we have an API key
        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("OpenAI library not installed")
                self.client = None
        else:
            self.client = None
    
    @with_fallback(lambda self, text: {"analysis": "Basic skill analysis", "recommendations": []})
    def analyze_profile(self, profile_text: str) -> Dict:
        """Analyze student profile using GPT"""
        if not self.client or not self.rate_limiter.can_make_call():
            raise Exception("OpenAI client not available or rate limit exceeded")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career counselor. Analyze the student profile and provide career recommendations."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this student profile and suggest suitable careers: {profile_text}"
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            self.rate_limiter.record_call()
            
            content = response.choices[0].message.content
            return {
                "analysis": content,
                "recommendations": self._extract_careers_from_text(content)
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _extract_careers_from_text(self, text: str) -> List[str]:
        """Extract career recommendations from GPT response"""
        # Simple extraction - look for common career patterns
        careers = []
        common_careers = [
            "Software Developer", "Data Scientist", "Product Manager",
            "Business Analyst", "Marketing Specialist", "Sales Representative",
            "Mechanical Engineer", "Civil Engineer", "Electrical Engineer",
            "Financial Analyst", "Human Resources", "Operations Manager"
        ]
        
        text_lower = text.lower()
        for career in common_careers:
            if career.lower() in text_lower:
                careers.append(career)
        
        return careers[:5]  # Return top 5 matches

class AIServiceManager:
    """Main manager for all AI services with fallback mechanisms"""
    
    def __init__(self):
        self.huggingface = HuggingFaceClient()
        self.openai = OpenAIClient()
        self.fallback_active = False
    
    def get_text_embeddings(self, text: str) -> List[float]:
        """Get text embeddings with fallback to simple hash-based approach"""
        try:
            result = self.huggingface.get_embeddings(text)
            if isinstance(result, list) and len(result) > 0:
                return result[0] if isinstance(result[0], list) else result
            return self._fallback_embeddings(text)
        except Exception as e:
            logger.warning(f"Embeddings API failed: {e}")
            return self._fallback_embeddings(text)
    
    def _fallback_embeddings(self, text: str) -> List[float]:
        """Simple fallback embedding based on text characteristics"""
        # Create a simple 384-dimensional vector based on text features
        import hashlib
        
        # Use text characteristics to create a pseudo-embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to numbers and normalize
        embedding = []
        for i in range(0, len(text_hash), 2):
            val = int(text_hash[i:i+2], 16) / 255.0  # Normalize to 0-1
            embedding.append(val)
        
        # Pad or truncate to 384 dimensions
        while len(embedding) < 384:
            embedding.extend(embedding[:min(len(embedding), 384 - len(embedding))])
        
        return embedding[:384]
    
    def classify_text(self, text: str, categories: List[str]) -> Dict:
        """Classify text into categories with fallback"""
        try:
            result = self.huggingface.classify_skills(text)
            return result
        except Exception as e:
            logger.warning(f"Classification API failed: {e}")
            return self._fallback_classification(text, categories)
    
    def _fallback_classification(self, text: str, categories: List[str]) -> Dict:
        """Simple keyword-based classification fallback"""
        text_lower = text.lower()
        scores = {}
        
        # Simple keyword matching
        keywords = {
            "TECHNOLOGY": ["python", "java", "programming", "software", "coding", "development"],
            "COMMUNICATION": ["presentation", "speaking", "writing", "communication"],
            "LEADERSHIP": ["leader", "team", "manage", "coordinate", "organize"],
            "ANALYTICAL": ["analysis", "data", "research", "problem", "solve"],
            "CREATIVE": ["design", "creative", "art", "innovation", "creative"],
            "MANAGEMENT": ["project", "management", "planning", "strategy"]
        }
        
        for category in categories:
            score = 0
            if category in keywords:
                for keyword in keywords[category]:
                    if keyword in text_lower:
                        score += 1
                scores[category] = min(score / len(keywords[category]), 1.0)
            else:
                scores[category] = 0.1  # Default low score
        
        # Normalize scores
        total = sum(scores.values()) or 1
        return {cat: score/total for cat, score in scores.items()}
    
    def analyze_student_profile(self, profile_data: Dict) -> Dict:
        """Comprehensive profile analysis using available AI services"""
        profile_text = self._create_profile_text(profile_data)
        
        analysis = {
            "profile_summary": profile_text[:200] + "...",
            "skill_analysis": {},
            "career_recommendations": [],
            "confidence_score": 0.0
        }
        
        try:
            # Try OpenAI first for comprehensive analysis
            if self.openai.client:
                openai_result = self.openai.analyze_profile(profile_text)
                analysis["ai_analysis"] = openai_result.get("analysis", "")
                analysis["career_recommendations"].extend(openai_result.get("recommendations", []))
        except Exception as e:
            logger.info(f"OpenAI analysis not available: {e}")
        
        try:
            # Use Hugging Face for skill classification
            skills_text = " ".join(profile_data.get("technical_skills", []) + 
                                 profile_data.get("soft_skills", []))
            if skills_text:
                skill_classification = self.huggingface.classify_skills(skills_text)
                analysis["skill_analysis"] = skill_classification
        except Exception as e:
            logger.info(f"Skill classification not available: {e}")
        
        # Fallback career recommendations if none found
        if not analysis["career_recommendations"]:
            analysis["career_recommendations"] = self._fallback_career_recommendations(profile_data)
        
        # Calculate confidence score
        analysis["confidence_score"] = self._calculate_confidence_score(analysis)
        
        return analysis
    
    def _create_profile_text(self, profile_data: Dict) -> str:
        """Create a comprehensive text representation of student profile"""
        parts = []
        
        if profile_data.get("academic_records"):
            parts.append(f"Academic: {profile_data['academic_records']}")
        
        if profile_data.get("technical_skills"):
            parts.append(f"Technical Skills: {', '.join(profile_data['technical_skills'])}")
        
        if profile_data.get("soft_skills"):
            parts.append(f"Soft Skills: {', '.join(profile_data['soft_skills'])}")
        
        if profile_data.get("co_curricular"):
            parts.append(f"Activities: {', '.join(profile_data['co_curricular'])}")
        
        return " | ".join(parts)
    
    def _fallback_career_recommendations(self, profile_data: Dict) -> List[Dict]:
        """Generate career recommendations using rule-based approach"""
        recommendations = []
        
        technical_skills = profile_data.get("technical_skills", [])
        academic_info = str(profile_data.get("academic_records", "")).lower()
        
        # Simple rule-based matching
        if any(skill.lower() in ["python", "java", "programming", "software"] 
               for skill in technical_skills):
            recommendations.append({
                "career": "Software Developer",
                "confidence": 0.8,
                "reason": "Strong programming skills"
            })
        
        if any(skill.lower() in ["data", "analytics", "statistics", "machine learning"] 
               for skill in technical_skills):
            recommendations.append({
                "career": "Data Scientist",
                "confidence": 0.7,
                "reason": "Data analysis skills"
            })
        
        if "business" in academic_info or "management" in academic_info:
            recommendations.append({
                "career": "Business Analyst",
                "confidence": 0.6,
                "reason": "Business background"
            })
        
        # Default recommendation if none match
        if not recommendations:
            recommendations.append({
                "career": "Technology Consultant",
                "confidence": 0.5,
                "reason": "General technology aptitude"
            })
        
        return recommendations[:3]  # Return top 3
    
    def _calculate_confidence_score(self, analysis: Dict) -> float:
        """Calculate overall confidence score for the analysis"""
        score = 0.5  # Base score
        
        if analysis.get("ai_analysis"):
            score += 0.2
        
        if analysis.get("skill_analysis"):
            score += 0.2
        
        if len(analysis.get("career_recommendations", [])) > 1:
            score += 0.1
        
        return min(score, 1.0)

# Global instance
ai_service = AIServiceManager()