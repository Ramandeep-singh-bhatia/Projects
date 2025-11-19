# Enterprise Document Intelligence Platform

A production-ready document processing and intelligence system featuring hybrid search, advanced RAG techniques, and comprehensive analytics.

## 🌟 Features

### Document Processing
- **Multi-Format Support**: PDF, DOCX, XLSX, PPTX, images (with OCR), emails, HTML, Markdown
- **Intelligent Extraction**: Layout analysis, table extraction, metadata extraction
- **Smart Chunking**: Semantic awareness, structure preservation, parent-child relationships

### Hybrid Search System
- **Vector Search**: Semantic similarity using Pinecone and OpenAI embeddings
- **Keyword Search**: BM25 algorithm for exact matching
- **Fusion Strategy**: Reciprocal Rank Fusion (RRF) with configurable weighting
- **Query Enhancement**: Query expansion, spelling correction, cross-encoder re-ranking

### Advanced RAG Techniques
- **Multi-Query Retrieval**: Generate query variations for comprehensive results
- **HyDE**: Hypothetical Document Embeddings for better retrieval
- **Parent Document Retrieval**: Retrieve precise chunks, return full context
- **Multi-Hop Reasoning**: Complex question answering with reasoning chains

### Analytics Dashboard
- **Document Overview**: Processing status, type distribution, statistics
- **Search Analytics**: Query trends, top searches, performance metrics
- **Content Intelligence**: Entity extraction, topic modeling, language distribution

### Enterprise Features
- **Async Processing**: Celery + Redis task queue
- **RBAC**: Role-based access control
- **Audit Logging**: Complete activity tracking
- **REST API**: FastAPI backend with comprehensive endpoints
- **Web Interface**: Streamlit dashboard for easy interaction

## 🏗️ Architecture

```
document-intelligence/
├── src/
│   ├── api/              # FastAPI endpoints
│   │   ├── main.py       # Application entry point
│   │   ├── schemas.py    # Pydantic models
│   │   └── routes/       # API routes
│   │       ├── auth.py
│   │       ├── documents.py
│   │       ├── search.py
│   │       └── analytics.py
│   ├── core/             # Core business logic
│   │   ├── database.py   # Database configuration
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── embeddings.py # Embedding generation
│   │   └── vector_store.py # Pinecone management
│   ├── processing/       # Document processing
│   │   ├── base_extractor.py
│   │   ├── pdf_extractor.py
│   │   ├── docx_extractor.py
│   │   ├── xlsx_extractor.py
│   │   ├── pptx_extractor.py
│   │   ├── text_extractor.py
│   │   ├── chunking.py
│   │   └── document_processor.py
│   ├── search/           # Search engines
│   │   ├── vector_search.py
│   │   ├── keyword_search.py
│   │   └── hybrid_search.py
│   ├── rag/              # RAG techniques
│   │   ├── multi_query.py
│   │   ├── hyde.py
│   │   └── rag_chain.py
│   └── utils/            # Utilities
│       └── logger.py
├── frontend/             # Streamlit dashboard
│   ├── app.py            # Main dashboard
│   └── pages/            # Dashboard pages
│       ├── upload.py
│       ├── search.py
│       ├── analytics.py
│       └── viewer.py
├── config/               # Configuration
│   └── settings.py
├── tests/                # Unit tests
├── data/                 # Data storage
│   ├── uploads/          # Uploaded files
│   ├── processed/        # Processed documents
│   └── samples/          # Sample data
└── logs/                 # Application logs
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- OpenAI API key
- Pinecone account

### Installation

1. **Clone the repository**
```bash
cd document-intelligence
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
# OpenAI
OPENAI_API_KEY=your_key_here

# Pinecone
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=document-intelligence

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/document_intelligence

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
```

5. **Initialize database**
```bash
# Create PostgreSQL database
createdb document_intelligence

# Run migrations (tables will be created automatically on first run)
python -c "from src.core.database import init_db; init_db()"
```

6. **Start services**

**Terminal 1 - FastAPI Backend:**
```bash
python src/api/main.py
```

**Terminal 2 - Streamlit Dashboard:**
```bash
streamlit run frontend/app.py
```

**Terminal 3 - Celery Worker (optional):**
```bash
celery -A src.tasks worker --loglevel=info
```

### Access the Application

- **API Documentation**: http://localhost:8000/api/docs
- **Streamlit Dashboard**: http://localhost:8501
- **API Health Check**: http://localhost:8000/api/health

## 📚 Usage Guide

### 1. Upload Documents

**Via Streamlit:**
1. Navigate to "Upload Documents" page
2. Select files (PDF, DOCX, XLSX, PPTX, etc.)
3. Click "Upload All"
4. Monitor processing status

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### 2. Search Documents

**Via Streamlit:**
1. Navigate to "Search & Query" page
2. Enter search query
3. Select search strategy (hybrid, vector, keyword, multi_query, hyde)
4. View results with relevance scores

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "top_k": 10,
    "strategy": "hybrid"
  }'
```

