from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tutors.models import TutorProfile, Subject
from decimal import Decimal
import random

User = get_user_model()

# Demo tutor data
DEMO_TUTORS = [
    {'name': 'Priya Sharma', 'email': 'priya.sharma@demo.com', 'city': 'Mumbai', 'state': 'Maharashtra', 'subjects': ['Mathematics', 'Physics'], 'rate': 800, 'rating': 4.8, 'levels': 'senior_secondary', 'bio': 'Experienced Mathematics and Physics tutor with 8 years of teaching experience. Specialized in CBSE and ICSE boards.'},
    {'name': 'Rajesh Kumar', 'email': 'rajesh.kumar@demo.com', 'city': 'Delhi', 'state': 'Delhi', 'subjects': ['Chemistry', 'Biology'], 'rate': 750, 'rating': 4.6, 'levels': 'secondary', 'bio': 'Chemistry expert with strong background in organic and inorganic chemistry. Helps students excel in competitive exams.'},
    {'name': 'Anjali Patel', 'email': 'anjali.patel@demo.com', 'city': 'Ahmedabad', 'state': 'Gujarat', 'subjects': ['English', 'Hindi'], 'rate': 600, 'rating': 4.9, 'levels': 'all', 'bio': 'Language specialist teaching English and Hindi. Focus on communication skills and literature.'},
    {'name': 'Vikram Singh', 'email': 'vikram.singh@demo.com', 'city': 'Bangalore', 'state': 'Karnataka', 'subjects': ['Computer Science', 'Mathematics'], 'rate': 1000, 'rating': 4.7, 'levels': 'undergraduate', 'bio': 'Computer Science professional with industry experience. Teaches programming and data structures.'},
    {'name': 'Meera Reddy', 'email': 'meera.reddy@demo.com', 'city': 'Hyderabad', 'state': 'Telangana', 'subjects': ['Physics', 'Mathematics'], 'rate': 850, 'rating': 4.5, 'levels': 'senior_secondary', 'bio': 'Physics tutor specializing in JEE and NEET preparation. Clear concepts and problem-solving approach.'},
    {'name': 'Arjun Mehta', 'email': 'arjun.mehta@demo.com', 'city': 'Pune', 'state': 'Maharashtra', 'subjects': ['Chemistry', 'Mathematics'], 'rate': 900, 'rating': 4.8, 'levels': 'senior_secondary', 'bio': 'Chemistry and Math tutor with excellent track record in board exams and competitive tests.'},
    {'name': 'Kavita Desai', 'email': 'kavita.desai@demo.com', 'city': 'Mumbai', 'state': 'Maharashtra', 'subjects': ['English', 'History'], 'rate': 650, 'rating': 4.6, 'levels': 'secondary', 'bio': 'English and History teacher with passion for literature and social studies.'},
    {'name': 'Suresh Iyer', 'email': 'suresh.iyer@demo.com', 'city': 'Chennai', 'state': 'Tamil Nadu', 'subjects': ['Mathematics', 'Physics'], 'rate': 800, 'rating': 4.7, 'levels': 'all', 'bio': 'Experienced tutor in Mathematics and Physics. Patient teaching style suitable for all levels.'},
    {'name': 'Deepika Nair', 'email': 'deepika.nair@demo.com', 'city': 'Kochi', 'state': 'Kerala', 'subjects': ['Biology', 'Chemistry'], 'rate': 750, 'rating': 4.9, 'levels': 'senior_secondary', 'bio': 'Biology expert with focus on NEET preparation. Makes complex topics easy to understand.'},
    {'name': 'Rahul Gupta', 'email': 'rahul.gupta@demo.com', 'city': 'Kolkata', 'state': 'West Bengal', 'subjects': ['Mathematics', 'Computer Science'], 'rate': 950, 'rating': 4.6, 'levels': 'undergraduate', 'bio': 'Mathematics and CS tutor with strong analytical skills. Helps students build problem-solving abilities.'},
    {'name': 'Sneha Joshi', 'email': 'sneha.joshi@demo.com', 'city': 'Jaipur', 'state': 'Rajasthan', 'subjects': ['English', 'French'], 'rate': 700, 'rating': 4.8, 'levels': 'all', 'bio': 'Multilingual tutor teaching English and French. Focus on conversation and grammar.'},
    {'name': 'Amit Verma', 'email': 'amit.verma@demo.com', 'city': 'Lucknow', 'state': 'Uttar Pradesh', 'subjects': ['Physics', 'Chemistry'], 'rate': 850, 'rating': 4.5, 'levels': 'senior_secondary', 'bio': 'Science tutor with expertise in Physics and Chemistry. Strong foundation building approach.'},
    {'name': 'Pooja Shah', 'email': 'pooja.shah@demo.com', 'city': 'Surat', 'state': 'Gujarat', 'subjects': ['Mathematics', 'Economics'], 'rate': 800, 'rating': 4.7, 'levels': 'senior_secondary', 'bio': 'Mathematics and Economics tutor helping students understand practical applications.'},
    {'name': 'Nikhil Rao', 'email': 'nikhil.rao@demo.com', 'city': 'Bangalore', 'state': 'Karnataka', 'subjects': ['Computer Science', 'Mathematics'], 'rate': 1100, 'rating': 4.9, 'levels': 'graduate', 'bio': 'Advanced CS and Math tutor for graduate level. Industry experience in software development.'},
    {'name': 'Isha Malhotra', 'email': 'isha.malhotra@demo.com', 'city': 'Chandigarh', 'state': 'Punjab', 'subjects': ['English', 'Psychology'], 'rate': 750, 'rating': 4.6, 'levels': 'undergraduate', 'bio': 'English and Psychology tutor with counseling background. Holistic learning approach.'},
    {'name': 'Karan Thakur', 'email': 'karan.thakur@demo.com', 'city': 'Indore', 'state': 'Madhya Pradesh', 'subjects': ['Mathematics', 'Physics'], 'rate': 900, 'rating': 4.8, 'levels': 'all', 'bio': 'Versatile tutor teaching Math and Physics across all levels. Patient and methodical teaching style.'},
    {'name': 'Divya Agarwal', 'email': 'divya.agarwal@demo.com', 'city': 'Nagpur', 'state': 'Maharashtra', 'subjects': ['Biology', 'Chemistry'], 'rate': 800, 'rating': 4.7, 'levels': 'senior_secondary', 'bio': 'Biology and Chemistry specialist with focus on medical entrance exams.'},
    {'name': 'Rohit Kapoor', 'email': 'rohit.kapoor@demo.com', 'city': 'Bhopal', 'state': 'Madhya Pradesh', 'subjects': ['Mathematics', 'Statistics'], 'rate': 850, 'rating': 4.5, 'levels': 'undergraduate', 'bio': 'Mathematics and Statistics tutor for college students. Strong in data analysis.'},
    {'name': 'Shruti Menon', 'email': 'shruti.menon@demo.com', 'city': 'Thiruvananthapuram', 'state': 'Kerala', 'subjects': ['English', 'Malayalam'], 'rate': 650, 'rating': 4.9, 'levels': 'all', 'bio': 'Language tutor specializing in English and Malayalam. Cultural context in teaching.'},
    {'name': 'Aditya Chaturvedi', 'email': 'aditya.chaturvedi@demo.com', 'city': 'Varanasi', 'state': 'Uttar Pradesh', 'subjects': ['Physics', 'Mathematics'], 'rate': 800, 'rating': 4.6, 'levels': 'senior_secondary', 'bio': 'Physics and Math tutor with engineering background. Practical problem-solving methods.'},
]

