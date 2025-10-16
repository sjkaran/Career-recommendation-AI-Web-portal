import openai
import os
import PyPDF2
import docx2txt
from config import Config

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return ""

def parse_resume(file_path):
    """
    Parse resume using OpenAI GPT-4 to extract structured information
    """
    try:
        # Extract text based on file type
        file_ext = file_path.split('.')[-1].lower()
        
        if file_ext == 'pdf':
            text = extract_text_from_pdf(file_path)
        elif file_ext == 'docx':
            text = extract_text_from_docx(file_path)
        elif file_ext == 'txt':
            text = extract_text_from_txt(file_path)
        else:
            return None
        
        if not text:
            return None
        
        # Use OpenAI to parse resume
        openai.api_key = Config.OPENAI_API_KEY
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert at parsing resumes and extracting structured information. 
                    Extract the following information from the resume text:
                    - skills (list of technical and soft skills)
                    - education (degree, institution, year)
                    - experience (job titles, companies, duration)
                    - projects (project names, descriptions)
                    - certifications (if any)
                    Return the data as a JSON object with these keys."""
                },
                {
                    "role": "user",
                    "content": f"Extract information from this resume:\n\n{text[:3000]}"  # Limit text length
                }
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        # Parse the response (this is a simplified version)
        # In a real implementation, you'd parse the JSON response properly
        extracted_data = {
            'skills': [],
            'education': '',
            'experience': [],
            'projects': [],
            'certifications': []
        }
        
        # For demo purposes, we'll do simple keyword extraction
        # In production, you'd use the OpenAI response
        text_lower = text.lower()
        
        # Simple skill extraction (very basic)
        common_skills = ['python', 'java', 'javascript', 'html', 'css', 'react', 'node', 
                        'sql', 'mongodb', 'aws', 'docker', 'git', 'machine learning', 
                        'data analysis', 'flask', 'django', 'spring', 'c++', 'c#']
        
        found_skills = [skill for skill in common_skills if skill in text_lower]
        extracted_data['skills'] = found_skills
        
        return extracted_data
        
    except Exception as e:
        print(f"Error parsing resume with AI: {e}")
        return None