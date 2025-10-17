"""
Module: resume_parser.py
Description: AI-powered resume parsing using FREE APIs (Gemini + Hugging Face + spaCy)
Author: AI Assistant for BPUT Career Platform
Date: 2025-01-20
Dependencies: google-generativeai, huggingface_hub, spacy, PyPDF2, docx2txt
"""

import os
import re
import json
import PyPDF2
import docx2txt
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from huggingface_hub import InferenceClient
import spacy
from datetime import datetime

# Load spaCy model (download with: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

# Comprehensive skill database for Indian engineering students
TECHNICAL_SKILLS = {
    'programming_languages': [
        'python', 'java', 'javascript', 'c++', 'c', 'c#', 'php', 'ruby', 'go', 'rust', 
        'kotlin', 'swift', 'typescript', 'r', 'matlab', 'scala', 'perl'
    ],
    'web_frameworks': [
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'node.js', 
        'laravel', 'ruby on rails', 'asp.net', 'jquery', 'bootstrap', 'tailwind'
    ],
    'mobile_frameworks': [
        'react native', 'flutter', 'android', 'ios', 'xamarin', 'ionic'
    ],
    'databases': [
        'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server', 'sqlite',
        'cassandra', 'dynamodb', 'elasticsearch', 'firebase'
    ],
    'cloud_platforms': [
        'aws', 'azure', 'gcp', 'heroku', 'digital ocean', 'ibm cloud', 'oracle cloud'
    ],
    'devops_tools': [
        'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'jira', 
        'ansible', 'terraform', 'prometheus', 'grafana'
    ],
    'data_science': [
        'machine learning', 'deep learning', 'data science', 'artificial intelligence',
        'natural language processing', 'computer vision', 'tensorflow', 'pytorch',
        'scikit-learn', 'keras', 'pandas', 'numpy', 'matplotlib', 'seaborn'
    ],
    'testing_tools': [
        'selenium', 'jest', 'mocha', 'junit', 'cypress', 'postman', 'soapui'
    ]
}

SOFT_SKILLS = [
    'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
    'time management', 'adaptability', 'creativity', 'work ethic', 'attention to detail',
    'collaboration', 'presentation', 'negotiation', 'conflict resolution', 'decision making'
]

# Indian education patterns
EDUCATION_PATTERNS = {
    'degrees': [
        r'b\.?tech\.?', r'b\.?e\.?', r'b\.?sc\.?', r'm\.?tech\.?', r'm\.?e\.?', 
        r'm\.?sc\.?', r'b\.?ca\.?', r'm\.?ca\.?', r'b\.?ba\.?', r'm\.?ba\.?',
        r'diploma', r'ph\.?d\.?'
    ],
    'institutions': [
        r'bput', r'biju patnaik university', r'college', r'university', r'institute',
        r'engineering', r'technology', r'school'
    ]
}

