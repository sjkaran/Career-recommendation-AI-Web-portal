"""
Career Recommendation Engine
Implements AI-powered career recommendations based on student profiles
"""
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import math

from .ai_services import ai_service

logger = logging.getLogger(__name__)

class SkillCareerMapping:
    """Manages skill-to-career mapping database and logic"""
    
    def __init__(self):
        self.skill_career_map = self._initialize_skill_career_mapping()
        self.career_requirements = self._initialize_career_requirements()
    
    def _initialize_skill_career_mapping(self) -> Dict:
        """Initialize comprehensive skill-to-career mapping"""
        return {
            # Technology Careers
            "Software Developer": {
                "required_skills": ["programming", "python", "java", "javascript", "software development"],
                "preferred_skills": ["algorithms", "data structures", "git", "testing", "debugging"],
                "soft_skills": ["problem solving", "analytical thinking", "attention to detail"],
                "academic_fields": ["computer science", "information technology", "software engineering"],
                "weight": 1.0
            },
            "Data Scientist": {
                "required_skills": ["python", "statistics", "machine learning", "data analysis"],
                "preferred_skills": ["sql", "pandas", "numpy", "visualization", "r programming"],
                "soft_skills": ["analytical thinking", "research", "communication"],
                "academic_fields": ["computer science", "statistics", "mathematics", "data science"],
                "weight": 0.9
            },
            "Web Developer": {
                "required_skills": ["html", "css", "javascript", "web development"],
                "preferred_skills": ["react", "angular", "node.js", "responsive design", "api"],
                "soft_skills": ["creativity", "attention to detail", "user focus"],
                "academic_fields": ["computer science", "web design", "information technology"],
                "weight": 0.9
            },
            "Mobile App Developer": {
                "required_skills": ["mobile development", "android", "ios", "java", "swift"],
                "preferred_skills": ["react native", "flutter", "ui/ux", "app store"],
                "soft_skills": ["creativity", "user experience", "problem solving"],
                "academic_fields": ["computer science", "mobile computing", "software engineering"],
                "weight": 0.8
            },
            
            # Engineering Careers
            "Mechanical Engineer": {
                "required_skills": ["mechanical engineering", "cad", "design", "manufacturing"],
                "preferred_skills": ["autocad", "solidworks", "thermodynamics", "materials"],
                "soft_skills": ["problem solving", "analytical thinking", "project management"],
                "academic_fields": ["mechanical engineering", "engineering"],
                "weight": 0.9
            },
            "Civil Engineer": {
                "required_skills": ["civil engineering", "construction", "structural design"],
                "preferred_skills": ["autocad", "project management", "surveying", "concrete"],
                "soft_skills": ["leadership", "communication", "planning"],
                "academic_fields": ["civil engineering", "construction engineering"],
                "weight": 0.9
            },
            "Electrical Engineer": {
                "required_skills": ["electrical engineering", "circuits", "electronics"],
                "preferred_skills": ["power systems", "control systems", "matlab", "pcb design"],
                "soft_skills": ["analytical thinking", "problem solving", "attention to detail"],
                "academic_fields": ["electrical engineering", "electronics engineering"],
                "weight": 0.9
            },
            
            # Business Careers
            "Business Analyst": {
                "required_skills": ["business analysis", "requirements gathering", "process improvement"],
                "preferred_skills": ["sql", "excel", "project management", "stakeholder management"],
                "soft_skills": ["communication", "analytical thinking", "problem solving"],
                "academic_fields": ["business administration", "management", "economics"],
                "weight": 0.8
            },
            "Product Manager": {
                "required_skills": ["product management", "strategy", "market research"],
                "preferred_skills": ["agile", "user experience", "analytics", "roadmap planning"],
                "soft_skills": ["leadership", "communication", "strategic thinking"],
                "academic_fields": ["business administration", "marketing", "engineering"],
                "weight": 0.7
            },
            "Marketing Specialist": {
                "required_skills": ["marketing", "digital marketing", "content creation"],
                "preferred_skills": ["social media", "seo", "analytics", "campaign management"],
                "soft_skills": ["creativity", "communication", "persuasion"],
                "academic_fields": ["marketing", "business administration", "communications"],
                "weight": 0.8
            },
            
            # Finance Careers
            "Financial Analyst": {
                "required_skills": ["financial analysis", "excel", "accounting", "finance"],
                "preferred_skills": ["financial modeling", "valuation", "risk analysis", "bloomberg"],
                "soft_skills": ["analytical thinking", "attention to detail", "communication"],
                "academic_fields": ["finance", "accounting", "economics", "business"],
                "weight": 0.8
            },
            
            # Other Careers
            "Operations Manager": {
                "required_skills": ["operations management", "process optimization", "logistics"],
                "preferred_skills": ["supply chain", "lean manufacturing", "project management"],
                "soft_skills": ["leadership", "problem solving", "communication"],
                "academic_fields": ["operations management", "industrial engineering", "business"],
                "weight": 0.7
            },
            "Human Resources Specialist": {
                "required_skills": ["human resources", "recruitment", "employee relations"],
                "preferred_skills": ["hr systems", "training", "performance management"],
                "soft_skills": ["communication", "empathy", "conflict resolution"],
                "academic_fields": ["human resources", "psychology", "business administration"],
                "weight": 0.7
            }
        }
    
    def _initialize_career_requirements(self) -> Dict:
        """Initialize detailed career requirements and growth paths"""
        return {
            career: {
                "entry_level": {
                    "experience": "0-2 years",
                    "key_skills": data["required_skills"][:3],
                    "salary_range": "Entry level"
                },
                "mid_level": {
                    "experience": "2-5 years", 
                    "key_skills": data["required_skills"] + data["preferred_skills"][:2],
                    "salary_range": "Mid level"
                },
                "senior_level": {
                    "experience": "5+ years",
                    "key_skills": data["required_skills"] + data["preferred_skills"],
                    "salary_range": "Senior level"
                },
                "growth_path": self._generate_growth_path(career),
                "industry_demand": self._get_industry_demand(career)
            }
            for career, data in self.skill_career_map.items()
        }
    
    def _generate_growth_path(self, career: str) -> List[str]:
        """Generate career growth path"""
        growth_paths = {
            "Software Developer": ["Junior Developer", "Software Developer", "Senior Developer", "Tech Lead", "Engineering Manager"],
            "Data Scientist": ["Data Analyst", "Data Scientist", "Senior Data Scientist", "Lead Data Scientist", "Head of Data"],
            "Business Analyst": ["Junior Analyst", "Business Analyst", "Senior Analyst", "Lead Analyst", "Product Manager"],
        }
        return growth_paths.get(career, ["Entry Level", "Mid Level", "Senior Level", "Lead", "Manager"])
    
    def _get_industry_demand(self, career: str) -> str:
        """Get industry demand level for career"""
        high_demand = ["Software Developer", "Data Scientist", "Web Developer", "Mobile App Developer"]
        medium_demand = ["Business Analyst", "Product Manager", "Financial Analyst"]
        
        if career in high_demand:
            return "High"
        elif career in medium_demand:
            return "Medium"
        else:
            return "Moderate"
    
    def get_career_match_score(self, career: str, student_skills: List[str], 
                              academic_field: str = "") -> float:
        """Calculate match score between student and career"""
        if career not in self.skill_career_map:
            return 0.0
        
        career_data = self.skill_career_map[career]
        score = 0.0
        
        # Normalize inputs
        student_skills_lower = [skill.lower().strip() for skill in student_skills]
        academic_field_lower = academic_field.lower().strip()
        
        # Required skills matching (40% weight)
        required_skills = [skill.lower() for skill in career_data["required_skills"]]
        required_matches = sum(1 for skill in required_skills 
                             if any(req_skill in student_skill for student_skill in student_skills_lower 
                                   for req_skill in [skill]))
        required_score = (required_matches / len(required_skills)) * 0.4
        
        # Preferred skills matching (30% weight)
        preferred_skills = [skill.lower() for skill in career_data["preferred_skills"]]
        preferred_matches = sum(1 for skill in preferred_skills 
                              if any(pref_skill in student_skill for student_skill in student_skills_lower 
                                    for pref_skill in [skill]))
        preferred_score = (preferred_matches / len(preferred_skills)) * 0.3 if preferred_skills else 0
        
        # Academic field matching (20% weight)
        academic_fields = [field.lower() for field in career_data["academic_fields"]]
        academic_score = 0.2 if any(field in academic_field_lower for field in academic_fields) else 0
        
        # Soft skills bonus (10% weight)
        soft_skills = [skill.lower() for skill in career_data["soft_skills"]]
        soft_matches = sum(1 for skill in soft_skills 
                          if any(soft_skill in student_skill for student_skill in student_skills_lower 
                                for soft_skill in [skill]))
        soft_score = (soft_matches / len(soft_skills)) * 0.1 if soft_skills else 0
        
        total_score = required_score + preferred_score + academic_score + soft_score
        
        # Apply career weight
        weighted_score = total_score * career_data["weight"]
        
        return min(weighted_score, 1.0)

