import re
import json
import math
from datetime import datetime
from collections import Counter

class AIRecruitmentAgent:
    """
    Advanced AI Recruitment Agent with CV parsing, scoring, and tiering
    """
    
    def __init__(self):
        self.skill_keywords = self._load_skill_database()
        self.education_keywords = self._load_education_keywords()
        self.experience_patterns = self._load_experience_patterns()
        
    def _load_skill_database(self):
        return {
            'technical': {
                'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby'],
                'web': ['react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'spring', 'laravel'],
                'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd'],
                'data': ['sql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'spark', 'hadoop', 'tableau'],
                'mobile': ['android', 'ios', 'flutter', 'react native', 'swift', 'kotlin'],
            },
            'business': {
                'management': ['project management', 'agile', 'scrum', 'kanban', 'jira', 'confluence'],
                'analysis': ['business analysis', 'data analysis', 'financial modeling', 'market research'],
                'strategy': ['strategic planning', 'business strategy', 'digital transformation', 'change management'],
            },
            'hr_specific': {
                'hris': ['hris', 'sap', 'oracle hcm', 'workday', 'bamboo', 'people management'],
                'talent': ['talent acquisition', 'recruitment', 'sourcing', 'employer branding', 'onboarding'],
                'performance': ['performance management', 'okrs', 'kpis', '360 feedback', 'appraisal'],
                'compensation': ['compensation', 'benefits', 'payroll', 'salary structure', 'grading'],
                'training': ['l&d', 'training', 'development', 'succession planning', 'career development'],
                'compliance': ['labor law', 'compliance', 'policy', 'employee relations', 'disciplinary'],
            },
            'soft_skills': {
                'leadership': ['leadership', 'team management', 'mentoring', 'coaching', 'delegation'],
                'communication': ['communication', 'presentation', 'negotiation', 'stakeholder management'],
                'analytical': ['problem solving', 'analytical', 'critical thinking', 'decision making'],
            }
        }
    
    def _load_education_keywords(self):
        return {
            'phd': ['phd', 'doctorate', 'ph.d', 'dba'],
            'masters': ['master', 'msc', 'ma', 'mba', 'm.sc', 'm.a', 'mphil'],
            'bachelors': ['bachelor', 'bsc', 'ba', 'b.sc', 'b.a', 'b.eng', 'b.tech'],
            'diploma': ['diploma', 'hnd', 'ond', 'certificate'],
            'certification': ['sphri', 'cipm', 'acipm', 'phri', 'shrm', 'pmp', 'cima', 'acca'],
        }
    
    def _load_experience_patterns(self):
        return [
            r'(\d+)[\+]*\s*years?\s*(?:of)?\s*(?:relevant)?\s*experience',
            r'experience[:\s]*(\d+)[\+]*\s*years?',
            r'(\d+)\+?\s*years?\s*(?:in|within)\s*(?:the)?\s*(?:field|industry|role)',
        ]
    
    def parse_cv(self, cv_text):
        """
        Advanced CV parsing to extract structured information
        """
        parsed = {
            'name': self._extract_name(cv_text),
            'email': self._extract_email(cv_text),
            'phone': self._extract_phone(cv_text),
            'linkedin': self._extract_linkedin(cv_text),
            'summary': self._extract_summary(cv_text),
            'skills': self._extract_all_skills(cv_text),
            'experience': self._extract_experience_details(cv_text),
            'education': self._extract_education(cv_text),
            'certifications': self._extract_certifications(cv_text),
            'languages': self._extract_languages(cv_text),
            'total_experience_years': 0,
        }
        
        parsed['total_experience_years'] = self._calculate_total_experience(parsed['experience'])
        
        return parsed
    
    def _extract_name(self, text):
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['email', 'phone', 'address', 'linkedin', 'summary', 'objective', 'curriculum', 'resume', 'cv']):
                if len(line.split()) >= 2 and len(line) < 50:
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
            r'\d{11}',
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
    
    def _extract_summary(self, text):
        summary_keywords = ['summary', 'profile', 'objective', 'about me']
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in summary_keywords):
                summary_lines = []
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                    else:
                        break
                return ' '.join(summary_lines)
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
        
        return found_skills
    
    def _extract_experience_details(self, text):
        experiences = []
        exp_section = False
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['experience', 'employment', 'work history']):
                exp_section = True
                continue
            if exp_section and any(keyword in line.lower() for keyword in ['education', 'skills', 'certification']):
                break
            if exp_section and line.strip():
                # Try to extract company and role
                company_match = re.search(r'(?:at|with)\s+([A-Z][\w\s&.,]+)', line)
                date_match = re.search(r'(\d{4})\s*[-–to]+\s*(\d{4}|present|current|date)', line.lower())
                
                if company_match or date_match:
                    experiences.append({
                        'line': line.strip(),
                        'company': company_match.group(1) if company_match else "",
                        'dates': date_match.group(0) if date_match else "",
                    })
        
        return experiences
    
    def _extract_education(self, text):
        education = []
        edu_section = False
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['education', 'academic', 'qualification']):
                edu_section = True
                continue
            if edu_section and any(keyword in line.lower() for keyword in ['experience', 'skills', 'certification']):
                break
            if edu_section and line.strip() and len(line) > 10:
                education.append(line.strip())
        
        return education[:5]
    
    def _extract_certifications(self, text):
        certifications = []
        cert_section = False
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['certification', 'license', 'professional']):
                cert_section = True
                continue
            if cert_section and line.strip() and len(line) > 5:
                certifications.append(line.strip())
                if len(certifications) >= 5:
                    break
        
        return certifications
    
    def _extract_languages(self, text):
        language_keywords = ['english', 'french', 'spanish', 'german', 'mandarin', 'arabic', 
                           'portuguese', 'yoruba', 'igbo', 'hausa', 'swahili']
        found_languages = []
        text_lower = text.lower()
        
        for lang in language_keywords:
            if lang in text_lower:
                found_languages.append(lang.title())
        
        return found_languages
    
    def _calculate_total_experience(self, experiences):
        total_years = 0
        for exp in experiences:
            dates = exp.get('dates', '')
            years = re.findall(r'\d{4}', dates)
            if len(years) >= 2:
                start, end = int(years[0]), int(years[-1])
                if end > 2000:  # Valid year
                    total_years += (end - start)
            elif len(years) == 1:
                total_years += 1  # Assume at least 1 year
        
        return total_years if total_years > 0 else 0
    
    def analyze_jd(self, jd_text):
        """Enhanced JD Analysis"""
        analysis = {
            'title': self._extract_jd_title(jd_text),
            'department': self._extract_department(jd_text),
            'required_skills': self._extract_all_skills(jd_text),
            'experience_level': self._extract_experience_level(jd_text),
            'key_responsibilities': self._extract_responsibilities(jd_text),
            'qualifications': self._extract_qualifications(jd_text),
            'education_required': self._extract_education_required(jd_text),
            'soft_skills_required': self._extract_soft_skills(jd_text),
        }
        return analysis
    
    def _extract_jd_title(self, text):
        lines = text.strip().split('\n')
        for line in lines[:3]:
            line = line.strip()
            if line and len(line) < 100 and not line.startswith('http'):
                return line
        return "Position"
    
    def _extract_department(self, text):
        departments = ['hr', 'human resources', 'engineering', 'sales', 'marketing', 
                      'finance', 'operations', 'legal', 'it', 'customer service']
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
        
        if 'senior' in text.lower():
            return "Senior Level"
        elif 'mid' in text.lower():
            return "Mid Level"
        elif 'junior' in text.lower():
            return "Junior Level"
        return "Not Specified"
    
    def _extract_responsibilities(self, text):
        responsibilities = []
        lines = text.split('\n')
        capture = False
        
        for line in lines:
            if any(kw in line.lower() for kw in ['responsibilities', 'what you', 'the role', 'key duties']):
                capture = True
                continue
            if capture and line.strip():
                if any(kw in line.lower() for kw in ['requirement', 'qualification', 'skill', 'experience']):
                    break
                cleaned = line.strip('- •·*').strip()
                if len(cleaned) > 10:
                    responsibilities.append(cleaned)
        
        return responsibilities[:10]
    
    def _extract_qualifications(self, text):
        qualifications = []
        lines = text.split('\n')
        capture = False
        
        for line in lines:
            if any(kw in line.lower() for kw in ['qualification', 'requirement', 'what you need']):
                capture = True
                continue
            if capture and line.strip():
                if any(kw in line.lower() for kw in ['responsibilities', 'benefit', 'about us']):
                    break
                cleaned = line.strip('- •·*').strip()
                if len(cleaned) > 5:
                    qualifications.append(cleaned)
        
        return qualifications[:10]
    
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
        
        soft_skill_keywords = [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical', 'interpersonal', 'time management', 'adaptability',
            'creativity', 'collaboration', 'emotional intelligence'
        ]
        
        for skill in soft_skill_keywords:
            if skill in text_lower:
                soft_skills.append(skill.title())
        
        return soft_skills
    
    def score_candidate_advanced(self, candidate_cv, jd_analysis):
        """
        Advanced candidate scoring with detailed breakdown and tiering
        """
        # Parse CV
        cv_data = self.parse_cv(candidate_cv)
        
        # Calculate individual scores
        skills_score = self._calculate_skills_match_score(cv_data, jd_analysis)
        experience_score = self._calculate_experience_score(cv_data, jd_analysis)
        education_score = self._calculate_education_score(cv_data, jd_analysis)
        soft_skills_score = self._calculate_soft_skills_score(cv_data, jd_analysis)
        certification_score = self._calculate_certification_score(cv_data, jd_analysis)
        
        # Weighted overall score
        weights = {
            'skills': 0.35,
            'experience': 0.30,
            'education': 0.15,
            'soft_skills': 0.10,
            'certifications': 0.10
        }
        
        overall_score = (
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            soft_skills_score * weights['soft_skills'] +
            certification_score * weights['certifications']
        )
        
        # Determine tier
        if overall_score >= 85:
            tier = "Tier 1 (Strong Fit)"
            recommendation = "Recommend for Final Stage Interview"
        elif overall_score >= 65:
            tier = "Tier 2 (Good Fit)"
            recommendation = "Keep in View"
        else:
            tier = "Tier 3 (Not Recommended)"
            recommendation = "Not Recommended"
        
        # Identify strengths and gaps
        strengths = self._identify_strengths(cv_data, jd_analysis)
        gaps = self._identify_gaps(cv_data, jd_analysis)
        
        # Check LinkedIn
        linkedin_verified = bool(cv_data.get('linkedin'))
        
        return {
            'candidate_name': cv_data.get('name', 'Unknown'),
            'overall_score': round(overall_score, 1),
            'tier': tier,
            'recommendation': recommendation,
            'skills_score': round(skills_score, 1),
            'experience_score': round(experience_score, 1),
            'education_score': round(education_score, 1),
            'soft_skills_score': round(soft_skills_score, 1),
            'certification_score': round(certification_score, 1),
            'linkedin_verified': linkedin_verified,
            'key_strengths': strengths,
            'gaps_identified': gaps,
            'parsed_data': cv_data
        }
    
    def _calculate_skills_match_score(self, cv_data, jd_analysis):
        if not jd_analysis.get('required_skills'):
            return 50
        
        cv_skills = [s['skill'].lower() for s in cv_data.get('skills', [])]
        jd_skills = [s['skill'].lower() for s in jd_analysis['required_skills']]
        
        if not jd_skills:
            return 50
        
        matched = sum(1 for skill in jd_skills if skill in cv_skills)
        return (matched / len(jd_skills)) * 100
    
    def _calculate_experience_score(self, cv_data, jd_analysis):
        cv_years = cv_data.get('total_experience_years', 0)
        exp_text = jd_analysis.get('experience_level', '')
        
        # Extract required years from JD
        required_years = 0
        for pattern in self.experience_patterns:
            match = re.search(pattern, exp_text.lower())
            if match:
                required_years = int(match.group(1))
                break
        
        if required_years == 0:
            return 70  # Default if not specified
        
        if cv_years >= required_years * 1.5:
            return 100
        elif cv_years >= required_years:
            return 85
        elif cv_years >= required_years * 0.7:
            return 65
        elif cv_years >= required_years * 0.5:
            return 40
        else:
            return 20
    
    def _calculate_education_score(self, cv_data, jd_analysis):
        jd_edu = jd_analysis.get('education_required', '').lower()
        cv_edu_text = ' '.join(cv_data.get('education', [])).lower()
        
        edu_levels = {
            'phd': 100,
            'masters': 85,
            'bachelors': 70,
            'diploma': 50,
            'certification': 40
        }
        
        # Check candidate's highest education
        for level, score in edu_levels.items():
            for keyword in self.education_keywords.get(level, []):
                if keyword in cv_edu_text:
                    # If JD doesn't specify education, return this score
                    if not jd_edu:
                        return score
                    # Check if education matches JD requirement
                    if level in jd_edu or any(kw in jd_edu for kw in self.education_keywords.get(level, [])):
                        return score
                    # If candidate has higher education than required
                    if level in ['phd', 'masters'] and jd_edu in ['bachelors', 'diploma']:
                        return 100
        
        return 30
    
    def _calculate_soft_skills_score(self, cv_data, jd_analysis):
        jd_soft_skills = jd_analysis.get('soft_skills_required', [])
        if not jd_soft_skills:
            return 70
        
        cv_text = json.dumps(cv_data).lower()
        matched = sum(1 for skill in jd_soft_skills if skill.lower() in cv_text)
        
        return (matched / len(jd_soft_skills)) * 100 if jd_soft_skills else 70
    
    def _calculate_certification_score(self, cv_data, jd_analysis):
        cv_certs = [c.lower() for c in cv_data.get('certifications', [])]
        
        # Look for HR certifications
        hr_certs = ['sphri', 'phri', 'cipm', 'acipm', 'shrm', 'gpHR']
        has_hr_cert = any(cert in ' '.join(cv_certs) for cert in hr_certs)
        
        # Look for relevant certifications mentioned in JD
        jd_text = json.dumps(jd_analysis).lower()
        relevant_certs = [cert for cert in cv_certs if any(word in jd_text for word in cert.split())]
        
        if has_hr_cert and relevant_certs:
            return 100
        elif has_hr_cert:
            return 85
        elif relevant_certs:
            return 70
        elif cv_certs:
            return 45
        else:
            return 0
    
    def _identify_strengths(self, cv_data, jd_analysis):
        strengths = []
        
        # Experience strength
        if cv_data.get('total_experience_years', 0) >= 10:
            strengths.append(f"{cv_data['total_experience_years']}+ years experience")
        
        # Skills match
        cv_skills = {s['skill'] for s in cv_data.get('skills', [])}
        jd_skills = {s['skill'] for s in jd_analysis.get('required_skills', [])}
        matched = cv_skills.intersection(jd_skills)
        if len(matched) >= 5:
            strengths.append(f"Strong skills match ({len(matched)} matching skills)")
        
        # Education
        if cv_data.get('education'):
            strengths.append("Relevant educational background")
        
        # Certifications
        if cv_data.get('certifications'):
            strengths.append(f"Professional certifications ({len(cv_data['certifications'])} certs)")
        
        # LinkedIn
        if cv_data.get('linkedin'):
            strengths.append("LinkedIn profile verified")
        
        return strengths[:5]
    
    def _identify_gaps(self, cv_data, jd_analysis):
        gaps = []
        
        # Missing skills
        cv_skills = {s['skill'] for s in cv_data.get('skills', [])}
        jd_skills = {s['skill'] for s in jd_analysis.get('required_skills', [])}
        missing = jd_skills - cv_skills
        if len(missing) > 0:
            gaps.append(f"Missing skills: {', '.join(list(missing)[:3])}")
        
        # Experience gap
        cv_years = cv_data.get('total_experience_years', 0)
        exp_text = jd_analysis.get('experience_level', '')
        for pattern in self.experience_patterns:
            match = re.search(pattern, exp_text.lower())
            if match:
                required = int(match.group(1))
                if cv_years < required:
                    gaps.append(f"Experience below required ({cv_years} vs {required} years)")
                break
        
        # LinkedIn missing
        if not cv_data.get('linkedin'):
            gaps.append("LinkedIn profile not provided")
        
        # Education gap
        if not cv_data.get('education'):
            gaps.append("Education details not clearly stated")
        
        return gaps[:4]
    
    def generate_candidate_report(self, candidates_scores):
        """
        Generate tiered report like the example format
        """
        tiers = {
            'Tier 1 (Strong Fit)': [],
            'Tier 2 (Good Fit)': [],
            'Tier 3 (Not Recommended)': []
        }
        
        for candidate in candidates_scores:
            tiers[candidate['tier']].append(candidate)
        
        return tiers