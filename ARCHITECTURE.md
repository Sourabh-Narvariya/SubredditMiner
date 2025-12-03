# System Architecture

## High-Level Design

SubredditMiner follows a modular, scalable architecture designed for maintainability and extensibility.

```
┌─────────────────────────────────────────────────────────────┐
│  User Interface / API Layer                                 │
│  (Django REST Framework)                                    │
└─────────────────────────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────────┐
│  Business Logic Layer                                       │
│  • Query Processing                                         │
│  • Community Discovery                                      │
│  • Content Filtering                                        │
└─────────────────────────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────────┐
│  AI/ML Services                                             │
│  • Google Gemini LLM                                        │
│  • LangChain Orchestration                                  │
│  • LangGraph Agents                                         │
└─────────────────────────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────────┐
│  Data Collection Layer                                      │
│  • Bright Data SERP API                                     │
│  • Reddit Scraping Pipeline                                 │
│  • Comment Extraction                                       │
└─────────────────────────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────────┐
│  Background Processing                                      │
│  • Celery Task Queue                                        │
│  • Django Q Async Jobs                                      │
│  • Webhook Handlers                                         │
└─────────────────────────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────────┐
│  Data Persistence Layer                                     │
│  • PostgreSQL Database                                      │
│  • Redis Cache                                              │
│  • File Storage                                             │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Layer
- **Framework**: Django REST Framework
- **Authentication**: Token-based auth
- **Endpoints**: 15+ REST endpoints
- **Serialization**: JSON
- **Documentation**: Auto-generated OpenAPI/Swagger

### 2. Business Logic
**Query Service**: Processes user search queries
- Parse and validate input
- Extract key topics
- Route to appropriate processors

**Community Discovery**: Find relevant Reddit communities
- Google search via Bright Data
- LLM-based relevance filtering
- Community tracking and management

**Content Pipeline**: Extract and process content
- Reddit post fetching
- Comment aggregation
- Metadata enrichment
- Duplicate detection

### 3. AI/LLM Integration
**Google Gemini API**
- Multi-turn conversations
- Context understanding
- Semantic analysis

**LangChain**
- Tool binding (Bright Data, custom scrapers)
- Memory management
- Chain orchestration

**LangGraph**
- Agentic workflows
- State management
- Conditional routing

### 4. Data Collection
**Bright Data SERP API**
- Google search proxy
- Geo-location support
- Rate limiting

**Reddit Scraper**
- Async HTTP requests
- Session management
- Error handling & retries

### 5. Background Jobs
**Celery**
- Task scheduling
- Periodic jobs
- Result caching

**Django Q**
- Simpler async task execution
- Webhook support
- Admin interface

### 6. Database Schema

**Core Tables**
```
- Query: user_id, search_text, created_at, status
- RedditCommunity: name, description, url, members
- RedditPost: community_id, title, content, upvotes, created_at
- Snapshot: community_id, scrape_timestamp, status
- TrackableItem: community_id, tracking_enabled, last_updated
- User: email, password_hash, created_at
```

## Data Flow

### Query Workflow
1. User submits query via API
2. System parses and stores query
3. Gemini AI extracts topics
4. Bright Data finds matching Reddit communities
5. LLM validates community relevance
6. Communities marked for tracking
7. Background job starts scraping
8. Results returned to user

### Scraping Workflow
1. Scheduled job checks trackable communities
2. Bright Data fetches Reddit content
3. Parse and clean HTML
4. Extract posts, comments, metadata
5. Check for duplicates
6. Store in database
7. Trigger webhooks if configured
8. Update scrape timestamp

## Scalability Considerations

**Horizontal Scaling**
- Stateless API servers
- Redis for distributed caching
- Database read replicas

**Vertical Optimization**
- Connection pooling
- Query optimization
- Indexed database lookups

**Rate Limiting**
- API throttling
- Bright Data quota management
- Request batching

## Security Architecture

- **API Authentication**: JWT tokens
- **Database**: Connection encryption
- **API Keys**: Environment variables
- **CORS**: Restricted origins
- **Input Validation**: Pydantic models
- **SQL Injection Prevention**: ORM usage

## Deployment Architecture

**Development**
- SQLite database
- Local Redis
- Single Celery worker

**Production**
- PostgreSQL cluster
- Redis Sentinel (HA)
- Multiple Celery workers
- Gunicorn + Nginx
- Docker containerization
- Kubernetes orchestration (optional)

## Performance Metrics

- API Response Time: <500ms (p95)
- Query Processing: <2 seconds
- Scraping Rate: 100+ posts/minute
- Database Query Time: <100ms
- Cache Hit Rate: 70%+

## Future Architecture Improvements

1. **Event-Driven**: Kafka for real-time processing
2. **GraphQL**: Alternative query language
3. **Microservices**: Separate scraping service
4. **Machine Learning**: Content classification models
5. **Real-time Streaming**: WebSocket support
