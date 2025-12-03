import logging
import os
from typing import List, Dict, Any
from google.generativeai import generativelanguage as glm
import google.generativeai as genai
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
from langchain_community.utilities import SerpAPIWrapper

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for managing LLM interactions using Google Gemini API.
    Handles query processing, topic extraction, and community relevance scoring.
    """
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_GENAI_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_GENAI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_topics(self, query_text: str) -> List[str]:
        """
        Extract relevant topics from user query using LLM.
        
        Args:
            query_text: User search query
        
        Returns:
            List of extracted topics
        """
        try:
            prompt = f"""
            Extract 3-5 key topics from this search query for Reddit communities.
            Query: {query_text}
            
            Return ONLY topics separated by commas, no explanations.
            """
            response = self.model.generate_content(prompt)
            topics = [t.strip() for t in response.text.split(',')]
            return topics
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return [query_text]
    
    def score_community_relevance(self, community_name: str, 
                                 community_desc: str, 
                                 query_topics: List[str]) -> float:
        """
        Score relevance of a Reddit community to query topics (0-1).
        
        Args:
            community_name: Reddit community name
            community_desc: Community description
            query_topics: List of query topics
        
        Returns:
            Relevance score between 0 and 1
        """
        try:
            topics_str = ", ".join(query_topics)
            prompt = f"""
            Rate the relevance of this Reddit community to these topics on a scale of 0-1.
            Only return the number, nothing else.
            
            Community: {community_name}
            Description: {community_desc}
            Topics: {topics_str}
            """
            response = self.model.generate_content(prompt)
            score = float(response.text.strip())
            return min(max(score, 0), 1)  # Ensure between 0 and 1
        except Exception as e:
            logger.error(f"Error scoring community: {e}")
            return 0.5


class RedditScraperService:
    """
    Service for Reddit scraping operations.
    Handles post extraction, comment aggregation, and data parsing.
    """
    
    @staticmethod
    def parse_reddit_post(post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw Reddit post data into structured format.
        
        Args:
            post_data: Raw post data from API
        
        Returns:
            Parsed post dictionary
        """
        return {
            'post_id': post_data.get('id'),
            'title': post_data.get('title'),
            'content': post_data.get('selftext'),
            'author': post_data.get('author'),
            'upvotes': post_data.get('score', 0),
            'comments_count': post_data.get('num_comments', 0),
            'post_url': post_data.get('url'),
        }
    
    @staticmethod
    def validate_post_data(post_data: Dict[str, Any]) -> bool:
        """
        Validate post data before storing.
        
        Args:
            post_data: Post data dictionary
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['post_id', 'title']
        return all(post_data.get(field) for field in required_fields)


class BrightDataService:
    """
    Service for Bright Data proxy integration.
    Handles search engine results proxy configuration.
    """
    
    @staticmethod
    def get_serp_config() -> Dict[str, Any]:
        """
        Get Bright Data SERP API configuration.
        
        Returns:
            Configuration dictionary for SERP API
        """
        api_key = os.getenv('BRIGHT_DATA_SER_API_KEY')
        if not api_key:
            raise ValueError("BRIGHT_DATA_SER_API_KEY environment variable not set")
        
        return {
            'provider': 'bright_data',
            'api_key': api_key,
            'search_engine': 'google',
            'country': 'us',
            'language': 'en',
            'parse': True,
        }


class CeleryTaskService:
    """
    Service for managing Celery background tasks.
    Handles task scheduling and monitoring.
    """
    
    @staticmethod
    def schedule_scraping_task(community_id: str, delay_minutes: int = 0) -> str:
        """
        Schedule a scraping task for a community.
        
        Args:
            community_id: Community ID to scrape
            delay_minutes: Delay in minutes before execution
        
        Returns:
            Task ID
        """
        from .tasks import scrape_reddit_community
        
        if delay_minutes > 0:
            task = scrape_reddit_community.apply_async(
                args=[community_id],
                countdown=delay_minutes * 60
            )
        else:
            task = scrape_reddit_community.apply_async(args=[community_id])
        
        return str(task.id)
