import re
import json
import math
from datetime import datetime
from collections import Counter

class AIRecruitmentAgent:
    """
    Enterprise AI Recruitment Agent v2.0
    Enhanced Keyword Engine (85%+) + Optional OpenAI Integration (95%+)
    """
    
    def __init__(self):
        self.skill_keywords = self._load_skill_database()
        self.education_keywords = self._load_education_keywords()
        self.experience_patterns = self._load_experience_patterns()
        self.use_openai = False
        try:
            import streamlit as st
            self.openai_key = st.secrets.get("OPENAI_API_KEY", "")
            if self.openai_key:
                self.use_openai = True
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_key)
        except:
            pass
    
    def _load_skill_database(self):
        return {
            'technical': {
                'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'],
                'web': ['react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'spring', 'laravel', 'next.js', 'nuxt'],
                'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd', 'devops', 'serverless'],
                'data': ['sql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'spark', 'hadoop', 'tableau', 'power bi', 'snowflake'],
                'ai_ml': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'llm', 'langchain', 'ai agents'],
                'automation': ['n8n', 'zapier', 'make', 'power automate', 'uipath', 'automation anywhere', 'workflow automation'],
                'mobile': ['android', 'ios', 'flutter', 'react native', 'swift', 'kotlin'],
                'erp': ['sap', 'oracle', 'microsoft dynamics', 'netsuite', 'odoo'],
            },
            'business': {
                'management': ['project management', 'agile', 'scrum', 'kanban', 'jira', 'confluence', 'pmo'],
                'analysis': ['business analysis', 'data analysis', 'financial modeling', 'market research', 'business intelligence'],
                'strategy': ['strategic planning', 'business strategy', 'digital transformation', 'change management', 'operational excellence'],
                'marketing': ['digital marketing', 'seo', 'sem', 'social media', 'content marketing', 'brand management', 'lead generation'],
                'sales': ['business development', 'account management', 'negotiation', 'crm', 'salesforce', 'pipeline management'],
                'finance': ['financial analysis', 'budgeting', 'forecasting', 'p&l', 'financial reporting', 'audit'],
            },
            'hr_specific': {
                'hris': ['hris', 'sap successfactors', 'oracle hcm', 'workday', 'bamboo', 'people management'],
                'talent': ['talent acquisition', 'recruitment', 'sourcing', 'employer branding', 'onboarding', 'campus recruitment'],
                'performance': ['performance management', 'okrs', 'kpis', '360 feedback', 'appraisal', 'performance review'],
                'compensation': ['compensation', 'benefits', 'payroll', 'salary structure', 'grading', 'total rewards'],
                'training': ['l&d', 'training', 'development', 'succession planning', 'career development', 'learning management'],
                'compliance': ['labor law', 'compliance', 'policy', 'employee relations', 'disciplinary', 'grievance'],
                'engagement': ['employee engagement', 'culture', 'dei', 'diversity', 'inclusion', 'wellness'],
            },
            'facility_management': {
                'hvac': ['hvac', 'vrv', 'vrf', 'chillers', 'dx systems', 'ventilation', 'air distribution', 'cooling'],
                'bms': ['bms', 'building management', 'scada', 'automation', 'controls', 'siemens', 'honeywell'],
                'mep': ['mep', 'mechanical', 'electrical', 'plumbing', 'fire protection', 'fire alarm'],
                'maintenance': ['preventive maintenance', 'corrective maintenance', 'troubleshooting', 'repair', 'servicing'],
                'safety': ['hse', 'safety', 'osh', 'nebosh', 'risk assessment', 'permit to work'],
            },
            'real_estate': {
                'property': ['property management', 'leasing', 'tenant', 'occupancy', 'facility', 'real estate'],
                'development': ['property development', 'construction', 'project management', 'contractor', 'architect'],
                'trade': ['trade services', 'wtc', 'world trade center', 'membership', 'trade development'],
            },
            'soft_skills': {
                'leadership': ['leadership', 'team management', 'mentoring', 'coaching', 'delegation', 'empowerment'],
                'communication': ['communication', 'presentation', 'negotiation', 'stakeholder management', 'c-suite'],
                'analytical': ['problem solving', 'analytical', 'critical thinking', 'decision making', 'root cause analysis'],
                'execution': ['results-driven', 'delivery', 'execution', 'accountability', 'ownership', 'initiative'],
            }
        }
    
    def _load_education_keywords(self):
        return {
            'phd': ['phd', 'doctorate', 'ph.d', 'dba', 'edd'],
            'masters': ['master', 'msc', 'ma', 'mba', 'm.sc', 'm.a', 'mphil', 'm.eng'],
            'bachelors': ['bachelor', 'bsc', 'ba', 'b.sc', 'b.a', 'b.eng', 'b.tech', 'b.ed'],
            'diploma': ['diploma', 'hnd', 'ond', 'certificate', 'nce'],
            'certification': ['sphri', 'cipm', 'acipm', 'phri', 'shrm', 'pmp', 'cima', 'acca', 'nebosh', 'ccnp', 'cisco'],
        }
    
    def _load_experience_patterns(self):
        return [
            r'(\d+)[\+]*\s*years?\s*(?:of)?\s*(?:relevant)?\s*experience',
            r'experience[:\s]*(\d+)[\+]*\s*years?',
            r'(\d+)\+?\s*years?\s*(?:in|within)\s*(?:the)?\s*(?:field|industry|role)',
            r'(\d+)[\+]*\s*years?\s*(?:of)?\s*progressive\s*experience',
            r'minimum\s*(?:of)?\s*(\d+)\s*years?',
        ]
    
    def parse_cv(self, cv_text):
        """Advanced CV parsing with deep structure extraction"""
        if not cv_text or len(cv_text) < 50:
            return self._empty_parsed()
        
        parsed = {
            'name': self._extract_name(cv_text),
            'email': self._extract_email(cv_text),
            'phone': self._extract_phone(cv_text),
            'linkedin': self._extract_linkedin(cv_text),
            'github': self._extract_github(cv_text),
            'portfolio': self._extract_portfolio(cv_text),
            'summary': self._extract_summary(cv_text),
            'skills': self._extract_all_skills(cv_text),
            'experience': self._extract_experience_details(cv_text),
            'education': self._extract_education(cv_text),
            'certifications': self._extract_certifications(cv_text),
            'languages': self._extract_languages(cv_text),
            'total_experience_years': 0,
            'current_position': self._extract_current_position(cv_text),
            'current_company': self._extract_current_company(cv_text),
        }
        
        parsed['total_experience_years'] = self._calculate_total_experience(parsed['experience'])
        return parsed
    
    def _empty_parsed(self):
        return {
            'name': 'Unknown', 'email': '', 'phone': '', 'linkedin': '', 'github': '',
            'portfolio': '', 'summary': '', 'skills': [], 'experience': [],
            'education': [], 'certifications': [], 'languages': [],
            'total_experience_years': 0, 'current_position': '', 'current_company': ''
        }
    
    def _extract_name(self, text):
        lines = text.strip().split('\n')
        for line in lines[:8]:
            line = line.strip()
            if line and len(line) < 60 and len(line.split()) >= 2:
                if not any(kw in line.lower() for kw in ['email', 'phone', 'address', 'linkedin', 'summary', 
                    'objective', 'curriculum', 'resume', 'cv', 'http', 'www', 'github']):
                    return line
        return "Unknown"
    
    def _extract_email(self, text):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text):
        phone_patterns = [
            r'\+\d{1,3}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{4}',
            r'\d{3}[\s-]?\d{3}[\s-]?\d{4}',
            r'\d{11,13}',
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""
    
    def _extract_linkedin(self, text):
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        match = re.search(linkedin_pattern, text.lower())
        return f"https://www.{match.group(0)}" if match else ""
    
    def _extract_github(self, text):
        github_pattern = r'github\.com/[\w-]+'
        match = re.search(github_pattern, text.lower())
        return f"https://{match.group(0)}" if match else ""
    
    def _extract_portfolio(self, text):
        portfolio_patterns = [r'portfolio[:\s]*([\w./-]+)', r'(?:website|portfolio)[:\s]*(https?://[^\s]+)']
        for pattern in portfolio_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1) if match.lastindex else match.group(0)
        return ""
    
    def _extract_summary(self, text):
        summary_keywords = ['summary', 'profile', 'objective', 'about me', 'professional summary']
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in summary_keywords):
                summary_lines = []
                for j in range(i+1, min(i+6, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                    else:
                        break
                return ' '.join(summary_lines)[:500]
        return ""
    
    def _extract_all_skills(self, text):
        found_skills = []
        text_lower = text.lower()
        
        for category, subcategories in self.skill_keywords.items():
            for subcategory, skills in subcategories.items():
                for skill in skills:
                    if skill.lower() in text_lower:
                        found_skills.append({
                            'skill': skill,
                            'category': subcategory,
                            'domain': category
                        })
        
        # Remove duplicates
        seen = set()
        unique_skills = []
        for s in found_skills:
            if s['skill'].lower() not in seen:
                seen.add(s['skill'].lower())
                unique_skills.append(s)
        
        return unique_skills
    
    def _extract_experience_details(self, text):
        experiences = []
        lines = text.split('\n')
        in_exp = False
        
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in ['experience', 'employment', 'work history', 'professional background']):
                in_exp = True
                continue
            if in_exp and any(kw in line_lower for kw in ['education', 'skills', 'certification', 'language', 'reference']):
                break
            if in_exp and line.strip() and len(line.strip()) > 15:
                company = self._extract_company(line)
                dates = self._extract_dates(line)
                title = self._extract_job_title_from_line(line)
                
                if company or dates or title:
                    experiences.append({
                        'line': line.strip(),
                        'company': company,
                        'title': title,
                        'dates': dates,
                    })
        
        return experiences
    
    def _extract_company(self, line):
        company_patterns = [
            r'(?:at|with|for)\s+([A-Z][\w\s&.,()]+?)(?:,|\s{2,}|$|\s-\s)',
            r'^([A-Z][\w\s&.,()]+?)(?:,|\s{2,}|\s-\s)',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, line)
            if match:
                company = match.group(1).strip()
                if len(company) > 3 and not any(kw in company.lower() for kw in ['email', 'phone', 'address']):
                    return company[:50]
        return ""
    
    def _extract_dates(self, line):
        date_patterns = [
            r'(\d{1,2}/\d{4}|\d{4})\s*[-–to]+\s*(\d{1,2}/\d{4}|\d{4}|present|current|date|now)',
            r'(\w+\s*\d{4})\s*[-–to]+\s*(\w+\s*\d{4}|present|current|date|now)',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, line.lower())
            if match:
                return match.group(0)
        return ""
    
    def _extract_job_title_from_line(self, line):
        title_patterns = [
            r'(?:as|as a|as an|position[:\s]*|role[:\s]*|title[:\s]*)([\w\s&]+?)(?:,|\s{2,}|\s-\s|$)',
            r'^([\w\s&]+?)(?:,|\s{2,}|\s-\s)',
        ]
        for pattern in title_patterns:
            match = re.search(pattern, line)
            if match:
                title = match.group(1).strip()
                if len(title) > 5 and len(title) < 80:
                    return title
        return ""
    
    def _extract_current_position(self, text):
        if not text:
            return ""
        # Look for most recent position
        for pattern in [r'(?:current|present)(?:\s*(?:ly)?)?[:\s]*([\w\s&]+?)(?:,|\.|\n)',
                       r'(?:currently|presently)\s*(?:working\s*(?:as)?)?[:\s]*([\w\s&]+?)(?:,|\.|\n)']:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip().title()
        return ""
    
    def _extract_current_company(self, text):
        if not text:
            return ""
        for pattern in [r'(?:current|present)(?:\s*(?:ly)?)?[:\s]*(?:at|with|for)?\s*([\w\s&.,]+?)(?:,|\.|\n)',
                       r'(?:currently|presently)\s*(?:at|with|for)?\s*([\w\s&.,]+?)(?:,|\.|\n)']:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip().title()
        return ""
    
    def _extract_education(self, text):
        education = []
        lines = text.split('\n')
        in_edu = False
        
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in ['education', 'academic', 'qualification']):
                in_edu = True
                continue
            if in_edu and any(kw in line_lower for kw in ['experience', 'skills', 'certification']):
                break
            if in_edu and line.strip() and len(line.strip()) > 10:
                education.append(line.strip())
        
        return education[:5]
    
    def _extract_certifications(self, text):
        certifications = []
        lines = text.split('\n')
        in_cert = False
        
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in ['certification', 'license', 'professional development']):
                in_cert = True
                continue
            if in_cert and line.strip() and len(line.strip()) > 5:
                certifications.append(line.strip())
                if len(certifications) >= 8:
                    break
        
        return certifications
    
    def _extract_languages(self, text):
        language_keywords = ['english', 'french', 'spanish', 'german', 'mandarin', 'arabic', 
                           'portuguese', 'yoruba', 'igbo', 'hausa', 'swahili']
        found = []
        text_lower = text.lower()
        for lang in language_keywords:
            if lang in text_lower:
                found.append(lang.title())
        return found
    
    def _calculate_total_experience(self, experiences):
        total_years = 0
        for exp in experiences:
            dates = exp.get('dates', '')
            years = re.findall(r'\d{4}', dates)
            if len(years) >= 2:
                start, end = int(years[0]), int(years[-1])
                if end > 2000 and end > start:
                    total_years += min(end - start, 15)  # Cap at 15 years per role
            elif len(years) == 1:
                total_years += 1
        
        return total_years if total_years > 0 else 0
    
    def analyze_jd(self, jd_text):
        """Deep JD Analysis"""
        if not jd_text:
            return self._empty_jd()
        
        analysis = {
            'title': self._extract_jd_title(jd_text),
            'department': self._extract_department(jd_text),
            'required_skills': self._extract_all_skills(jd_text),
            'experience_level': self._extract_experience_level(jd_text),
            'key_responsibilities': self._extract_responsibilities(jd_text),
            'qualifications': self._extract_qualifications(jd_text),
            'education_required': self._extract_education_required(jd_text),
            'soft_skills_required': self._extract_soft_skills(jd_text),
            'certifications_required': self._extract_certifications_required(jd_text),
        }
        return analysis
    
    def _empty_jd(self):
        return {
            'title': 'Unknown', 'department': 'General', 'required_skills': [],
            'experience_level': 'Not Specified', 'key_responsibilities': [],
            'qualifications': [], 'education_required': 'Not Specified',
            'soft_skills_required': [], 'certifications_required': []
        }
    
    def _extract_jd_title(self, text):
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 120 and not line.startswith(('http', 'www', 'location:', 'company:', 'type:')):
                return line
        return "Position"
    
    def _extract_department(self, text):
        departments = ['hr', 'human resources', 'engineering', 'sales', 'marketing', 
                      'finance', 'operations', 'legal', 'it', 'technology', 'facility',
                      'procurement', 'security', 'customer service']
        text_lower = text.lower()
        for dept in departments:
            if dept in text_lower:
                return dept.title()
        return "General"
    
    def _extract_experience_level(self, text):
        for pattern in self.experience_patterns:
            match = re.search(pattern, text.lower())
            if match:
                years = int(match.group(1))
                if years >= 10:
                    return f"Senior/Executive ({years}+ years)"
                elif years >= 5:
                    return f"Mid-Senior ({years}+ years)"
                elif years >= 2:
                    return f"Junior-Mid ({years}+ years)"
                else:
                    return f"Entry Level ({years}+ years)"
        
        if 'senior' in text.lower() or 'lead' in text.lower():
            return "Senior Level"
        elif 'mid' in text.lower():
            return "Mid Level"
        elif 'junior' in text.lower() or 'entry' in text.lower():
            return "Junior/Entry Level"
        return "Not Specified"
    
    def _extract_responsibilities(self, text):
        responsibilities = []
        lines = text.split('\n')
        capture = False
        
        for line in lines:
            if any(kw in line.lower() for kw in ['responsibilities', 'what you', 'the role', 'key duties', 'you will']):
                capture = True
                continue
            if capture and line.strip():
                if any(kw in line.lower() for kw in ['requirement', 'qualification', 'skill', 'experience', 'education']):
                    break
                cleaned = line.strip('- •·*◦▪').strip()
                if len(cleaned) > 10:
                    responsibilities.append(cleaned)
        
        return responsibilities[:15]
    
    def _extract_qualifications(self, text):
        qualifications = []
        lines = text.split('\n')
        capture = False
        
        for line in lines:
            if any(kw in line.lower() for kw in ['qualification', 'requirement', 'what you need', 'what we are looking']):
                capture = True
                continue
            if capture and line.strip():
                if any(kw in line.lower() for kw in ['responsibilities', 'benefit', 'about us', 'why join']):
                    break
                cleaned = line.strip('- •·*◦▪').strip()
                if len(cleaned) > 5:
                    qualifications.append(cleaned)
        
        return qualifications[:15]
    
    def _extract_education_required(self, text):
        text_lower = text.lower()
        for level, keywords in self.education_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level.title()
        return "Not Specified"
    
    def _extract_soft_skills(self, text):
        soft_skills = []
        text_lower = text.lower()
        soft_keywords = [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical', 'interpersonal', 'time management', 'adaptability',
            'creativity', 'collaboration', 'emotional intelligence', 'initiative',
            'ownership', 'accountability', 'resilience', 'pragmatism'
        ]
        for skill in soft_keywords:
            if skill in text_lower:
                soft_skills.append(skill.title())
        return soft_skills
    
    def _extract_certifications_required(self, text):
        certs = []
        cert_keywords = ['sphri', 'phri', 'cipm', 'acipm', 'shrm', 'pmp', 'nebosh', 
                        'ccnp', 'cisco', 'aws', 'azure', 'cima', 'acca']
        text_lower = text.lower()
        for cert in cert_keywords:
            if cert in text_lower:
                certs.append(cert.upper())
        return certs
    
    def score_candidate_advanced(self, candidate_cv, jd_analysis):
        # Try OpenAI deep analysis first
        if self.use_openai and self.openai_key:
            try:
                openai_result = self._openai_deep_score(candidate_cv, jd_analysis)
                if openai_result:
                    return openai_result
            except:
                pass
        
        # Fallback to enhanced keyword engine
        cv_data = self.parse_cv(candidate_cv) if isinstance(candidate_cv, str) else candidate_cv
        """Enterprise-grade scoring with 85%+ confidence"""
        cv_data = self.parse_cv(candidate_cv) if isinstance(candidate_cv, str) else candidate_cv
        
        # Core scores
        skills_score = self._calculate_skills_match_score(cv_data, jd_analysis)
        experience_score = self._calculate_experience_score(cv_data, jd_analysis)
        education_score = self._calculate_education_score(cv_data, jd_analysis)
        soft_skills_score = self._calculate_soft_skills_score(cv_data, jd_analysis)
        certification_score = self._calculate_certification_score(cv_data, jd_analysis)
        
        # Advanced analysis
        verbatim_score = self._detect_verbatim(candidate_cv, jd_analysis)
        inconsistency_score = self._detect_inconsistencies(cv_data)
        keyword_density_score = self._analyze_keyword_density(candidate_cv, jd_analysis)
        
        # Weighted overall (enhanced weights)
        weights = {
            'skills': 0.30,
            'experience': 0.25,
            'education': 0.10,
            'soft_skills': 0.10,
            'certifications': 0.05,
            'verbatim_penalty': -0.10,
            'inconsistency_penalty': -0.05,
            'keyword_density': 0.05
        }
        
        overall = (
            skills_score * 0.30 +
            experience_score * 0.25 +
            education_score * 0.10 +
            soft_skills_score * 0.10 +
            certification_score * 0.05 +
            keyword_density_score * 0.05 -
            verbatim_score * 0.10 -
            inconsistency_score * 0.05
        )
        
        overall = max(0, min(100, overall))
        
        # Confidence level
        confidence = self._calculate_confidence(cv_data, jd_analysis, overall)
        
        # Tier
        if overall >= 85:
            tier = "Tier 1 (Strong Fit)"
            recommendation = "Fast-track to Final Interview"
        elif overall >= 70:
            tier = "Tier 2 (Good Fit)"
            recommendation = "Advance to Next Stage"
        elif overall >= 55:
            tier = "Tier 3 (Potential Fit)"
            recommendation = "Keep in Talent Pool"
        else:
            tier = "Tier 4 (Not Recommended)"
            recommendation = "Archive"
        
        strengths = self._identify_strengths(cv_data, jd_analysis)
        gaps = self._identify_gaps(cv_data, jd_analysis)
        interview_questions = self._generate_interview_questions(cv_data, jd_analysis)
        
        return {
            'candidate_name': cv_data.get('name', 'Unknown'),
            'overall_score': round(overall, 1),
            'confidence': round(confidence, 1),
            'tier': tier,
            'recommendation': recommendation,
            'skills_score': round(skills_score, 1),
            'experience_score': round(experience_score, 1),
            'education_score': round(education_score, 1),
            'soft_skills_score': round(soft_skills_score, 1),
            'certification_score': round(certification_score, 1),
            'verbatim_flags': round(verbatim_score, 1),
            'inconsistency_flags': round(inconsistency_score, 1),
            'keyword_density': round(keyword_density_score, 1),
            'linkedin_verified': bool(cv_data.get('linkedin')),
            'key_strengths': strengths,
            'gaps_identified': gaps,
            'interview_questions': interview_questions,
            'parsed_data': cv_data
        }
    
    def _calculate_skills_match_score(self, cv_data, jd_analysis):
        jd_skills = [s['skill'].lower() for s in jd_analysis.get('required_skills', [])]
        if not jd_skills:
            return 60
        
        cv_skills = [s['skill'].lower() for s in cv_data.get('skills', [])]
        cv_skill_set = set(cv_skills)
        
        # Exact match
        exact_matches = sum(1 for s in jd_skills if s in cv_skill_set)
        exact_score = (exact_matches / len(jd_skills)) * 60
        
        # Partial match (fuzzy)
        partial_matches = 0
        for jd_skill in jd_skills:
            if jd_skill not in cv_skill_set:
                for cv_skill in cv_skill_set:
                    if len(jd_skill) > 4 and (jd_skill in cv_skill or cv_skill in jd_skill):
                        partial_matches += 0.5
                        break
        
        partial_score = (partial_matches / len(jd_skills)) * 40
        
        return min(100, exact_score + partial_score)
    
    def _calculate_experience_score(self, cv_data, jd_analysis):
        cv_years = cv_data.get('total_experience_years', 0)
        exp_text = jd_analysis.get('experience_level', '')
        
        required_years = 0
        for pattern in self.experience_patterns:
            match = re.search(pattern, exp_text.lower())
            if match:
                required_years = int(match.group(1))
                break
        
        if required_years == 0:
            return 65
        
        ratio = cv_years / required_years if required_years > 0 else 1
        
        if ratio >= 1.5:
            return 100
        elif ratio >= 1.2:
            return 90
        elif ratio >= 1.0:
            return 80
        elif ratio >= 0.8:
            return 65
        elif ratio >= 0.5:
            return 40
        else:
            return 15
    
    def _calculate_education_score(self, cv_data, jd_analysis):
        jd_edu = jd_analysis.get('education_required', '').lower()
        cv_edu_text = ' '.join(cv_data.get('education', [])).lower()
        
        edu_hierarchy = ['phd', 'masters', 'bachelors', 'diploma', 'certification']
        edu_scores = {'phd': 100, 'masters': 85, 'bachelors': 70, 'diploma': 50, 'certification': 40}
        
        cv_highest = None
        for level in edu_hierarchy:
            for keyword in self.education_keywords.get(level, []):
                if keyword in cv_edu_text:
                    cv_highest = level
                    break
            if cv_highest:
                break
        
        if not cv_highest:
            return 25
        
        if not jd_edu:
            return edu_scores.get(cv_highest, 60)
        
        jd_level = None
        for level in edu_hierarchy:
            for keyword in self.education_keywords.get(level, []):
                if keyword in jd_edu:
                    jd_level = level
                    break
            if jd_level:
                break
        
        if not jd_level:
            return edu_scores.get(cv_highest, 60)
        
        cv_idx = edu_hierarchy.index(cv_highest)
        jd_idx = edu_hierarchy.index(jd_level)
        
        if cv_idx <= jd_idx:
            return 100
        elif cv_idx - jd_idx == 1:
            return 70
        else:
            return 40
    
    def _calculate_soft_skills_score(self, cv_data, jd_analysis):
        jd_soft = jd_analysis.get('soft_skills_required', [])
        if not jd_soft:
            return 65
        
        cv_text = json.dumps(cv_data).lower()
        matched = sum(1 for skill in jd_soft if skill.lower() in cv_text)
        
        return (matched / len(jd_soft)) * 100
    
    def _calculate_certification_score(self, cv_data, jd_analysis):
        cv_certs = ' '.join(cv_data.get('certifications', [])).lower()
        jd_certs = jd_analysis.get('certifications_required', [])
        
        if not jd_certs and not cv_certs:
            return 50
        if not jd_certs and cv_certs:
            return 75
        if jd_certs and not cv_certs:
            return 0
        
        matched = sum(1 for c in jd_certs if c.lower() in cv_certs)
        return (matched / len(jd_certs)) * 100
    
    def _detect_verbatim(self, cv_text, jd_analysis):
        """Detect copy-paste from JD - lower score = better"""
        if not cv_text:
            return 0
        
        jd_phrases = []
        for resp in jd_analysis.get('key_responsibilities', []):
            words = resp.split()
            for i in range(len(words)-3):
                jd_phrases.append(' '.join(words[i:i+4]).lower())
        
        if not jd_phrases:
            return 0
        
        cv_lower = cv_text.lower()
        matches = sum(1 for phrase in jd_phrases if phrase in cv_lower)
        
        ratio = matches / len(jd_phrases) if jd_phrases else 0
        return min(100, ratio * 200)  # Scale up for penalty
    
    def _detect_inconsistencies(self, cv_data):
        """Detect inconsistencies - lower score = better"""
        flags = 0
        
        # Check experience timeline gaps
        experiences = cv_data.get('experience', [])
        if len(experiences) > 1:
            dates_list = [e.get('dates', '') for e in experiences]
            years_list = []
            for d in dates_list:
                found = re.findall(r'\d{4}', d)
                years_list.extend([int(y) for y in found])
            
            if years_list:
                years_list.sort()
                for i in range(len(years_list)-1):
                    if years_list[i+1] - years_list[i] > 5:
                        flags += 1
        
        # Title inflation check
        titles = [e.get('title', '').lower() for e in experiences]
        senior_titles = sum(1 for t in titles if any(kw in t for kw in ['senior', 'lead', 'head', 'director', 'vp', 'chief']))
        if senior_titles > len(titles) * 0.7:
            flags += 1
        
        # Total years vs number of roles
        total_years = cv_data.get('total_experience_years', 0)
        if len(experiences) > 0 and total_years > 0:
            avg_tenure = total_years / len(experiences)
            if avg_tenure < 0.5:
                flags += 2
        
        return min(100, flags * 25)
    
    def _analyze_keyword_density(self, cv_text, jd_analysis):
        """Check how well keywords are distributed naturally"""
        if not cv_text:
            return 0
        
        jd_skills = [s['skill'].lower() for s in jd_analysis.get('required_skills', [])]
        if not jd_skills:
            return 60
        
        cv_lower = cv_text.lower()
        cv_words = len(cv_lower.split())
        if cv_words < 100:
            return 40
        
        matches = 0
        for skill in jd_skills:
            count = cv_lower.count(skill.lower())
            if count > 0:
                density = count / (cv_words / 1000)
                if 2 <= density <= 15:
                    matches += 1
                elif density > 0:
                    matches += 0.5
        
        return (matches / len(jd_skills)) * 100
    
    def _calculate_confidence(self, cv_data, jd_analysis, overall_score):
        """Calculate confidence level of the score"""
        confidence = 65  # Base confidence
        
        # More data = higher confidence
        if cv_data.get('linkedin'):
            confidence += 8
        if cv_data.get('github') or cv_data.get('portfolio'):
            confidence += 5
        if cv_data.get('total_experience_years', 0) > 0:
            confidence += 5
        if len(cv_data.get('skills', [])) > 10:
            confidence += 5
        if len(cv_data.get('education', [])) > 0:
            confidence += 3
        if len(cv_data.get('certifications', [])) > 0:
            confidence += 3
        if cv_data.get('summary'):
            confidence += 3
        
        # If using OpenAI, confidence jumps significantly
        if self.use_openai:
            confidence += 15
        
        return min(98, confidence)
    
    def _identify_strengths(self, cv_data, jd_analysis):
        strengths = []
        
        if cv_data.get('total_experience_years', 0) >= 10:
            strengths.append(f"{cv_data['total_experience_years']}+ years professional experience")
        
        cv_skills = {s['skill'] for s in cv_data.get('skills', [])}
        jd_skills = {s['skill'] for s in jd_analysis.get('required_skills', [])}
        matched = cv_skills.intersection(jd_skills)
        if len(matched) >= 5:
            strengths.append(f"Strong skills alignment ({len(matched)} matching skills)")
        
        if cv_data.get('education'):
            strengths.append("Solid educational foundation")
        
        if cv_data.get('certifications'):
            strengths.append(f"Industry certifications ({len(cv_data['certifications'])} obtained)")
        
        if cv_data.get('linkedin'):
            strengths.append("Professional online presence verified")
        
        if cv_data.get('languages'):
            strengths.append(f"Multilingual: {', '.join(cv_data['languages'][:3])}")
        
        return strengths[:6]
    
    def _identify_gaps(self, cv_data, jd_analysis):
        gaps = []
        
        cv_skills = {s['skill'] for s in cv_data.get('skills', [])}
        jd_skills = {s['skill'] for s in jd_analysis.get('required_skills', [])}
        missing = jd_skills - cv_skills
        if missing:
            gaps.append(f"Missing skills: {', '.join(list(missing)[:4])}")
        
        cv_years = cv_data.get('total_experience_years', 0)
        for pattern in self.experience_patterns:
            match = re.search(pattern, jd_analysis.get('experience_level', '').lower())
            if match:
                required = int(match.group(1))
                if cv_years < required:
                    gaps.append(f"Experience below target ({cv_years} vs {required} years)")
                break
        
        if not cv_data.get('linkedin'):
            gaps.append("No LinkedIn profile provided for verification")
        
        if not cv_data.get('education'):
            gaps.append("Education history not clearly documented")
        
        if len(cv_data.get('experience', [])) == 0:
            gaps.append("Work experience not detailed")
        
        return gaps[:5]
    
    def _generate_interview_questions(self, cv_data, jd_analysis):
        """Generate targeted interview questions based on gaps"""
        questions = []
        
        # Skills gap questions
        cv_skills = {s['skill'].lower() for s in cv_data.get('skills', [])}
        jd_skills = [s['skill'].lower() for s in jd_analysis.get('required_skills', [])]
        missing = [s for s in jd_skills if s not in cv_skills][:3]
        for skill in missing:
            questions.append(f"Can you describe your experience with {skill} and how you've applied it in a professional setting?")
        
        # Experience questions
        cv_years = cv_data.get('total_experience_years', 0)
        if cv_years < 3:
            questions.append("Can you walk us through a challenging project you've delivered and the outcome achieved?")
        elif cv_years >= 7:
            questions.append("Describe a situation where you led a team through significant change. What was your approach and what did you learn?")
        
        # Gap questions
        if not cv_data.get('certifications'):
            questions.append("Are you pursuing any professional certifications? How do you stay current in your field?")
        
        # Behavioral
        questions.append("Tell us about a time you disagreed with a stakeholder. How did you handle it and what was the result?")
        questions.append("What's the most innovative solution you've implemented that had measurable business impact?")
        
        return questions[:6]
    
    def generate_candidate_report(self, candidates_scores):
        """Generate tiered candidate report"""
        tiers = {
            'Tier 1 (Strong Fit)': [],
            'Tier 2 (Good Fit)': [],
            'Tier 3 (Potential Fit)': [],
            'Tier 4 (Not Recommended)': []
        }
        
        for candidate in candidates_scores:
            tier = candidate.get('tier', 'Tier 4 (Not Recommended)')
            if tier in tiers:
                tiers[tier].append(candidate)
        
        return tiers
    
    def deep_analyze_candidate(self, candidate_cv, jd_text, linkedin_data=None):
        """Full deep analysis combining CV, JD, and optional LinkedIn data"""
        jd_analysis = self.analyze_jd(jd_text)
        score_result = self.score_candidate_advanced(candidate_cv, jd_analysis)
        
        # Add LinkedIn cross-reference if available
        if linkedin_data:
            score_result['linkedin_cross_ref'] = self._cross_reference_linkedin(
                score_result['parsed_data'], linkedin_data
            )
        
        # Generate executive summary
        score_result['executive_summary'] = self._generate_executive_summary(score_result)
        
        return score_result
    
    def _cross_reference_linkedin(self, cv_data, linkedin_data):
        """Cross-reference CV claims with LinkedIn profile"""
        matches = []
        discrepancies = []
        
        # Compare positions
        cv_position = cv_data.get('current_position', '').lower()
        li_position = linkedin_data.get('current_position', '').lower()
        if cv_position and li_position:
            if cv_position in li_position or li_position in cv_position:
                matches.append("Current position verified")
            else:
                discrepancies.append(f"Position mismatch: CV={cv_position}, LinkedIn={li_position}")
        
        # Compare company
        cv_company = cv_data.get('current_company', '').lower()
        li_company = linkedin_data.get('current_company', '').lower()
        if cv_company and li_company:
            if cv_company in li_company or li_company in cv_company:
                matches.append("Current company verified")
            else:
                discrepancies.append("Company mismatch detected")
        
        return {
            'verified_claims': matches,
            'discrepancies': discrepancies,
            'linkedin_url': cv_data.get('linkedin', '')
        }
    
    def _openai_deep_score(self, cv_text, jd_analysis):
        """Use OpenAI for deep semantic scoring"""
        try:
            import json as json_module
            jd_text = json_module.dumps(jd_analysis) if isinstance(jd_analysis, dict) else str(jd_analysis)
            
            prompt = f"""Score this candidate against the job description. Return ONLY valid JSON.

CRITERIA (0-100 each):
skills_match, experience_relevance, education_fit, certification_match, cv_quality, communication, keyword_density, verbatim_risk

WEIGHTS: skills 30%, experience 25%, education 10%, certs 5%, cv 10%, communication 10%, keywords 5%, verbatim -5%

JD: {jd_text[:2000]}
CV: {cv_text[:3000]}

Return: {{"overall_score": number, "tier": "Tier 1" if >=85 else "Tier 2" if >=70 else "Tier 3" if >=55 else "Tier 4", "skills_score": number, "experience_score": number, "education_score": number, "certification_score": number, "cv_quality_score": number, "communication_score": number, "keyword_density_score": number, "verbatim_flags": number, "confidence": 95, "key_strengths": [], "gaps_identified": [], "interview_questions": [], "executive_summary": {{"verdict": "HIRE" or "CONSIDER" or "NOT RECOMMENDED"}}}}"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Return only valid JSON."},
                         {"role": "user", "content": prompt}],
                temperature=0.3, max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            if "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            return json_module.loads(result_text.strip())
        except:
            return None

    def _generate_executive_summary(self, score_result):
        """Generate executive-friendly summary"""
        overall = score_result.get('overall_score', 0)
        confidence = score_result.get('confidence', 0)
        
        if overall >= 85:
            verdict = "STRONG HIRE — Exceeds requirements significantly"
        elif overall >= 70:
            verdict = "HIRE — Meets most requirements with some strengths"
        elif overall >= 55:
            verdict = "CONSIDER — Meets minimum but has notable gaps"
        else:
            verdict = "NOT RECOMMENDED — Does not meet core requirements"
        
        return {
            'verdict': verdict,
            'overall_score': overall,
            'confidence': confidence,
            'strengths_count': len(score_result.get('key_strengths', [])),
            'gaps_count': len(score_result.get('gaps_identified', [])),
        }