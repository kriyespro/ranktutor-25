from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, SoftDeleteModel


class BlogPost(TimeStampedModel, SoftDeleteModel):
    """Blog posts for CMS"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    content = models.TextField()
    excerpt = models.TextField(blank=True, help_text='Short summary for listing pages')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Publishing
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    views_count = models.IntegerField(default=0)
    
    # Categories
    category = models.ForeignKey('BlogCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField('BlogTag', blank=True, related_name='posts')
    
    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title


class BlogCategory(TimeStampedModel):
    """Blog categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BlogTag(TimeStampedModel):
    """Blog tags"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = 'Blog Tag'
        verbose_name_plural = 'Blog Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class FAQ(TimeStampedModel):
    """Frequently Asked Questions"""
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ('general', 'General'),
            ('students', 'For Students'),
            ('tutors', 'For Tutors'),
            ('payments', 'Payments'),
            ('bookings', 'Bookings'),
            ('other', 'Other'),
        ],
        default='general'
    )
    order = models.IntegerField(default=0, help_text='Display order')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order', 'question']
    
    def __str__(self):
        return self.question


class Page(TimeStampedModel):
    """Static pages for CMS"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    is_published = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        ordering = ['title']
    
    def __str__(self):
        return self.title
