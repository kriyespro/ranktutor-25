from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import BlogPost, BlogCategory, BlogTag, FAQ, Page


def blog_list(request):
    """List all blog posts"""
    posts = BlogPost.objects.filter(is_published=True)
    
    # Filters
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    search = request.GET.get('search')
    
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(excerpt__icontains=search)
        )
    
    categories = BlogCategory.objects.all()
    recent_posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')[:5]
    
    context = {
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'cms/blog_list.jinja', context)


def blog_detail(request, slug):
    """Blog post detail"""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment views
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        is_published=True,
        category=post.category
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'cms/blog_detail.jinja', context)


def faq_list(request):
    """FAQ list page"""
    category = request.GET.get('category', 'general')
    faqs = FAQ.objects.filter(is_active=True, category=category).order_by('order', 'question')
    
    context = {
        'faqs': faqs,
        'current_category': category,
    }
    return render(request, 'cms/faq.jinja', context)


def page_detail(request, slug):
    """Static page detail"""
    page = get_object_or_404(Page, slug=slug, is_published=True)
    
    context = {
        'page': page,
    }
    return render(request, 'cms/page.jinja', context)