class CareerRecommendationEngine:
    """Main career recommendation engine using AI and rule-based approaches"""
    
    def __init__(self):
        self.skill_mapping = SkillCareerMapping()
        self.ai_service = ai_service
        self.recommendation_cache = {}
    
    def generate_recommendations(self, student_profile: Dict) -> Dict:
        """Generate comprehensive career recommendations for a student"""
        try:
            # Create cache key
            cache_key = self._create_cache_key(student_profile)
            if cache_key in self.recommendation_cache:
                logger.info("Returning cached recommendations")
                return self.recommendation_cache[cache_key]
            
            # Extract profile information
            technical_skills = student_profile.get("technical_skills", [])
            soft_skills = student_profile.get("soft_skills", [])
            academic_info = student_profile.get("academic_records", {})
            co_curricular = student_profile.get("co_curricular", [])
            career_interests = student_profile.get("career_interests", [])
            
            # Combine all skills
            all_skills = technical_skills + soft_skills + co_curricular
            academic_field = str(academic_info.get("major", "")) if isinstance(academic_info, dict) else str(academic_info)
            
            # Get AI-powered analysis
            ai_analysis = self._get_ai_analysis(student_profile)
            
            # Get rule-based recommendations
            rule_based_recommendations = self._get_rule_based_recommendations(
                all_skills, academic_field, career_interests
            )
            
            # Combine and rank recommendations
            final_recommendations = self._combine_recommendations(
                ai_analysis.get("career_recommendations", []),
                rule_based_recommendations
            )
            
            # Generate detailed recommendation report
            recommendation_report = {
                "recommendations": final_recommendations[:5],  # Top 5
                "ai_analysis": ai_analysis,
                "skill_analysis": self._analyze_skills(all_skills),
                "career_roadmaps": self._generate_career_roadmaps(final_recommendations[:3]),
                "skill_gaps": self._identify_skill_gaps(final_recommendations[:3], all_skills),
                "confidence_score": self._calculate_overall_confidence(ai_analysis, final_recommendations),
                "generated_at": datetime.now().isoformat()
            }
            
            # Cache the result
            self.recommendation_cache[cache_key] = recommendation_report
            
            return recommendation_report
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._get_fallback_recommendations(student_profile)
    
    def _create_cache_key(self, student_profile: Dict) -> str:
        """Create a cache key for the student profile"""
        import hashlib
        profile_str = json.dumps(student_profile, sort_keys=True)
        return hashlib.md5(profile_str.encode()).hexdigest()
    
    def _get_ai_analysis(self, student_profile: Dict) -> Dict:
        """Get AI-powered analysis of student profile"""
        try:
            return self.ai_service.analyze_student_profile(student_profile)
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return {
                "career_recommendations": [],
                "confidence_score": 0.3,
                "analysis": "AI analysis unavailable"
            }
    
    def _get_rule_based_recommendations(self, skills: List[str], 
                                      academic_field: str, 
                                      interests: List[str]) -> List[Dict]:
        """Get recommendations using rule-based matching"""
        recommendations = []
        
        for career in self.skill_mapping.skill_career_map.keys():
            match_score = self.skill_mapping.get_career_match_score(
                career, skills, academic_field
            )
            
            # Boost score if career matches interests
            if interests:
                interest_boost = any(interest.lower() in career.lower() 
                                   for interest in interests)
                if interest_boost:
                    match_score = min(match_score * 1.2, 1.0)
            
            if match_score > 0.1:  # Only include careers with some match
                recommendations.append({
                    "career": career,
                    "confidence": match_score,
                    "source": "rule_based",
                    "reason": self._generate_recommendation_reason(career, skills, academic_field)
                })
        
        return sorted(recommendations, key=lambda x: x["confidence"], reverse=True)
    
    def _generate_recommendation_reason(self, career: str, skills: List[str], 
                                     academic_field: str) -> str:
        """Generate explanation for why this career was recommended"""
        career_data = self.skill_mapping.skill_career_map.get(career, {})
        required_skills = career_data.get("required_skills", [])
        
        matching_skills = []
        for skill in skills:
            for req_skill in required_skills:
                if req_skill.lower() in skill.lower():
                    matching_skills.append(skill)
                    break
        
        reason_parts = []
        if matching_skills:
            reason_parts.append(f"Matching skills: {', '.join(matching_skills[:3])}")
        
        if academic_field:
            academic_fields = career_data.get("academic_fields", [])
            if any(field.lower() in academic_field.lower() for field in academic_fields):
                reason_parts.append(f"Academic background in {academic_field}")
        
        return "; ".join(reason_parts) if reason_parts else "General aptitude match"
    
    def _combine_recommendations(self, ai_recommendations: List, 
                               rule_recommendations: List[Dict]) -> List[Dict]:
        """Combine AI and rule-based recommendations"""
        combined = {}
        
        # Add rule-based recommendations
        for rec in rule_recommendations:
            career = rec["career"]
            combined[career] = rec
        
        # Merge AI recommendations
        for ai_rec in ai_recommendations:
            if isinstance(ai_rec, dict):
                career = ai_rec.get("career")
                confidence = ai_rec.get("confidence", 0.5)
            elif isinstance(ai_rec, str):
                career = ai_rec
                confidence = 0.6
            else:
                continue
            
            if career in combined:
                # Boost confidence if both AI and rules agree
                combined[career]["confidence"] = min(
                    (combined[career]["confidence"] + confidence) / 2 * 1.3, 1.0
                )
                combined[career]["source"] = "ai_and_rules"
            else:
                combined[career] = {
                    "career": career,
                    "confidence": confidence,
                    "source": "ai_only",
                    "reason": "AI-powered analysis"
                }
        
        return sorted(combined.values(), key=lambda x: x["confidence"], reverse=True)
    
    def _analyze_skills(self, skills: List[str]) -> Dict:
        """Analyze and categorize student skills"""
        skill_categories = {
            "technical": [],
            "soft": [],
            "domain": [],
            "tools": []
        }
        
        technical_keywords = ["programming", "python", "java", "javascript", "sql", "html", "css"]
        soft_keywords = ["communication", "leadership", "teamwork", "problem solving"]
        tool_keywords = ["excel", "powerpoint", "photoshop", "autocad", "git"]
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized = False
            
            if any(keyword in skill_lower for keyword in technical_keywords):
                skill_categories["technical"].append(skill)
                categorized = True
            
            if any(keyword in skill_lower for keyword in soft_keywords):
                skill_categories["soft"].append(skill)
                categorized = True
            
            if any(keyword in skill_lower for keyword in tool_keywords):
                skill_categories["tools"].append(skill)
                categorized = True
            
            if not categorized:
                skill_categories["domain"].append(skill)
        
        return {
            "categories": skill_categories,
            "total_skills": len(skills),
            "technical_ratio": len(skill_categories["technical"]) / max(len(skills), 1),
            "soft_ratio": len(skill_categories["soft"]) / max(len(skills), 1)
        }
    
    def _generate_career_roadmaps(self, recommendations: List[Dict]) -> Dict:
        """Generate career roadmaps for top recommendations"""
        roadmaps = {}
        
        for rec in recommendations:
            career = rec["career"]
            if career in self.skill_mapping.career_requirements:
                roadmaps[career] = self.skill_mapping.career_requirements[career]
        
        return roadmaps
    
    def _identify_skill_gaps(self, recommendations: List[Dict], 
                           current_skills: List[str]) -> Dict:
        """Identify skill gaps for recommended careers"""
        gaps = {}
        current_skills_lower = [skill.lower() for skill in current_skills]
        
        for rec in recommendations:
            career = rec["career"]
            if career in self.skill_mapping.skill_career_map:
                career_data = self.skill_mapping.skill_career_map[career]
                required_skills = career_data["required_skills"]
                
                missing_skills = []
                for req_skill in required_skills:
                    if not any(req_skill.lower() in current_skill 
                             for current_skill in current_skills_lower):
                        missing_skills.append(req_skill)
                
                if missing_skills:
                    gaps[career] = {
                        "missing_skills": missing_skills,
                        "priority": "high" if len(missing_skills) > 3 else "medium",
                        "learning_resources": self._suggest_learning_resources(missing_skills)
                    }
        
        return gaps
    
    def _suggest_learning_resources(self, skills: List[str]) -> List[Dict]:
        """Suggest learning resources for missing skills"""
        resources = []
        
        resource_map = {
            "python": {"platform": "Codecademy", "type": "Course", "duration": "4-6 weeks"},
            "java": {"platform": "Oracle Java Tutorials", "type": "Documentation", "duration": "6-8 weeks"},
            "javascript": {"platform": "freeCodeCamp", "type": "Interactive", "duration": "3-4 weeks"},
            "sql": {"platform": "W3Schools", "type": "Tutorial", "duration": "2-3 weeks"},
            "machine learning": {"platform": "Coursera", "type": "Course", "duration": "8-12 weeks"}
        }
        
        for skill in skills[:3]:  # Top 3 missing skills
            skill_lower = skill.lower()
            if skill_lower in resource_map:
                resource = resource_map[skill_lower].copy()
                resource["skill"] = skill
                resources.append(resource)
            else:
                resources.append({
                    "skill": skill,
                    "platform": "YouTube/Online Tutorials",
                    "type": "Video",
                    "duration": "2-4 weeks"
                })
        
        return resources
    
    def _calculate_overall_confidence(self, ai_analysis: Dict, 
                                    recommendations: List[Dict]) -> float:
        """Calculate overall confidence in recommendations"""
        base_confidence = 0.5
        
        # Boost if AI analysis is available
        if ai_analysis.get("confidence_score", 0) > 0.5:
            base_confidence += 0.2
        
        # Boost if we have multiple high-confidence recommendations
        high_conf_recs = [r for r in recommendations if r.get("confidence", 0) > 0.7]
        if len(high_conf_recs) >= 2:
            base_confidence += 0.2
        
        # Boost if AI and rules agree on top recommendation
        if (recommendations and 
            recommendations[0].get("source") == "ai_and_rules"):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _get_fallback_recommendations(self, student_profile: Dict) -> Dict:
        """Provide fallback recommendations when main system fails"""
        return {
            "recommendations": [
                {
                    "career": "Technology Consultant",
                    "confidence": 0.5,
                    "source": "fallback",
                    "reason": "General technology aptitude"
                },
                {
                    "career": "Business Analyst", 
                    "confidence": 0.4,
                    "source": "fallback",
                    "reason": "Analytical skills"
                }
            ],
            "ai_analysis": {"analysis": "System temporarily unavailable"},
            "skill_analysis": {"categories": {"technical": [], "soft": []}},
            "career_roadmaps": {},
            "skill_gaps": {},
            "confidence_score": 0.3,
            "generated_at": datetime.now().isoformat()
        }

# Global instance
recommendation_engine = CareerRecommendationEngine()