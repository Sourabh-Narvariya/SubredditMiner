from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Query(models.Model):
    """
    Stores user search queries for Reddit communities.
    Tracks search history and associated topics.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queries')
    search_text = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.search_text[:50]}"


class RedditCommunity(models.Model):
    """
    Represents a Reddit subreddit discovered through search queries.
    Stores metadata about communities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='communities')
    name = models.CharField(max_length=255)  # e.g., r/python
    description = models.TextField()
    url = models.URLField()
    members_count = models.IntegerField(default=0)
    relevance_score = models.FloatField(default=0.0)  # LLM-based relevance (0-1)
    is_trackable = models.BooleanField(default=False)
    discovered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['query', 'name']
        ordering = ['-relevance_score']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_trackable']),
        ]
    
    def __str__(self):
        return self.name


class RedditPost(models.Model):
    """
    Represents a Reddit post scraped from a community.
    Stores post content, metadata, and engagement metrics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(RedditCommunity, on_delete=models.CASCADE, related_name='posts')
    post_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=500)
    content = models.TextField()
    author = models.CharField(max_length=255)
    upvotes = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    post_url = models.URLField()
    created_at_reddit = models.DateTimeField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at_reddit']
        indexes = [
            models.Index(fields=['community', '-created_at_reddit']),
            models.Index(fields=['post_id']),
        ]
    
    def __str__(self):
        return f"{self.community.name} - {self.title[:50]}"


class TrackableItem(models.Model):
    """
    Represents a community marked for continuous tracking.
    Stores tracking preferences and status.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.OneToOneField(RedditCommunity, on_delete=models.CASCADE, related_name='trackable')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracked_communities')
    tracking_enabled = models.BooleanField(default=True)
    last_scraped_at = models.DateTimeField(null=True, blank=True)
    scrape_frequency_hours = models.IntegerField(default=24)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['community', 'user']
        indexes = [
            models.Index(fields=['user', 'tracking_enabled']),
        ]
    
    def __str__(self):
        return f"Track: {self.community.name}"


class Snapshot(models.Model):
    """
    Represents a scraping job snapshot for a community.
    Tracks scraping attempts, status, and results.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(RedditCommunity, on_delete=models.CASCADE, related_name='snapshots')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    posts_scraped = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    webhook_delivered = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['community', 'status']),
            models.Index(fields=['-started_at']),
        ]
    
    def __str__(self):
        return f"{self.community.name} - {self.status}"


class TaskLog(models.Model):
    """
    Logs background tasks (Celery/Django Q) for monitoring.
    Useful for debugging and performance analysis.
    """
    TASK_TYPES = [
        ('scrape', 'Scrape Community'),
        ('process', 'Process Results'),
        ('notify', 'Send Notification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    task_id = models.CharField(max_length=255, unique=True)
    related_object = models.CharField(max_length=255)  # Reference to object being processed
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['task_type', 'status']),
        ]
