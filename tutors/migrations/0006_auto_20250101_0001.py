from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutors', '0005_tutorprofile_intervention_required_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorprofile',
            name='achievements',
            field=models.TextField(blank=True, help_text='Awards, recognitions or milestones'),
        ),
        migrations.AddField(
            model_name='tutorprofile',
            name='education',
            field=models.TextField(blank=True, help_text='Academic qualifications, certifications, and training'),
        ),
        migrations.AddField(
            model_name='tutorprofile',
            name='experience_summary',
            field=models.TextField(blank=True, help_text='Summary of teaching experience'),
        ),
        migrations.AddField(
            model_name='tutorprofile',
            name='headline',
            field=models.CharField(blank=True, help_text='Short headline that appears in listings', max_length=150),
        ),
        migrations.AddField(
            model_name='tutorprofile',
            name='hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Default hourly rate in INR', max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='tutorprofile',
            name='languages',
            field=models.CharField(blank=True, help_text='Languages spoken (comma separated)', max_length=255),
        ),
        migrations.AddField(
            model_name='tutorprofile',
            name='teaching_style',
            field=models.TextField(blank=True, help_text='Describe teaching methodology and approach'),
        ),
    ]