class ResumeParser:
    """AI-powered resume parser using free APIs with fallbacks"""
    
    def __init__(self):
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.huggingface_token = os.environ.get('HUGGINGFACE_API_KEY')
        
        # Configure Gemini if available
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"Gemini configuration failed: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
            
        # Configure Hugging Face if available
        if self.huggingface_token:
            try:
                self.hf_client = InferenceClient(token=self.huggingface_token)
            except Exception as e:
                print(f"Hugging Face configuration failed: {e}")
                self.hf_client = None
        else:
            self.hf_client = None
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Parse resume using FREE AI APIs with fallbacks
        
        Args:
            file_path (str): Path to resume file (PDF/DOCX/TXT)
        
        Returns:
            dict: Extracted resume data with skills, education, experience
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Resume file not found: {file_path}")
            
            # Extract text from file
            text = self._extract_text_from_file(file_path)
            if not text or len(text.strip()) < 50:
                raise ValueError("Resume text is too short or empty")
            
            # Try Google Gemini first (most accurate)
            if self.gemini_model:
                try:
                    result = self._parse_with_gemini(text)
                    if result and result.get('skills', {}).get('technical'):
                        print("Successfully parsed with Google Gemini")
                        return result
                except Exception as e:
                    print(f"Gemini parsing failed: {e}")
            
            # Fallback to Hugging Face
            if self.hf_client:
                try:
                    result = self._parse_with_huggingface(text)
                    if result and result.get('skills', {}).get('technical'):
                        print("Successfully parsed with Hugging Face")
                        return result
                except Exception as e:
                    print(f"Hugging Face parsing failed: {e}")
            
            # Final fallback to spaCy (offline, always works)
            result = self._parse_with_spacy(text)
            print("Used spaCy fallback parsing")
            return result
            
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return self._get_empty_result()
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF, DOCX, or TXT files"""
        file_ext = file_path.split('.')[-1].lower()
        
        if file_ext == 'pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_ext == 'docx':
            return self._extract_text_from_docx(file_path)
        elif file_ext == 'txt':
            return self._extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {e}")
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Failed to extract text from TXT: {e}")
    
    def _parse_with_gemini(self, text: str) -> Dict[str, Any]:
        """Parse resume using Google Gemini API"""
        try:
            prompt = f"""
            Extract the following information from this resume text in JSON format:
            
            RESUME TEXT:
            {text[:3000]}  # Limit text to avoid token limits
            
            Required JSON structure:
            {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "+91-XXXXXXXXXX",
                "education": [
                    {{
                        "degree": "Degree Name",
                        "field": "Field of Study",
                        "institution": "Institution Name",
                        "year": "Graduation Year",
                        "cgpa": "CGPA/Percentage"
                    }}
                ],
                "skills": {{
                    "technical": ["skill1", "skill2"],
                    "soft": ["skill1", "skill2"]
                }},
                "experience": [
                    {{
                        "company": "Company Name",
                        "role": "Job Role",
                        "duration": "Duration",
                        "description": "Job Description"
                    }}
                ],
                "projects": [
                    {{
                        "name": "Project Name",
                        "technologies": ["tech1", "tech2"],
                        "description": "Project Description"
                    }}
                ],
                "certifications": ["cert1", "cert2"]
            }}
            
            Important:
            - Extract Indian phone numbers in +91-XXXXXXXXXX format
            - For education, focus on B.Tech, M.Tech, B.E., M.E. degrees
            - Identify technical skills relevant to engineering students
            - Return only valid JSON, no additional text
            """
            
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response (remove markdown code blocks if present)
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'\s*```', '', response_text)
            
            result = json.loads(response_text)
            
            # Add confidence scores
            result['confidence_scores'] = {
                'name': 0.95,
                'email': 1.0 if result.get('email') else 0.0,
                'skills': 0.90,
                'education': 0.85,
                'experience': 0.80
            }
            
            return result
            
        except Exception as e:
            print(f"Gemini parsing error: {e}")
            raise
    
    def _parse_with_huggingface(self, text: str) -> Dict[str, Any]:
        """Parse resume using Hugging Face Inference API"""
        try:
            # For Hugging Face, we'll use a simpler approach since we can't easily get structured JSON
            # We'll extract key information using multiple API calls
            
            result = self._get_empty_result()
            
            # Extract name using NER
            try:
                name_entities = self.hf_client.token_classification(text)
                for entity in name_entities:
                    if entity['entity_group'] == 'PER':
                        result['name'] = entity['word']
                        break
            except:
                pass
            
            # Extract email using regex
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            if email_match:
                result['email'] = email_match.group()
            
            # Extract phone using regex (Indian format)
            phone_patterns = [
                r'\+91[-\s]?\d{10}',
                r'\b\d{10}\b',
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
            ]
            for pattern in phone_patterns:
                phone_match = re.search(pattern, text)
                if phone_match:
                    result['phone'] = phone_match.group()
                    break
            
            # Extract skills
            result['skills'] = self._extract_skills_from_text(text)
            
            # Extract education
            result['education'] = self._extract_education(text)
            
            # Extract experience
            result['experience'] = self._extract_experience(text)
            
            # Add confidence scores
            result['confidence_scores'] = {
                'name': 0.7 if result.get('name') else 0.0,
                'email': 1.0 if result.get('email') else 0.0,
                'phone': 0.9 if result.get('phone') else 0.0,
                'skills': 0.8,
                'education': 0.7,
                'experience': 0.6
            }
            
            return result
            
        except Exception as e:
            print(f"Hugging Face parsing error: {e}")
            raise
    
    def _parse_with_spacy(self, text: str) -> Dict[str, Any]:
        """Parse resume using spaCy NLP (offline fallback)"""
        if not nlp:
            return self._get_empty_result()
        
        try:
            doc = nlp(text)
            
            result = self._get_empty_result()
            
            # Extract name using NER
            for ent in doc.ents:
                if ent.label_ == "PERSON" and not result.get('name'):
                    result['name'] = ent.text
                    break
            
            # Extract email using regex
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            if email_match:
                result['email'] = email_match.group()
            
            # Extract phone using regex (Indian format)
            phone_patterns = [
                r'\+91[-\s]?\d{10}',
                r'\b\d{10}\b',
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
            ]
            for pattern in phone_patterns:
                phone_match = re.search(pattern, text)
                if phone_match:
                    result['phone'] = phone_match.group()
                    break
            
            # Extract skills
            result['skills'] = self._extract_skills_from_text(text)
            
            # Extract education
            result['education'] = self._extract_education(text)
            
            # Extract experience
            result['experience'] = self._extract_experience(text)
            
            # Extract projects (simple pattern matching)
            result['projects'] = self._extract_projects(text)
            
            # Add confidence scores
            result['confidence_scores'] = {
                'name': 0.6 if result.get('name') else 0.0,
                'email': 1.0 if result.get('email') else 0.0,
                'phone': 0.9 if result.get('phone') else 0.0,
                'skills': 0.7,
                'education': 0.6,
                'experience': 0.5
            }
            
            return result
            
        except Exception as e:
            print(f"spaCy parsing error: {e}")
            return self._get_empty_result()
    
    def _extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills from text"""
        text_lower = text.lower()
        
        technical_skills = []
        soft_skills = []
        
        # Extract technical skills
        for category, skills in TECHNICAL_SKILLS.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    technical_skills.append(skill.title())
        
        # Remove duplicates
        technical_skills = list(set(technical_skills))
        
        # Extract soft skills
        for skill in SOFT_SKILLS:
            if skill.lower() in text_lower:
                soft_skills.append(skill.title())
        
        soft_skills = list(set(soft_skills))
        
        return {
            'technical': technical_skills,
            'soft': soft_skills
        }
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education details from text"""
        education = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for degree patterns
            degree_found = False
            for degree_pattern in EDUCATION_PATTERNS['degrees']:
                if re.search(degree_pattern, line_lower):
                    degree_found = True
                    break
            
            if degree_found:
                edu_entry = {}
                
                # Extract degree
                for degree_pattern in EDUCATION_PATTERNS['degrees']:
                    match = re.search(degree_pattern, line_lower)
                    if match:
                        edu_entry['degree'] = match.group().upper()
                        break
                
                # Extract institution
                for inst_pattern in EDUCATION_PATTERNS['institutions']:
                    if re.search(inst_pattern, line_lower):
                        edu_entry['institution'] = line.strip()
                        break
                
                # Extract year
                year_match = re.search(r'(20\d{2})|(?:\b(19\d{2})\b)', line)
                if year_match:
                    edu_entry['year'] = year_match.group()
                
                # Extract CGPA/Percentage
                cgpa_match = re.search(r'(\d+\.\d+)\s*(?:cgpa|gpa)', line_lower)
                if cgpa_match:
                    edu_entry['cgpa'] = cgpa_match.group(1)
                else:
                    percentage_match = re.search(r'(\d+\.?\d*)%', line)
                    if percentage_match:
                        edu_entry['cgpa'] = percentage_match.group(1) + '%'
                
                if edu_entry:
                    education.append(edu_entry)
        
        return education
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from text"""
        experience = []
        lines = text.split('\n')
        
        experience_keywords = ['intern', 'experience', 'work', 'job', 'employed', 'role']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for experience indicators
            if any(keyword in line_lower for keyword in experience_keywords):
                exp_entry = {}
                
                # Simple extraction - look for company-like patterns
                # This is a basic implementation that can be enhanced
                if len(line.strip()) > 5 and len(line.strip()) < 100:
                    exp_entry['role'] = line.strip()
                    
                    # Look for duration in current or next line
                    duration_patterns = [
                        r'(\d+\s*(?:months?|years?|mos?|yrs?))',
                        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}',
                        r'\d{1,2}/\d{4}\s*[-–]\s*\d{1,2}/\d{4}'
                    ]
                    
                    for j in range(i, min(i+3, len(lines))):
                        for pattern in duration_patterns:
                            match = re.search(pattern, lines[j].lower())
                            if match:
                                exp_entry['duration'] = match.group()
                                break
                        if exp_entry.get('duration'):
                            break
                
                if exp_entry.get('role'):
                    experience.append(exp_entry)
        
        return experience[:3]  # Return max 3 experiences
    
    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract project details from text"""
        projects = []
        lines = text.split('\n')
        
        project_keywords = ['project', 'developed', 'built', 'created', 'implemented']
        
        current_project = None
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            line_stripped = line.strip()
            
            # Check for project indicators
            if any(keyword in line_lower for keyword in project_keywords):
                if current_project and len(current_project.get('description', '')) > 10:
                    projects.append(current_project)
                
                current_project = {
                    'name': line_stripped,
                    'technologies': [],
                    'description': ''
                }
            
            # Add to current project description
            elif current_project and line_stripped and len(line_stripped) > 10:
                if len(current_project['description']) < 200:  # Limit description length
                    current_project['description'] += line_stripped + " "
                
                # Extract technologies from project description
                project_techs = self._extract_skills_from_text(line_stripped)['technical']
                current_project['technologies'].extend(project_techs)
                current_project['technologies'] = list(set(current_project['technologies']))
        
        # Add the last project
        if current_project and len(current_project.get('description', '')) > 10:
            projects.append(current_project)
        
        return projects[:5]  # Return max 5 projects
    
    def _get_empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            'name': '',
            'email': '',
            'phone': '',
            'education': [],
            'skills': {
                'technical': [],
                'soft': []
            },
            'experience': [],
            'projects': [],
            'certifications': [],
            'confidence_scores': {
                'name': 0.0,
                'email': 0.0,
                'phone': 0.0,
                'skills': 0.0,
                'education': 0.0,
                'experience': 0.0
            }
        }

# Global instance
resume_parser = ResumeParser()

def parse_resume_file(file_path: str) -> Dict[str, Any]:
    """
    Main function to parse resume file
    
    Args:
        file_path (str): Path to resume file
    
    Returns:
        dict: Parsed resume data
    """
    return resume_parser.parse_resume(file_path)

# Test function
def test_parser():
    """Test the resume parser with sample data"""
    sample_text = """
    RAHUL KUMAR
    Email: rahul.kumar@example.com
    Phone: +91-9876543210
    
    EDUCATION
    B.Tech in Computer Science and Engineering
    Biju Patnaik University of Technology, Odisha
    CGPA: 8.5/10
    Expected Graduation: 2025
    
    SKILLS
    Programming: Python, Java, JavaScript, C++
    Web Development: React, Node.js, Django, Flask
    Databases: MySQL, MongoDB
    Tools: Git, Docker, AWS
    
    EXPERIENCE
    Software Development Intern
    Tech Solutions Pvt. Ltd., Bhubaneswar
    June 2024 - August 2024
    - Developed web applications using React and Node.js
    - Implemented RESTful APIs
    - Collaborated with team using Agile methodology
    
    PROJECTS
    E-commerce Website
    - Built using React, Node.js, MongoDB
    - Features: user authentication, product catalog, shopping cart
    - Deployed on AWS EC2
    
    Machine Learning Project
    - Developed sentiment analysis model using Python and TensorFlow
    - Achieved 85% accuracy on test data
    """
    
    # Test with sample text file
    with open('sample_resume.txt', 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    result = parse_resume_file('sample_resume.txt')
    print("Parsing Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Clean up
    if os.path.exists('sample_resume.txt'):
        os.remove('sample_resume.txt')
    
    return result

if __name__ == "__main__":
    test_parser()