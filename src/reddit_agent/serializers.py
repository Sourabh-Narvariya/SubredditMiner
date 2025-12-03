from rest_framework import serializers
from .models import (
    Query, RedditCommunity, RedditPost, 
    TrackableItem, Snapshot, TaskLog
)


class QuerySerializer(serializers.ModelSerializer):
    """Serializer for Query model with nested communities."""
    communities = serializers.SerializerMethodField()
    
    class Meta:
        model = Query
        fields = ['id', 'user', 'search_text', 'status', 'created_at', 
                 'updated_at', 'completed_at', 'error_message', 'communities']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_communities(self, obj):
        communities = obj.communities.all()
        return RedditCommunitySerializer(communities, many=True).data


class RedditCommunitySerializer(serializers.ModelSerializer):
    """Serializer for Reddit communities with relevance scoring."""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RedditCommunity
        fields = ['id', 'name', 'description', 'url', 'members_count', 
                 'relevance_score', 'is_trackable', 'discovered_at', 'posts_count']
        read_only_fields = ['id', 'discovered_at']
    
    def get_posts_count(self, obj):
        return obj.posts.count()


class RedditPostSerializer(serializers.ModelSerializer):
    """Serializer for Reddit posts with engagement metrics."""
    
    class Meta:
        model = RedditPost
        fields = ['id', 'community', 'post_id', 'title', 'content', 
                 'author', 'upvotes', 'comments_count', 'post_url', 
                 'created_at_reddit', 'scraped_at']
        read_only_fields = ['id', 'scraped_at']


class TrackableItemSerializer(serializers.ModelSerializer):
    """Serializer for tracked communities."""
    community_name = serializers.CharField(source='community.name', read_only=True)
    
    class Meta:
        model = TrackableItem
        fields = ['id', 'community', 'community_name', 'user', 
                 'tracking_enabled', 'last_scraped_at', 
                 'scrape_frequency_hours', 'created_at']
        read_only_fields = ['id', 'created_at', 'last_scraped_at']


class SnapshotSerializer(serializers.ModelSerializer):
    """Serializer for scraping job snapshots."""
    community_name = serializers.CharField(source='community.name', read_only=True)
    
    class Meta:
        model = Snapshot
        fields = ['id', 'community', 'community_name', 'status', 
                 'started_at', 'completed_at', 'posts_scraped', 
                 'error_message', 'webhook_delivered']
        read_only_fields = ['id', 'started_at']


class TaskLogSerializer(serializers.ModelSerializer):
    """Serializer for background task monitoring."""
    
    class Meta:
        model = TaskLog
        fields = ['id', 'task_type', 'task_id', 'related_object', 
                 'started_at', 'completed_at', 'status', 'result', 'error']
        read_only_fields = ['id', 'started_at']


class QueryDetailSerializer(QuerySerializer):
    """Extended serializer with full community details."""
    communities = RedditCommunitySerializer(many=True, read_only=True)
    
    class Meta(QuerySerializer.Meta):
        fields = QuerySerializer.Meta.fields