class Command(BaseCommand):
    help = 'Create 20 demo tutors for testing'

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0
        
        for tutor_data in DEMO_TUTORS:
            # Check if user already exists
            if User.objects.filter(email=tutor_data['email']).exists():
                self.stdout.write(self.style.WARNING(f'Tutor {tutor_data["name"]} already exists. Skipping.'))
                skipped_count += 1
                continue
            
            # Create user
            username = tutor_data['email'].split('@')[0].replace('.', '_')
            user = User.objects.create_user(
                username=username,
                email=tutor_data['email'],
                password='demo123456',  # Demo password
                role='tutor',
                first_name=tutor_data['name'].split()[0],
                last_name=' '.join(tutor_data['name'].split()[1:]) if len(tutor_data['name'].split()) > 1 else '',
                is_verified=True
            )
            
            # Create tutor profile
            tutor_profile = TutorProfile.objects.create(
                user=user,
                headline=f"Expert {', '.join(tutor_data['subjects'][:2])} Tutor",
                bio=tutor_data['bio'],
                city=tutor_data['city'],
                state=tutor_data['state'],
                pincode=str(random.randint(100000, 999999)),
                hourly_rate=Decimal(str(tutor_data['rate'])),
                teaching_levels=tutor_data['levels'],
                is_available_online=True,
                is_available_home=random.choice([True, False]),
                is_verified=True,
                verification_status='approved',
                average_rating=Decimal(str(tutor_data['rating'])),
                total_reviews=random.randint(10, 50),
                years_of_experience=random.randint(3, 10),
                profile_complete=True,
                latitude=Decimal(str(19.0760 + random.uniform(-0.5, 0.5))),  # Around Mumbai area
                longitude=Decimal(str(72.8777 + random.uniform(-0.5, 0.5))),
            )
            
            # Add subjects
            for subject_name in tutor_data['subjects']:
                subject, _ = Subject.objects.get_or_create(name=subject_name)
                tutor_profile.subjects.add(subject)
            
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created tutor: {tutor_data["name"]} - {tutor_data["city"]}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} demo tutors.'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped {skipped_count} tutors (already exist).'))

