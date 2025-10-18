"""
Resume Parser using FREE APIs and fallback to regex
No paid APIs required - uses pattern matching and free text extraction
"""

import os
import re
import json
import PyPDF2
import docx2txt
from typing import Dict, List, Any

# Technical skills database
TECHNICAL_SKILLS = [
    'Python', 'Java', 'JavaScript', 'C++', 'C', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
    'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Node.js', 'Express',
    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQLite',
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'Jenkins',
    'Machine Learning', 'Data Science', 'AI', 'Deep Learning', 'TensorFlow',
    'PyTorch', 'scikit-learn', 'Pandas', 'NumPy', 'Matplotlib'
]

SOFT_SKILLS = [
    'Communication', 'Leadership', 'Teamwork', 'Problem Solving',
    'Critical Thinking', 'Time Management', 'Adaptability', 'Creativity'
]

def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Parse resume using pattern matching (100% free)
    
    Args:
        file_path: Path to resume file
        
    Returns:
        Dictionary with extracted information
    """
    try:
        # Extract text from file
        text = extract_text_from_file(file_path)
        
        if not text or len(text.strip()) < 50:
            return get_empty_result()
        
        # Parse using pattern matching
        result = {
            'name': extract_name(text),
            'email': extract_email(text),
            'phone': extract_phone(text),
            'education': extract_education(text),
            'skills': extract_skills(text),
            'experience': extract_experience(text),
            'projects': extract_projects(text),
            'certifications': extract_certifications(text)
        }
        
        return result
        
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return get_empty_result()

def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF, DOCX, or TXT file"""
    file_ext = file_path.split('.')[-1].lower()
    
    try:
        if file_ext == 'pdf':
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
                
        elif file_ext == 'docx':
            return docx2txt.process(file_path)
            
        elif file_ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
                
        else:
            return ""
            
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_name(text: str) -> str:
    """Extract name from resume"""
    # Name is usually in the first few lines
    lines = text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        # Skip empty lines and common headers
        if not line or line.lower() in ['resume', 'curriculum vitae', 'cv']:
            continue
        # Name is usually 2-4 words, capitalized
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            return line
    return ""

def extract_email(text: str) -> str:
    """Extract email address"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group() if match else ""

def extract_phone(text: str) -> str:
    """Extract phone number (Indian format)"""
    phone_patterns = [
        r'\+91[-\s]?\d{10}',
        r'\b\d{10}\b',
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    return ""

def extract_education(text: str) -> List[Dict[str, str]]:
    """Extract education details"""
    education = []
    
    # Degree patterns
    degree_patterns = [
        r'b\.?tech\.?', r'b\.?e\.?', r'bachelor',
        r'm\.?tech\.?', r'm\.?e\.?', r'master',
        r'b\.?sc\.?', r'm\.?sc\.?',
        r'b\.?ca\.?', r'm\.?ca\.?',
        r'diploma', r'ph\.?d\.?'
    ]
    
    lines = text.lower().split('\n')
    
    for i, line in enumerate(lines):
        # Check if line contains degree
        for pattern in degree_patterns:
            if re.search(pattern, line):
                edu_entry = {
                    'degree': line.strip()[:100],
                    'institution': '',
                    'year': '',
                    'cgpa': ''
                }
                
                # Look for institution in nearby lines
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if 'college' in lines[j] or 'university' in lines[j] or 'institute' in lines[j]:
                        edu_entry['institution'] = lines[j].strip()[:100]
                        break
                
                # Extract year
                year_match = re.search(r'(20\d{2})|(\b19\d{2}\b)', text[max(0, i*50-100):(i+3)*50])
                if year_match:
                    edu_entry['year'] = year_match.group()
                
                # Extract CGPA
                cgpa_match = re.search(r'(\d+\.\d+)\s*(?:cgpa|gpa)', text[max(0, i*50-100):(i+3)*50], re.IGNORECASE)
                if cgpa_match:
                    edu_entry['cgpa'] = cgpa_match.group(1)
                
                education.append(edu_entry)
                break
    
    return education[:3]  # Return max 3 education entries

def extract_skills(text: str) -> Dict[str, List[str]]:
    """Extract technical and soft skills"""
    text_lower = text.lower()
    
    technical = []
    soft = []
    
    # Extract technical skills
    for skill in TECHNICAL_SKILLS:
        if skill.lower() in text_lower:
            technical.append(skill)
    
    # Extract soft skills
    for skill in SOFT_SKILLS:
        if skill.lower() in text_lower:
            soft.append(skill)
    
    return {
        'technical': list(set(technical)),
        'soft': list(set(soft))
    }

def extract_experience(text: str) -> List[Dict[str, str]]:
    """Extract work experience"""
    experience = []
    
    keywords = ['experience', 'intern', 'work', 'employment', 'trainee']
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Check if line contains experience keywords
        if any(keyword in line_lower for keyword in keywords):
            if len(line.strip()) > 10 and len(line.strip()) < 100:
                exp_entry = {
                    'role': line.strip(),
                    'company': '',
                    'duration': ''
                }
                
                # Look for duration in nearby lines
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
                
                experience.append(exp_entry)
    
    return experience[:3]  # Return max 3 experiences

def extract_projects(text: str) -> List[Dict[str, Any]]:
    """Extract project details"""
    projects = []
    
    keywords = ['project', 'developed', 'built', 'created', 'implemented']
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        if any(keyword in line_lower for keyword in keywords):
            if len(line.strip()) > 10:
                project = {
                    'name': line.strip()[:100],
                    'description': '',
                    'technologies': []
                }
                
                # Look for technologies in nearby lines
                tech_text = ' '.join(lines[i:min(i+3, len(lines))]).lower()
                for skill in TECHNICAL_SKILLS:
                    if skill.lower() in tech_text:
                        project['technologies'].append(skill)
                
                # Get description from next line if available
                if i+1 < len(lines) and len(lines[i+1].strip()) > 20:
                    project['description'] = lines[i+1].strip()[:200]
                
                projects.append(project)
    
    return projects[:5]  # Return max 5 projects

def extract_certifications(text: str) -> List[str]:
    """Extract certifications"""
    certifications = []
    
    cert_keywords = ['certified', 'certification', 'certificate', 'qualified']
    lines = text.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in cert_keywords):
            if len(line.strip()) > 10 and len(line.strip()) < 150:
                certifications.append(line.strip())
    
    return certifications[:5]  # Return max 5 certifications

def get_empty_result() -> Dict[str, Any]:
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
        'certifications': []
    }

# Test function
if __name__ == "__main__":
    sample_text = """
    RAHUL KUMAR
    Email: rahul.kumar@example.com
    Phone: +91-9876543210
    
    EDUCATION
    B.Tech in Computer Science Engineering
    Biju Patnaik University of Technology, Odisha
    CGPA: 8.5/10
    Expected Graduation: 2025
    
    SKILLS
    Python, Java, JavaScript, React, Node.js, MySQL, MongoDB
    Machine Learning, Data Science, AWS, Docker
    
    EXPERIENCE
    Software Development Intern
    Tech Solutions Pvt. Ltd., Bhubaneswar
    June 2024 - August 2024
    
    PROJECTS
    E-commerce Website - Built using React and Node.js
    Machine Learning Project - Sentiment analysis using Python
    """
    
    result = parse_resume('test.txt')
    print(json.dumps(result, indent=2))