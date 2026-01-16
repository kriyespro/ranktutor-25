from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile
from tutors.models import TutorProfile, Subject
from students.models import StudentProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users for development'

    def handle(self, *args, **options):
        # Create test subjects
        subjects = ['Mathematics', 'Physics', 'Chemistry', 'English', 'Computer Science']
        for subject_name in subjects:
            Subject.objects.get_or_create(name=subject_name)
        
        # Create test students
        students_data = [
            {'email': 'student1@test.com', 'username': 'student1', 'password': 'TestStudent123!', 'first_name': 'John', 'last_name': 'Student'},
            {'email': 'student2@test.com', 'username': 'student2', 'password': 'TestStudent123!', 'first_name': 'Jane', 'last_name': 'Student'},
        ]
        
        for data in students_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'student',
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                StudentProfile.objects.create(user=user, city='Mumbai', state='Maharashtra')
                self.stdout.write(self.style.SUCCESS(f'Created student: {user.username}'))
        
        # Create test parents
        parents_data = [
            {'email': 'parent1@test.com', 'username': 'parent1', 'password': 'TestParent123!', 'first_name': 'Parent', 'last_name': 'One'},
        ]
        
        for data in parents_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'parent',
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                StudentProfile.objects.create(user=user, city='Delhi', state='Delhi')
                self.stdout.write(self.style.SUCCESS(f'Created parent: {user.username}'))
        
        # Create test tutors
        tutors_data = [
            {'email': 'tutor1@test.com', 'username': 'tutor1', 'password': 'TestTutor123!', 'first_name': 'Tutor', 'last_name': 'One', 'city': 'Mumbai'},
            {'email': 'tutor2@test.com', 'username': 'tutor2', 'password': 'TestTutor123!', 'first_name': 'Tutor', 'last_name': 'Two', 'city': 'Delhi'},
        ]
        
        for data in tutors_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'tutor',
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                tutor_profile = TutorProfile.objects.create(
                    user=user,
                    city=data['city'],
                    state='Maharashtra' if data['city'] == 'Mumbai' else 'Delhi',
                    pincode='400001' if data['city'] == 'Mumbai' else '110001',
                    bio=f'Experienced tutor in {data["city"]}',
                    is_available_online=True,
                    is_available_home=True,
                )
                # Add subjects
                math_subject = Subject.objects.get(name='Mathematics')
                tutor_profile.subjects.add(math_subject)
                self.stdout.write(self.style.SUCCESS(f'Created tutor: {user.username}'))
        
        # Create admin users
        admin_data = [
            {'email': 'admin@ranktutor.com', 'username': 'admin', 'password': 'Admin@RankTutor2025!', 'first_name': 'Global', 'last_name': 'Admin', 'role': 'global_admin'},
            {'email': 'cityadmin1@test.com', 'username': 'cityadmin1', 'password': 'TestCityAdmin123!', 'first_name': 'City', 'last_name': 'Admin', 'role': 'city_admin'},
        ]
        
        for data in admin_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                    'is_staff': True,
                    'is_superuser': data['role'] == 'global_admin',
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                UserProfile.objects.create(user=user, city='Mumbai' if 'city' in data['username'] else 'Delhi', state='Maharashtra')
                self.stdout.write(self.style.SUCCESS(f'Created {data["role"]}: {user.username}'))
        
        self.stdout.write(self.style.SUCCESS('\nAll test users created successfully!'))
        self.stdout.write(self.style.SUCCESS('Check test_user.txt for login credentials.'))

