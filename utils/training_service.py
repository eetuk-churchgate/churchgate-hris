"""
Churchgate Group HRIS - Training & Development Service
Learning Management System Integration
"""

from datetime import datetime, timedelta
import json
import random

class TrainingService:
    def __init__(self):
        self.courses = self._initialize_courses()
        self.webinars = self._initialize_webinars()
        self.learning_paths = self._initialize_learning_paths()
        self.certifications = self._initialize_certifications()
    
    def _initialize_courses(self):
        """Initialize course catalog"""
        return [
            {
                'id': 'COURSE-001',
                'title': 'Building Management Systems - Advanced',
                'category': 'Technical',
                'department': ['ELV Systems', 'MEP', 'Operations'],
                'level': 'Advanced',
                'duration': '8 weeks',
                'format': 'Online',
                'provider': 'Siemens Academy',
                'description': 'Advanced BMS integration and automation for smart buildings',
                'objectives': [
                    'Master BMS architecture and protocols',
                    'Implement energy optimization strategies',
                    'Integrate IoT devices with BMS',
                    'Develop predictive maintenance systems'
                ],
                'status': 'Active'
            },
            {
                'id': 'COURSE-002',
                'title': 'AI in Facility Management',
                'category': 'Technology',
                'department': ['ELV Systems', 'IT', 'Operations'],
                'level': 'Intermediate',
                'duration': '6 weeks',
                'format': 'Hybrid',
                'provider': 'LinkedIn Learning',
                'description': 'Practical AI applications for modern facility management',
                'objectives': [
                    'Understand AI fundamentals for FM',
                    'Implement predictive analytics',
                    'Automate routine FM tasks',
                    'Use data for decision making'
                ],
                'status': 'Active'
            },
            {
                'id': 'COURSE-003',
                'title': 'Strategic HR Management',
                'category': 'Management',
                'department': ['HR', 'Admin'],
                'level': 'Advanced',
                'duration': '10 weeks',
                'format': 'In-Person',
                'provider': 'SHRM',
                'description': 'Strategic human resource management for organizational excellence',
                'objectives': [
                    'Develop HR strategy aligned with business goals',
                    'Implement talent management frameworks',
                    'Design compensation and benefits strategies',
                    'Lead organizational change initiatives'
                ],
                'status': 'Active'
            },
            {
                'id': 'COURSE-004',
                'title': 'Financial Modeling for Real Estate',
                'category': 'Finance',
                'department': ['Finance', 'Accounts'],
                'level': 'Advanced',
                'duration': '8 weeks',
                'format': 'Online',
                'provider': 'CFA Institute',
                'description': 'Advanced financial modeling techniques for real estate investments',
                'objectives': [
                    'Build comprehensive financial models',
                    'Analyze real estate investments',
                    'Perform sensitivity analysis',
                    'Create professional investment presentations'
                ],
                'status': 'Active'
            },
            {
                'id': 'COURSE-005',
                'title': 'Leadership Excellence Program',
                'category': 'Leadership',
                'department': ['All'],
                'level': 'Advanced',
                'duration': '12 weeks',
                'format': 'Hybrid',
                'provider': 'Harvard Business School Online',
                'description': 'Comprehensive leadership development for senior managers',
                'objectives': [
                    'Develop strategic thinking capabilities',
                    'Master team leadership and motivation',
                    'Improve decision-making skills',
                    'Build organizational culture'
                ],
                'status': 'Active'
            },
            {
                'id': 'COURSE-006',
                'title': 'Occupational Health & Safety',
                'category': 'Compliance',
                'department': ['All'],
                'level': 'Beginner',
                'duration': '4 weeks',
                'format': 'Online',
                'provider': 'IOSH',
                'description': 'Essential workplace health and safety training',
                'objectives': [
                    'Understand HSE regulations',
                    'Identify workplace hazards',
                    'Implement safety protocols',
                    'Respond to emergencies'
                ],
                'status': 'Active'
            },
            {
                'id': 'COURSE-007',
                'title': 'Data Analytics for Operations',
                'category': 'Technical',
                'department': ['Operations', 'ELV Systems', 'Finance'],
                'level': 'Intermediate',
                'duration': '8 weeks',
                'format': 'Online',
                'provider': 'Google Analytics Academy',
                'description': 'Using data analytics to drive operational excellence',
                'objectives': [
                    'Collect and analyze operational data',
                    'Create insightful dashboards',
                    'Use data for process improvement',
                    'Implement data-driven decision making'
                ],
                'status': 'Active'
            },
            {
                'id': 'COURSE-008',
                'title': 'Customer Experience Management',
                'category': 'Service',
                'department': ['Sales', 'Marketing', 'Operations'],
                'level': 'Intermediate',
                'duration': '6 weeks',
                'format': 'Online',
                'provider': 'CX Academy',
                'description': 'Delivering exceptional customer experiences',
                'objectives': [
                    'Understand customer journey mapping',
                    'Implement feedback systems',
                    'Design service improvement initiatives',
                    'Measure customer satisfaction'
                ],
                'status': 'Active'
            },
        ]
    
    def _initialize_webinars(self):
        """Initialize upcoming webinars"""
        today = datetime.now()
        return [
            {
                'id': 'WEB-001',
                'title': 'AI in Real Estate Management 2026',
                'date': (today + timedelta(days=15)).strftime('%Y-%m-%d'),
                'time': '10:00 AM WAT',
                'duration': '2 hours',
                'speaker': 'Dr. Adebayo Ogunlesi',
                'source': 'LinkedIn Learning',
                'department': ['Technology', 'ELV Systems', 'Operations'],
                'description': 'Exploring how AI is transforming real estate management and operations',
                'registration_link': '#',
                'status': 'Upcoming'
            },
            {
                'id': 'WEB-002',
                'title': 'HR Tech Summit 2026',
                'date': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
                'time': '9:00 AM WAT',
                'duration': '1 day',
                'speaker': 'Multiple Speakers',
                'source': 'SHRM',
                'department': ['HR'],
                'description': 'Latest trends and technologies in human resource management',
                'registration_link': '#',
                'status': 'Upcoming'
            },
            {
                'id': 'WEB-003',
                'title': 'Sustainable Building Practices',
                'date': (today + timedelta(days=20)).strftime('%Y-%m-%d'),
                'time': '2:00 PM WAT',
                'duration': '1.5 hours',
                'speaker': 'Arch. Femi Adebayo',
                'source': 'IFMA',
                'department': ['MEP', 'Operations', 'ELV Systems'],
                'description': 'Implementing sustainable practices in building management',
                'registration_link': '#',
                'status': 'Upcoming'
            },
            {
                'id': 'WEB-004',
                'title': 'Financial Planning for 2027',
                'date': (today + timedelta(days=45)).strftime('%Y-%m-%d'),
                'time': '11:00 AM WAT',
                'duration': '2 hours',
                'speaker': 'Mr. Olusegun Agbaje',
                'source': 'CFA Society Nigeria',
                'department': ['Finance', 'Accounts'],
                'description': 'Strategic financial planning and budgeting for the upcoming year',
                'registration_link': '#',
                'status': 'Upcoming'
            },
            {
                'id': 'WEB-005',
                'title': 'Cybersecurity for Smart Buildings',
                'date': (today + timedelta(days=25)).strftime('%Y-%m-%d'),
                'time': '3:00 PM WAT',
                'duration': '1 hour',
                'speaker': 'Mr. Abdul-Hakeem Ajijola',
                'source': 'NITDA',
                'department': ['IT', 'ELV Systems'],
                'description': 'Protecting smart building systems from cyber threats',
                'registration_link': '#',
                'status': 'Upcoming'
            },
        ]
    
    def _initialize_learning_paths(self):
        """Initialize learning paths for different roles"""
        return {
            'ELV Systems': {
                'name': 'ELV Systems Professional Path',
                'courses': ['COURSE-001', 'COURSE-002', 'COURSE-007'],
                'duration': '6 months',
                'certification': 'Certified ELV Systems Professional'
            },
            'MEP': {
                'name': 'MEP Engineering Excellence Path',
                'courses': ['COURSE-001', 'COURSE-008'],
                'duration': '4 months',
                'certification': 'Certified MEP Specialist'
            },
            'HR': {
                'name': 'HR Leadership Path',
                'courses': ['COURSE-003', 'COURSE-005'],
                'duration': '6 months',
                'certification': 'SHRM Certified Professional'
            },
            'Finance': {
                'name': 'Finance Excellence Path',
                'courses': ['COURSE-004', 'COURSE-007'],
                'duration': '5 months',
                'certification': 'Certified Financial Analyst'
            },
        }
    
    def _initialize_certifications(self):
        """Initialize available certifications"""
        return [
            {
                'name': 'Certified ELV Systems Professional',
                'provider': 'Churchgate Group / Siemens',
                'validity': '3 years',
                'requirements': ['COURSE-001', 'COURSE-002'],
                'exam': 'Online Assessment + Practical'
            },
            {
                'name': 'SHRM Certified Professional',
                'provider': 'SHRM',
                'validity': '3 years',
                'requirements': ['COURSE-003', 'COURSE-005'],
                'exam': 'SHRM-CP Exam'
            },
            {
                'name': 'Certified Financial Analyst',
                'provider': 'CFA Institute',
                'validity': 'Lifetime',
                'requirements': ['COURSE-004'],
                'exam': 'CFA Level 1'
            },
        ]
    
    def get_recommended_courses(self, department, employee_level=None):
        """Get recommended courses based on department and level"""
        recommended = []
        
        for course in self.courses:
            if 'All' in course['department'] or department in course['department']:
                if employee_level and course['level'] == employee_level:
                    recommended.insert(0, course)
                else:
                    recommended.append(course)
        
        return recommended[:6]  # Return top 6 recommendations
    
    def get_upcoming_webinars(self, department=None):
        """Get upcoming webinars, optionally filtered by department"""
        today = datetime.now()
        upcoming = []
        
        for webinar in self.webinars:
            webinar_date = datetime.strptime(webinar['date'], '%Y-%m-%d')
            if webinar_date > today:
                if department is None or 'All' in webinar.get('department', []) or department in webinar.get('department', []):
                    upcoming.append(webinar)
        
        return sorted(upcoming, key=lambda x: x['date'])
    
    def get_learning_path(self, department):
        """Get learning path for a department"""
        return self.learning_paths.get(department)
    
    def get_course_by_id(self, course_id):
        """Get course details by ID"""
        for course in self.courses:
            if course['id'] == course_id:
                return course
        return None
    
    def get_webinar_by_id(self, webinar_id):
        """Get webinar details by ID"""
        for webinar in self.webinars:
            if webinar['id'] == webinar_id:
                return webinar
        return None
    
    def enroll_in_course(self, employee_id, course_id):
        """Enroll an employee in a course"""
        course = self.get_course_by_id(course_id)
        if course:
            return True, f"Enrolled in {course['title']}"
        return False, "Course not found"
    
    def register_for_webinar(self, employee_id, webinar_id):
        """Register an employee for a webinar"""
        webinar = self.get_webinar_by_id(webinar_id)
        if webinar:
            return True, f"Registered for {webinar['title']}"
        return False, "Webinar not found"
    
    def get_training_calendar(self, month=None, year=None):
        """Get training calendar for a specific month"""
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
        
        events = []
        
        # Add courses starting this month
        for course in self.courses:
            events.append({
                'type': 'Course',
                'title': course['title'],
                'department': course['department'],
                'format': course['format'],
                'duration': course['duration']
            })
        
        # Add webinars this month
        for webinar in self.webinars:
            webinar_date = datetime.strptime(webinar['date'], '%Y-%m-%d')
            if webinar_date.month == month and webinar_date.year == year:
                events.append({
                    'type': 'Webinar',
                    'title': webinar['title'],
                    'date': webinar['date'],
                    'time': webinar['time'],
                    'speaker': webinar['speaker']
                })
        
        return events
    
    def get_training_stats(self, department=None):
        """Get training statistics"""
        return {
            'total_courses': len(self.courses),
            'active_courses': len([c for c in self.courses if c['status'] == 'Active']),
            'upcoming_webinars': len(self.get_upcoming_webinars(department)),
            'certifications_available': len(self.certifications),
            'departments_covered': len(set([d for c in self.courses for d in c['department']]))
        }
    
    def search_training(self, query):
        """Search courses and webinars"""
        results = []
        
        query_lower = query.lower()
        
        for course in self.courses:
            if (query_lower in course['title'].lower() or 
                query_lower in course['description'].lower() or
                query_lower in course['category'].lower()):
                results.append({'type': 'Course', 'data': course})
        
        for webinar in self.webinars:
            if (query_lower in webinar['title'].lower() or 
                query_lower in webinar['description'].lower()):
                results.append({'type': 'Webinar', 'data': webinar})
        
        return results


# Test the training service
if __name__ == "__main__":
    training = TrainingService()
    
    # Test recommendations
    courses = training.get_recommended_courses('ELV Systems')
    print(f"Recommended courses for ELV Systems: {len(courses)}")
    
    # Test webinars
    webinars = training.get_upcoming_webinars('Technology')
    print(f"Upcoming webinars for Technology: {len(webinars)}")
    
    # Test stats
    stats = training.get_training_stats()
    print(f"Training stats: {stats}")
    
    print("✅ Training service test complete")