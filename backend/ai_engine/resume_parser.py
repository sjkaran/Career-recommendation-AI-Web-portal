"""
Enhanced NLP Resume Parser with spaCy and OpenAI Fallback
Description: Extracts structured information from resumes in PDF, DOCX, and TXT formats
Author: BPUT Career Platform Team
Date: 2024
"""

import spacy
import re
import json
import pdfplumber
import docx2txt
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import openai
from backend.config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    """
    Enhanced resume parser that uses spaCy for entity extraction with OpenAI fallback
    """
    
    def __init__(self):
        """Initialize the parser with spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.error("spaCy model 'en_core_web_sm' not found. Please install it using: python -m spacy download en_core_web_sm")
            raise
        
        # Indian education patterns
        self.education_patterns = [
            r'(B\.?Tech\.?|B\.?E\.?|Bachelor of Technology)',
            r'(M\.?Tech\.?|M\.?E\.?|Master of Technology)',
            r'(B\.?Sc\.?|Bachelor of Science)',
            r'(M\.?Sc\.?|Master of Science)',
            r'(B\.?C\.?A\.?|Bachelor of Computer Applications)',
            r'(M\.?C\.?A\.?|Master of Computer Applications)',
            r'(B\.?B\.?A\.?|Bachelor of Business Administration)',
            r'(M\.?B\.?A\.?|Master of Business Administration)',
            r'(Diploma)'
        ]
        
        # Programming languages and frameworks
        self.technical_skills = {
            'programming_languages': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 
                'swift', 'kotlin', 'typescript', 'r', 'matlab', 'scala', 'perl'
            ],
            'frameworks': [
                'django', 'flask', 'react', 'angular', 'vue', 'spring', 'express', 
                'laravel', 'ruby on rails', 'tensorflow', 'pytorch', 'keras',
                'bootstrap', 'jquery', 'node.js', 'react native', 'flutter'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'redis', 
                'cassandra', 'dynamodb', 'firebase'
            ],
            'tools': [
                'git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp',
                'linux', 'unix', 'jira', 'confluence', 'figma', 'photoshop'
            ]
        }
        
        self.soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
            'time management', 'adaptability', 'creativity', 'work ethic', 'attention to detail',
            'collaboration', 'analytical skills', 'presentation', 'negotiation'
        ]

    def extract_text_from_file(self, file_path: str, file_format: str) -> Optional[str]:
        """
        Extract text from PDF, DOCX, or TXT files
        
        Args:
            file_path: Path to the resume file
            file_format: One of 'pdf', 'docx', 'txt'
            
        Returns:
            Extracted text or None if error
        """
        try:
            if file_format.lower() == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_format.lower() == 'docx':
                return self._extract_from_docx(file_path)
            elif file_format.lower() == 'txt':
                return self._extract_from_txt(file_path)
            else:
                logger.error(f"Unsupported file format: {file_format}")
                return None
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return None

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            raise

    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"TXT extraction error: {str(e)}")
            raise

    def parse_resume(self, file_path: str, file_format: str) -> Dict:
        """
        Main method to parse resume and return structured data
        
        Args:
            file_path: Path to resume file
            file_format: File format ('pdf', 'docx', 'txt')
            
        Returns:
            Dictionary with parsed resume data
        """
        start_time = datetime.now()
        
        try:
            # Extract text from file
            text = self.extract_text_from_file(file_path, file_format)
            if not text:
                return self._fallback_to_openai(file_path, file_format)
            
            # Try spaCy parsing first
            spacy_result = self._parse_with_spacy(text)
            
            # If spaCy extraction is poor, fallback to OpenAI
            if self._is_extraction_poor(spacy_result):
                logger.info("spaCy extraction quality poor, falling back to OpenAI")
                openai_result = self._fallback_to_openai(file_path, file_format)
                return self._merge_results(spacy_result, openai_result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            spacy_result['processing_metadata']['processing_time_seconds'] = processing_time
            
            return spacy_result
            
        except Exception as e:
            logger.error(f"Resume parsing failed: {str(e)}")
            # Final fallback to OpenAI
            return self._fallback_to_openai(file_path, file_format)

    def _parse_with_spacy(self, text: str) -> Dict:
        """
        Parse resume text using spaCy
        
        Args:
            text: Resume text content
            
        Returns:
            Structured resume data
        """
        doc = self.nlp(text)
        
        result = {
            'personal_info': self._extract_personal_info(doc, text),
            'education': self._extract_education(doc, text),
            'work_experience': self._extract_work_experience(doc, text),
            'skills': self._extract_skills(doc, text),
            'projects': self._extract_projects(doc, text),
            'certifications': self._extract_certifications(doc, text),
            'processing_metadata': {
                'parser_used': 'spacy',
                'confidence_score': 0.0,
                'extraction_quality': 'high'
            }
        }
        
        # Calculate overall confidence score
        result['processing_metadata']['confidence_score'] = self._calculate_confidence(result)
        
        return result

    def _extract_personal_info(self, doc, text: str) -> Dict:
        """Extract personal information"""
        personal_info = {
            'name': self._extract_name(doc),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'confidence': 0.0
        }
        
        # Calculate confidence for personal info
        confidence_factors = []
        if personal_info['name']: confidence_factors.append(0.3)
        if personal_info['email']: confidence_factors.append(0.4)
        if personal_info['phone']: confidence_factors.append(0.3)
        
        personal_info['confidence'] = sum(confidence_factors)
        return personal_info

    def _extract_name(self, doc) -> Optional[str]:
        """Extract candidate name using NER"""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Simple heuristic: first PERSON entity is likely the name
                return ent.text
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number using regex"""
        # Indian phone number patterns
        phone_patterns = [
            r'\b\d{10}\b',  # 10 digits
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 333-333-3333
            r'\b\d{5}[-.\s]?\d{5}\b',  # 33333 33333
            r'\b\+91[-.\s]?\d{10}\b'  # +91 3333333333
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return None

    def _extract_education(self, doc, text: str) -> List[Dict]:
        """Extract education information"""
        education_entries = []
        
        # Look for education section
        edu_section = self._find_section(text, ['education', 'academic', 'qualification'])
        
        if edu_section:
            # Split by lines and process each potential education entry
            lines = edu_section.split('\n')
            current_entry = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Look for degree patterns
                degree_match = self._find_degree(line)
                if degree_match:
                    if current_entry:  # Save previous entry
                        education_entries.append(current_entry)
                    current_entry = {
                        'degree': degree_match,
                        'institution': self._extract_institution(line),
                        'year': self._extract_year(line),
                        'grade': self._extract_grade(line),
                        'confidence': 0.7
                    }
                elif current_entry and not current_entry.get('institution'):
                    # Try to extract institution from subsequent lines
                    institution = self._extract_institution(line)
                    if institution:
                        current_entry['institution'] = institution
            
            if current_entry:
                education_entries.append(current_entry)
        
        return education_entries

    def _find_degree(self, text: str) -> Optional[str]:
        """Find degree in text"""
        for pattern in self.education_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_institution(self, text: str) -> Optional[str]:
        """Extract educational institution"""
        # Common Indian institutions patterns
        institutions = [
            'BPUT', 'Biju Patnaik University', 'IIT', 'NIT', 'VSSUT', 'CET', 'ITER', 'SOA',
            'Siksha O Anusandhan', 'KIIT', 'CVRCE', 'GITA', 'TECHNO'
        ]
        
        for inst in institutions:
            if inst.lower() in text.lower():
                return inst
        
        # Fallback: look for capitalized words that might be institutions
        words = text.split()
        potential_inst = []
        for word in words:
            if word.istitle() and len(word) > 3:
                potential_inst.append(word)
        
        return ' '.join(potential_inst[:3]) if potential_inst else None

    def _extract_year(self, text: str) -> Optional[str]:
        """Extract year from education entry"""
        year_pattern = r'(20\d{2}[-–]20\d{2}|20\d{2}[-–]Present|20\d{2})'
        match = re.search(year_pattern, text)
        return match.group(0) if match else None

    def _extract_grade(self, text: str) -> Optional[str]:
        """Extract grade/CGPA from text"""
        # CGPA patterns
        cgpa_patterns = [
            r'CGPA[:]?\s*(\d+\.\d+)',
            r'GPA[:]?\s*(\d+\.\d+)',
            r'(\d+\.\d+)\s*(?:CGPA|GPA)',
            r'(\d+\.\d+)\/\d+\.\d+'  # 8.5/10.0
        ]
        
        # Percentage patterns
        percentage_patterns = [
            r'(\d+\.?\d*)%',
            r'(\d+\.?\d*)\s*%',
            r'percentage[:]?\s*(\d+\.?\d*)'
        ]
        
        for pattern in cgpa_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"CGPA: {match.group(1)}"
        
        for pattern in percentage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"Percentage: {match.group(1)}%"
        
        return None

    def _extract_work_experience(self, doc, text: str) -> List[Dict]:
        """Extract work experience information"""
        experience_entries = []
        
        # Find experience section
        exp_section = self._find_section(text, ['experience', 'work', 'employment', 'internship'])
        
        if exp_section:
            lines = exp_section.split('\n')
            current_entry = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for company patterns and dates
                company = self._extract_company(line)
                duration = self._extract_duration(line)
                
                if company or duration:
                    if current_entry:  # Save previous entry
                        experience_entries.append(current_entry)
                    
                    current_entry = {
                        'company': company,
                        'role': self._extract_role(line),
                        'duration': duration,
                        'description': line,
                        'confidence': 0.6
                    }
                elif current_entry:
                    # Add to description of current entry
                    current_entry['description'] += ' ' + line
            
            if current_entry:
                experience_entries.append(current_entry)
        
        return experience_entries

    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name"""
        # Look for organization entities in spaCy doc
        line_doc = self.nlp(text)
        for ent in line_doc.ents:
            if ent.label_ == "ORG":
                return ent.text
        return None

    def _extract_role(self, text: str) -> Optional[str]:
        """Extract job role"""
        roles = ['intern', 'developer', 'engineer', 'analyst', 'manager', 'lead', 'head']
        words = text.lower().split()
        
        for i, word in enumerate(words):
            if word in roles and i > 0:
                # Return the role with context
                start = max(0, i-2)
                return ' '.join(words[start:i+1]).title()
        
        return None

    def _extract_duration(self, text: str) -> Optional[str]:
        """Extract duration with various date formats"""
        duration_patterns = [
            r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|Present)',
            r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|Present)',
            r'(\d{4})\s*[-–]\s*(\d{4})',
            r'(\d{1,2} \w+ \d{4})\s*[-–]\s*(\d{1,2} \w+ \d{4})'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)} - {match.group(2)}"
        
        return None

    def _extract_skills(self, doc, text: str) -> Dict:
        """Extract technical and soft skills"""
        skills_section = self._find_section(text, ['skills', 'technical', 'programming'])
        
        all_skills_text = skills_section if skills_section else text
        all_skills_text_lower = all_skills_text.lower()
        
        technical_skills = []
        soft_skills = []
        
        # Extract technical skills
        for category, skills in self.technical_skills.items():
            for skill in skills:
                if skill.lower() in all_skills_text_lower:
                    technical_skills.append({
                        'skill': skill.title(),
                        'category': category,
                        'confidence': 0.8
                    })
        
        # Extract soft skills
        for skill in self.soft_skills:
            if skill.lower() in all_skills_text_lower:
                soft_skills.append({
                    'skill': skill.title(),
                    'category': 'soft_skills',
                    'confidence': 0.7
                })
        
        return {
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'confidence': min(0.8, len(technical_skills) * 0.1)  # Higher confidence with more skills
        }

    def _extract_projects(self, doc, text: str) -> List[Dict]:
        """Extract project information"""
        projects_section = self._find_section(text, ['projects', 'personal projects', 'academic projects'])
        projects = []
        
        if projects_section:
            lines = projects_section.split('\n')
            current_project = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Project titles often start with specific patterns
                if (line.istitle() or 
                    re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', line) or
                    'project' in line.lower()):
                    
                    if current_project:
                        projects.append(current_project)
                    
                    current_project = {
                        'title': line,
                        'description': '',
                        'technologies': [],
                        'confidence': 0.6
                    }
                elif current_project:
                    current_project['description'] += ' ' + line
                    # Extract technologies from description
                    for category, skills in self.technical_skills.items():
                        for skill in skills:
                            if skill.lower() in line.lower() and skill not in current_project['technologies']:
                                current_project['technologies'].append(skill.title())
            
            if current_project:
                projects.append(current_project)
        
        return projects

    def _extract_certifications(self, doc, text: str) -> List[Dict]:
        """Extract certifications"""
        cert_section = self._find_section(text, ['certifications', 'certificates', 'courses'])
        certifications = []
        
        if cert_section:
            lines = cert_section.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.isspace():
                    certifications.append({
                        'name': line,
                        'confidence': 0.5
                    })
        
        return certifications

    def _find_section(self, text: str, section_names: List[str]) -> Optional[str]:
        """Find a specific section in the resume text"""
        lines = text.split('\n')
        in_section = False
        section_content = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if this line starts a section we're looking for
            if any(name in line_lower for name in section_names):
                in_section = True
                continue
            
            # If we're in a section and hit another major section, break
            if in_section and line_lower and (
                'experience' in line_lower or 
                'education' in line_lower or 
                'skills' in line_lower or
                'projects' in line_lower
            ):
                break
            
            if in_section and line.strip():
                section_content.append(line.strip())
        
        return '\n'.join(section_content) if section_content else None

    def _is_extraction_poor(self, result: Dict) -> bool:
        """Check if spaCy extraction quality is poor"""
        confidence = result['processing_metadata']['confidence_score']
        
        # If confidence is very low or no personal info extracted
        if confidence < 0.3:
            return True
        
        # If no education or experience found
        if not result['education'] and not result['work_experience']:
            return True
        
        return False

    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate overall confidence score for extraction"""
        weights = {
            'personal_info': 0.3,
            'education': 0.25,
            'work_experience': 0.25,
            'skills': 0.2
        }
        
        scores = []
        
        # Personal info confidence
        personal_conf = result['personal_info'].get('confidence', 0)
        scores.append(personal_conf * weights['personal_info'])
        
        # Education confidence (average of entries)
        edu_conf = sum(edu.get('confidence', 0) for edu in result['education']) / max(1, len(result['education']))
        scores.append(edu_conf * weights['education'])
        
        # Work experience confidence
        exp_conf = sum(exp.get('confidence', 0) for exp in result['work_experience']) / max(1, len(result['work_experience']))
        scores.append(exp_conf * weights['work_experience'])
        
        # Skills confidence
        skills_conf = result['skills'].get('confidence', 0)
        scores.append(skills_conf * weights['skills'])
        
        return min(1.0, sum(scores))

    def _fallback_to_openai(self, file_path: str, file_format: str) -> Dict:
        """
        Fallback to OpenAI API when spaCy parsing fails
        
        Args:
            file_path: Path to resume file
            file_format: File format
            
        Returns:
            Structured resume data from OpenAI
        """
        try:
            if not Config.OPENAI_API_KEY:
                logger.warning("OpenAI API key not configured, returning empty result")
                return self._get_empty_result()
            
            # Extract text
            text = self.extract_text_from_file(file_path, file_format)
            if not text:
                return self._get_empty_result()
            
            # Use OpenAI to parse resume
            openai.api_key = Config.OPENAI_API_KEY
            
            prompt = f"""
            Parse the following resume text and extract structured information in JSON format.
            Focus on Indian education system and job market.
            
            Resume Text:
            {text[:3000]}  # Limit text to avoid token limits
            
            Extract the following information:
            - personal_info (name, email, phone)
            - education (degree, institution, year, grade)
            - work_experience (company, role, duration, description)
            - skills (technical_skills, soft_skills)
            - projects (title, description, technologies)
            - certifications (name)
            
            Return ONLY valid JSON, no other text.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a resume parser. Extract structured information from resumes and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            # Parse OpenAI response
            result_text = response.choices[0].message.content.strip()
            openai_result = json.loads(result_text)
            
            # Add processing metadata
            openai_result['processing_metadata'] = {
                'parser_used': 'openai',
                'confidence_score': 0.9,  # OpenAI generally has high confidence
                'extraction_quality': 'high'
            }
            
            return openai_result
            
        except Exception as e:
            logger.error(f"OpenAI fallback failed: {str(e)}")
            return self._get_empty_result()

    def _merge_results(self, spacy_result: Dict, openai_result: Dict) -> Dict:
        """Merge results from spaCy and OpenAI"""
        merged = openai_result.copy()  # Prefer OpenAI results
        
        # Fill in any missing fields from spaCy
        for key in spacy_result:
            if key not in merged or not merged[key]:
                merged[key] = spacy_result[key]
        
        merged['processing_metadata']['parser_used'] = 'hybrid'
        return merged

    def _get_empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'personal_info': {'name': None, 'email': None, 'phone': None, 'confidence': 0.0},
            'education': [],
            'work_experience': [],
            'skills': {'technical_skills': [], 'soft_skills': [], 'confidence': 0.0},
            'projects': [],
            'certifications': [],
            'processing_metadata': {
                'parser_used': 'none',
                'confidence_score': 0.0,
                'extraction_quality': 'poor',
                'error': 'Parsing failed'
            }
        }


# Singleton instance
resume_parser = ResumeParser()