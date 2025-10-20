"""
Job Matching and Candidate Shortlisting System
Implements AI-powered semantic similarity matching for job-candidate pairing
"""
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import math

from .ai_services import ai_service

logger = logging.getLogger(__name__)

class SemanticMatcher:
    """Handles semantic similarity matching using AI embeddings"""
    
    def __init__(self):
        self.ai_service = ai_service
        self.embedding_cache = {}
    
    def get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for text with caching"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            embedding = self.ai_service.get_text_embeddings(text)
            self.embedding_cache[text] = embedding
            return embedding
        except Exception as e:
            logger.warning(f"Failed to get embedding: {e}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding based on text characteristics"""
        # Create a basic embedding based on text features
        words = text.lower().split()
        
        # Create features based on word characteristics
        features = []
        
        # Length features
        features.append(len(words) / 100.0)  # Normalized word count
        features.append(len(text) / 1000.0)  # Normalized character count
        
        # Keyword presence features (technology focus)
        tech_keywords = [
            "python", "java", "javascript", "react", "angular", "node",
            "sql", "database", "api", "web", "mobile", "cloud", "ai",
            "machine learning", "data", "analytics", "software", "development"
        ]
        
        for keyword in tech_keywords:
            features.append(1.0 if keyword in text.lower() else 0.0)
        
        # Pad to standard embedding size (384)
        while len(features) < 384:
            features.extend(features[:min(len(features), 384 - len(features))])
        
        return features[:384]
    
    def calculate_similarity(self, embedding1: List[float], 
                           embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Ensure embeddings are same length
            min_len = min(len(embedding1), len(embedding2))
            emb1 = embedding1[:min_len]
            emb2 = embedding2[:min_len]
            
            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(emb1, emb2))
            magnitude1 = math.sqrt(sum(a * a for a in emb1))
            magnitude2 = math.sqrt(sum(b * b for b in emb2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.warning(f"Similarity calculation failed: {e}")
            return 0.0

class CandidateRanker:
    """Ranks candidates based on job requirements and multiple criteria"""
    
    def __init__(self):
        self.semantic_matcher = SemanticMatcher()
        self.ranking_weights = {
            "semantic_similarity": 0.35,
            "skill_match": 0.25,
            "experience_match": 0.15,
            "education_match": 0.15,
            "location_preference": 0.05,
            "availability": 0.05
        }
    
    def rank_candidates(self, job_requirements: Dict, 
                       candidates: List[Dict]) -> List[Dict]:
        """Rank candidates for a specific job posting"""
        try:
            job_text = self._create_job_text(job_requirements)
            job_embedding = self.semantic_matcher.get_text_embedding(job_text)
            
            ranked_candidates = []
            
            for candidate in candidates:
                candidate_score = self._calculate_candidate_score(
                    job_requirements, candidate, job_embedding
                )
                
                ranked_candidate = {
                    "candidate_id": candidate.get("id"),
                    "student_profile": candidate,
                    "overall_score": candidate_score["overall_score"],
                    "score_breakdown": candidate_score["breakdown"],
                    "match_reasons": candidate_score["reasons"],
                    "recommendation": self._generate_recommendation(candidate_score),
                    "ranked_at": datetime.now().isoformat()
                }
                
                ranked_candidates.append(ranked_candidate)
            
            # Sort by overall score
            ranked_candidates.sort(key=lambda x: x["overall_score"], reverse=True)
            
            # Add ranking positions
            for i, candidate in enumerate(ranked_candidates):
                candidate["rank"] = i + 1
                candidate["percentile"] = ((len(ranked_candidates) - i) / 
                                        len(ranked_candidates)) * 100
            
            return ranked_candidates
            
        except Exception as e:
            logger.error(f"Error ranking candidates: {e}")
            return self._fallback_ranking(candidates)
    
    def _create_job_text(self, job_requirements: Dict) -> str:
        """Create comprehensive text representation of job requirements"""
        parts = []
        
        if job_requirements.get("title"):
            parts.append(f"Job Title: {job_requirements['title']}")
        
        if job_requirements.get("description"):
            parts.append(f"Description: {job_requirements['description']}")
        
        if job_requirements.get("required_skills"):
            skills = job_requirements["required_skills"]
            if isinstance(skills, list):
                parts.append(f"Required Skills: {', '.join(skills)}")
            else:
                parts.append(f"Required Skills: {skills}")
        
        if job_requirements.get("preferred_qualifications"):
            quals = job_requirements["preferred_qualifications"]
            if isinstance(quals, list):
                parts.append(f"Preferred Qualifications: {', '.join(quals)}")
            else:
                parts.append(f"Preferred Qualifications: {quals}")
        
        if job_requirements.get("experience_level"):
            parts.append(f"Experience Level: {job_requirements['experience_level']}")
        
        return " | ".join(parts)
    
    def _create_candidate_text(self, candidate: Dict) -> str:
        """Create comprehensive text representation of candidate profile"""
        parts = []
        
        if candidate.get("technical_skills"):
            skills = candidate["technical_skills"]
            if isinstance(skills, list):
                parts.append(f"Technical Skills: {', '.join(skills)}")
            else:
                parts.append(f"Technical Skills: {skills}")
        
        if candidate.get("soft_skills"):
            skills = candidate["soft_skills"]
            if isinstance(skills, list):
                parts.append(f"Soft Skills: {', '.join(skills)}")
            else:
                parts.append(f"Soft Skills: {skills}")
        
        if candidate.get("academic_records"):
            academic = candidate["academic_records"]
            if isinstance(academic, dict):
                parts.append(f"Education: {academic.get('major', '')} {academic.get('degree', '')}")
            else:
                parts.append(f"Education: {academic}")
        
        if candidate.get("co_curricular"):
            activities = candidate["co_curricular"]
            if isinstance(activities, list):
                parts.append(f"Activities: {', '.join(activities)}")
            else:
                parts.append(f"Activities: {activities}")
        
        return " | ".join(parts)
    
    def _calculate_candidate_score(self, job_requirements: Dict, 
                                 candidate: Dict, job_embedding: List[float]) -> Dict:
        """Calculate comprehensive score for a candidate"""
        scores = {}
        reasons = []
        
        # 1. Semantic Similarity Score
        candidate_text = self._create_candidate_text(candidate)
        candidate_embedding = self.semantic_matcher.get_text_embedding(candidate_text)
        semantic_score = self.semantic_matcher.calculate_similarity(
            job_embedding, candidate_embedding
        )
        scores["semantic_similarity"] = semantic_score
        
        if semantic_score > 0.7:
            reasons.append(f"Strong profile match ({semantic_score:.2f})")
        
        # 2. Skill Match Score
        skill_score = self._calculate_skill_match(job_requirements, candidate)
        scores["skill_match"] = skill_score
        
        if skill_score > 0.6:
            reasons.append(f"Good skill alignment ({skill_score:.2f})")
        
        # 3. Experience Match Score
        experience_score = self._calculate_experience_match(job_requirements, candidate)
        scores["experience_match"] = experience_score
        
        # 4. Education Match Score
        education_score = self._calculate_education_match(job_requirements, candidate)
        scores["education_match"] = education_score
        
        # 5. Location Preference Score (placeholder)
        location_score = 0.8  # Default good score
        scores["location_preference"] = location_score
        
        # 6. Availability Score (placeholder)
        availability_score = 0.9  # Default good score
        scores["availability"] = availability_score
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[criterion] * self.ranking_weights[criterion]
            for criterion in self.ranking_weights
        )
        
        return {
            "overall_score": overall_score,
            "breakdown": scores,
            "reasons": reasons
        }
    
    def _calculate_skill_match(self, job_requirements: Dict, candidate: Dict) -> float:
        """Calculate skill matching score"""
        required_skills = job_requirements.get("required_skills", [])
        if isinstance(required_skills, str):
            required_skills = [s.strip() for s in required_skills.split(",")]
        
        candidate_skills = []
        candidate_skills.extend(candidate.get("technical_skills", []))
        candidate_skills.extend(candidate.get("soft_skills", []))
        
        if not required_skills or not candidate_skills:
            return 0.3  # Default score when no skills data
        
        # Normalize skills to lowercase for comparison
        required_lower = [skill.lower().strip() for skill in required_skills]
        candidate_lower = [skill.lower().strip() for skill in candidate_skills]
        
        # Calculate matches
        matches = 0
        for req_skill in required_lower:
            for cand_skill in candidate_lower:
                if (req_skill in cand_skill or cand_skill in req_skill or
                    self._skills_are_similar(req_skill, cand_skill)):
                    matches += 1
                    break
        
        # Calculate score
        skill_score = matches / len(required_skills)
        return min(skill_score, 1.0)
    
    def _skills_are_similar(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are similar"""
        # Simple similarity check for common skill variations
        skill_synonyms = {
            "javascript": ["js", "node.js", "nodejs"],
            "python": ["py"],
            "machine learning": ["ml", "ai", "artificial intelligence"],
            "database": ["sql", "mysql", "postgresql"],
            "web development": ["frontend", "backend", "full stack"]
        }
        
        for main_skill, synonyms in skill_synonyms.items():
            if ((main_skill in skill1 and any(syn in skill2 for syn in synonyms)) or
                (main_skill in skill2 and any(syn in skill1 for syn in synonyms))):
                return True
        
        return False
    
    def _calculate_experience_match(self, job_requirements: Dict, candidate: Dict) -> float:
        """Calculate experience level matching score"""
        required_exp = job_requirements.get("experience_level", "").lower()
        
        # Extract experience from candidate profile
        candidate_exp = self._extract_candidate_experience(candidate)
        
        # Simple experience matching logic
        if "entry" in required_exp or "junior" in required_exp or "0" in required_exp:
            return 0.9 if candidate_exp <= 2 else 0.6
        elif "mid" in required_exp or "2-5" in required_exp:
            return 0.9 if 1 <= candidate_exp <= 6 else 0.7
        elif "senior" in required_exp or "5+" in required_exp:
            return 0.9 if candidate_exp >= 3 else 0.5
        else:
            return 0.7  # Default score
    
    def _extract_candidate_experience(self, candidate: Dict) -> int:
        """Extract years of experience from candidate profile"""
        # This is a simplified extraction - in real implementation,
        # you'd parse work experience, internships, projects, etc.
        
        co_curricular = candidate.get("co_curricular", [])
        technical_skills = candidate.get("technical_skills", [])
        
        # Estimate experience based on profile completeness and activities
        experience_indicators = len(co_curricular) + len(technical_skills)
        
        if experience_indicators > 10:
            return 3  # Experienced
        elif experience_indicators > 5:
            return 1  # Some experience
        else:
            return 0  # Entry level
    
    def _calculate_education_match(self, job_requirements: Dict, candidate: Dict) -> float:
        """Calculate education matching score"""
        # Extract education requirements from job (if any)
        job_description = job_requirements.get("description", "").lower()
        
        candidate_academic = candidate.get("academic_records", {})
        if isinstance(candidate_academic, dict):
            candidate_major = candidate_academic.get("major", "").lower()
            candidate_degree = candidate_academic.get("degree", "").lower()
        else:
            candidate_major = str(candidate_academic).lower()
            candidate_degree = ""
        
        # Simple education matching
        education_keywords = [
            "computer science", "engineering", "technology", "business",
            "mathematics", "statistics", "data science"
        ]
        
        job_edu_match = any(keyword in job_description for keyword in education_keywords)
        candidate_edu_match = any(keyword in candidate_major or keyword in candidate_degree 
                                for keyword in education_keywords)
        
        if job_edu_match and candidate_edu_match:
            return 0.9
        elif candidate_edu_match:
            return 0.7
        else:
            return 0.5  # Default score
    
    def _generate_recommendation(self, candidate_score: Dict) -> str:
        """Generate hiring recommendation based on candidate score"""
        overall_score = candidate_score["overall_score"]
        
        if overall_score >= 0.8:
            return "Highly Recommended - Excellent match for the position"
        elif overall_score >= 0.6:
            return "Recommended - Good fit with minor gaps"
        elif overall_score >= 0.4:
            return "Consider - Potential fit with some development needed"
        else:
            return "Not Recommended - Significant gaps in requirements"
    
    def _fallback_ranking(self, candidates: List[Dict]) -> List[Dict]:
        """Provide fallback ranking when main system fails"""
        fallback_candidates = []
        
        for i, candidate in enumerate(candidates):
            fallback_candidates.append({
                "candidate_id": candidate.get("id"),
                "student_profile": candidate,
                "overall_score": 0.5,  # Default score
                "score_breakdown": {"fallback": 0.5},
                "match_reasons": ["System temporarily unavailable"],
                "recommendation": "Manual review recommended",
                "rank": i + 1,
                "percentile": ((len(candidates) - i) / len(candidates)) * 100,
                "ranked_at": datetime.now().isoformat()
            })
        
        return fallback_candidates

class FeedbackLearningSystem:
    """Implements feedback loop for improving match accuracy"""
    
    def __init__(self):
        self.feedback_data = []
        self.learning_enabled = True
    
    def record_feedback(self, job_id: str, candidate_id: str, 
                       employer_rating: float, hire_decision: bool,
                       feedback_notes: str = "") -> None:
        """Record employer feedback on candidate matches"""
        feedback_entry = {
            "job_id": job_id,
            "candidate_id": candidate_id,
            "employer_rating": employer_rating,  # 1-5 scale
            "hire_decision": hire_decision,
            "feedback_notes": feedback_notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.feedback_data.append(feedback_entry)
        
        # Trigger learning update if we have enough data
        if len(self.feedback_data) >= 10:
            self._update_matching_weights()
    
    def _update_matching_weights(self) -> None:
        """Update matching algorithm weights based on feedback"""
        if not self.learning_enabled:
            return
        
        try:
            # Analyze feedback patterns
            positive_feedback = [f for f in self.feedback_data 
                               if f["employer_rating"] >= 4 or f["hire_decision"]]
            
            if len(positive_feedback) >= 5:
                # Simple learning: boost weights for criteria that correlate with positive feedback
                logger.info(f"Learning from {len(positive_feedback)} positive feedback entries")
                
                # In a real implementation, you'd use more sophisticated ML here
                # For now, we'll just log that learning occurred
                
        except Exception as e:
            logger.error(f"Error in feedback learning: {e}")
    
    def get_feedback_analytics(self) -> Dict:
        """Get analytics on feedback and matching performance"""
        if not self.feedback_data:
            return {"message": "No feedback data available"}
        
        total_feedback = len(self.feedback_data)
        positive_feedback = len([f for f in self.feedback_data 
                               if f["employer_rating"] >= 4])
        hire_rate = len([f for f in self.feedback_data 
                        if f["hire_decision"]]) / total_feedback
        
        avg_rating = sum(f["employer_rating"] for f in self.feedback_data) / total_feedback
        
        return {
            "total_feedback_entries": total_feedback,
            "positive_feedback_rate": positive_feedback / total_feedback,
            "hire_rate": hire_rate,
            "average_employer_rating": avg_rating,
            "last_updated": datetime.now().isoformat()
        }

class JobMatchingService:
    """Main service for job matching and candidate shortlisting"""
    
    def __init__(self):
        self.candidate_ranker = CandidateRanker()
        self.feedback_system = FeedbackLearningSystem()
    
    def find_matching_candidates(self, job_posting: Dict, 
                               candidate_pool: List[Dict],
                               max_candidates: int = 10) -> Dict:
        """Find and rank matching candidates for a job posting"""
        try:
            # Rank all candidates
            ranked_candidates = self.candidate_ranker.rank_candidates(
                job_posting, candidate_pool
            )
            
            # Filter to top candidates
            top_candidates = ranked_candidates[:max_candidates]
            
            # Generate matching report
            matching_report = {
                "job_id": job_posting.get("id"),
                "job_title": job_posting.get("title"),
                "total_candidates_evaluated": len(candidate_pool),
                "shortlisted_candidates": len(top_candidates),
                "top_candidates": top_candidates,
                "matching_summary": self._generate_matching_summary(ranked_candidates),
                "generated_at": datetime.now().isoformat()
            }
            
            return matching_report
            
        except Exception as e:
            logger.error(f"Error in job matching: {e}")
            return {
                "error": "Job matching temporarily unavailable",
                "job_id": job_posting.get("id"),
                "generated_at": datetime.now().isoformat()
            }
    
    def _generate_matching_summary(self, ranked_candidates: List[Dict]) -> Dict:
        """Generate summary statistics for the matching process"""
        if not ranked_candidates:
            return {"message": "No candidates evaluated"}
        
        scores = [c["overall_score"] for c in ranked_candidates]
        
        return {
            "average_match_score": sum(scores) / len(scores),
            "highest_match_score": max(scores),
            "candidates_above_threshold": len([s for s in scores if s >= 0.6]),
            "score_distribution": {
                "excellent": len([s for s in scores if s >= 0.8]),
                "good": len([s for s in scores if 0.6 <= s < 0.8]),
                "fair": len([s for s in scores if 0.4 <= s < 0.6]),
                "poor": len([s for s in scores if s < 0.4])
            }
        }
    
    def record_employer_feedback(self, job_id: str, candidate_id: str,
                               rating: float, hired: bool, notes: str = "") -> None:
        """Record employer feedback for learning"""
        self.feedback_system.record_feedback(
            job_id, candidate_id, rating, hired, notes
        )
    
    def get_matching_analytics(self) -> Dict:
        """Get analytics on matching performance"""
        return self.feedback_system.get_feedback_analytics()

# Global instance
job_matching_service = JobMatchingService()