### 3. Ask Questions (RAG)

**Via Streamlit:**
1. Navigate to "Search & Query" → "Ask Questions" tab
2. Enter your question
3. Select retrieval strategy
4. View AI-generated answer with sources

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/search/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings in the research papers?",
    "top_k": 5,
    "strategy": "multi_query"
  }'
```

### 4. View Analytics

Navigate to "Analytics Dashboard" to see:
- Document processing statistics
- Search patterns and trends
- Content intelligence insights
- Performance metrics

## 🔧 Configuration

### Search Strategies

**Hybrid** (Default - Recommended)
- Combines vector and keyword search
- 70% vector, 30% keyword weighting
- Best for most use cases

**Vector**
- Pure semantic similarity
- Best for conceptual queries
- Uses OpenAI embeddings

**Keyword (BM25)**
- Exact keyword matching
- Best for specific terms
- Fast execution

**Multi-Query**
- Generates query variations
- Comprehensive coverage
- Higher latency

**HyDE**
- Hypothetical document embeddings
- Good for vague queries
- Creative retrieval

### Chunking Strategies

Configure in `config/settings.py`:
```python
CHUNK_SIZE=1000           # Characters per chunk
CHUNK_OVERLAP=200         # Overlap between chunks
MIN_CHUNK_SIZE=100        # Minimum chunk size
```

### Performance Tuning

**Vector Search:**
```python
VECTOR_SEARCH_TOP_K=10
SIMILARITY_THRESHOLD=0.7
```

**Hybrid Search:**
```python
HYBRID_VECTOR_WEIGHT=0.7
HYBRID_KEYWORD_WEIGHT=0.3
```

**RAG:**
```python
MULTI_QUERY_NUM_QUERIES=3
MAX_CONTEXT_LENGTH=4000
```

## 🧪 Testing

Run unit tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📊 Monitoring

### Logs

Application logs are stored in `logs/`:
- `app_YYYY-MM-DD.log`: General application logs
- `error_YYYY-MM-DD.log`: Error logs only

### Metrics

Enable Prometheus metrics:
```env
ENABLE_METRICS=True
PROMETHEUS_PORT=9090
```

## 🔐 Security

### Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Rotate keys regularly
3. **Database**: Use strong passwords, enable SSL
4. **File Upload**: Validate file types and sizes
5. **CORS**: Configure allowed origins properly

### Authentication

The platform includes JWT-based authentication:

**Register:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user",
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=securepassword"
```

## 🚀 Deployment

### Docker Deployment (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: document_intelligence
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  api:
    build: .
    command: python src/api/main.py
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  dashboard:
    build: .
    command: streamlit run frontend/app.py
    ports:
      - "8501:8501"
    depends_on:
      - api
```

### Production Considerations

1. **Use production WSGI server** (Gunicorn/Uvicorn workers)
2. **Enable HTTPS** with SSL certificates
3. **Set up reverse proxy** (Nginx)
4. **Configure auto-scaling** for API workers
5. **Implement rate limiting**
6. **Set up database backups**
7. **Monitor with APM tools** (DataDog, New Relic)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **LangChain**: LLM orchestration framework
- **Pinecone**: Vector database
- **OpenAI**: Embeddings and language models
- **FastAPI**: Modern Python web framework
- **Streamlit**: Data app framework

## 📞 Support

For issues and questions:
- GitHub Issues: [Report a bug](https://github.com/yourusername/document-intelligence/issues)
- Documentation: [Full documentation](https://docs.example.com)

## 🗺️ Roadmap

- [ ] Support for more file formats (EML, MSG)
- [ ] Advanced entity extraction with spaCy
- [ ] Topic modeling with BERTopic
- [ ] Multi-language support
- [ ] Document comparison features
- [ ] Batch export functionality
- [ ] API rate limiting
- [ ] Comprehensive test coverage (>80%)
- [ ] Docker deployment configuration
- [ ] CI/CD pipeline setup

---

**Built with ❤️ for enterprise document intelligence**
