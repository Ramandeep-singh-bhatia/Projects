# 🤖 Multi-Agent Business Automation System

A sophisticated multi-agent system using CrewAI that coordinates multiple specialized AI agents to automate complete business workflows end-to-end.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### 7 Specialized AI Agents

1. **Research Agent** 🔍
   - Web search and information retrieval
   - Multi-source research synthesis
   - Fact verification and competitive analysis

2. **Analysis Agent** 📊
   - Python code interpreter and data visualization
   - Statistical analysis and trend identification
   - Performance benchmarking and forecasting

3. **Planning Agent** 📋
   - Strategic planning and task breakdown
   - Resource allocation and timeline estimation
   - Risk assessment and dependency mapping

4. **Content Creation Agent** ✍️
   - Blog posts, reports, and documentation
   - SEO optimization and multi-language support
   - Technical writing and API documentation

5. **Outreach Agent** 📧
   - Email campaigns and CRM integration
   - Meeting scheduling and follow-up automation
   - Stakeholder communication

6. **Quality Assurance Agent** ✅
   - Fact-checking and accuracy verification
   - Compliance checking (PII, legal, brand voice)
   - Error detection and final approval workflows

7. **Coordinator Agent** 🎯
   - Workflow orchestration and task delegation
   - Progress tracking and bottleneck detection
   - Conflict resolution and output synthesis

### 5 Pre-Built Workflows

1. **Market Research & Competitive Analysis**
   - Input: Industry/competitor names
   - Output: 20-page analysis report in ~15 minutes
   - Agents: Research → Analysis → Content → QA

2. **Content Marketing Campaign**
   - Input: Topic and duration
   - Output: Complete campaign with 20+ posts
   - Agents: Planning → Research → Content → Analysis → QA → Outreach

3. **Lead Generation & Outreach**
   - Input: ICP criteria and target count
   - Output: Automated outreach with 25%+ response rate
   - Agents: Research → Analysis → Content → QA → Outreach

4. **Product Launch Preparation**
   - Input: Product details and launch date
   - Output: Complete launch package in ~2 hours
   - Agents: Planning → Research → Content → Analysis → Outreach → QA

5. **Customer Support Escalation**
   - Input: Customer issue details
   - Output: End-to-end resolution with CSAT > 90%
   - Agents: Research → Analysis → Planning → Outreach → QA

## 🏗️ Architecture

```
multi-agent-system/
├── backend/
│   ├── agents/              # 7 specialized agents
│   ├── workflows/           # 5 pre-built workflows
│   ├── tools/              # Custom tools (web search, data analysis)
│   ├── memory/             # Redis & PostgreSQL managers
│   ├── api/                # FastAPI application
│   └── config/             # Configuration settings
├── frontend/
│   ├── dashboard/          # React monitoring dashboard
│   └── demo/               # Streamlit demo interface
├── tests/                  # Test suite
├── docker/                 # Docker configurations
├── docs/                   # Documentation
└── scripts/                # Demo and utility scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Redis
- PostgreSQL
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multi-agent-system
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start with Docker Compose** (Recommended)
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL (port 5432)
   - Redis (port 6379)
   - FastAPI Backend (port 8000)
   - React Dashboard (port 3000)
   - Streamlit Demo (port 8501)
   - Prometheus (port 9090)
   - Grafana (port 3001)

4. **Or install locally**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Start services
   python backend/api/main.py
   ```

### Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Streamlit Demo**: http://localhost:8501
- **React Dashboard**: http://localhost:3000
- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboard**: http://localhost:3001

## 📖 Usage

### Execute a Workflow via API

```python
import requests

# Execute market research workflow
response = requests.post(
    "http://localhost:8000/api/v1/workflows/execute",
    json={
        "workflow_type": "market_research",
        "input_data": {
            "industry": "SaaS B2B",
            "competitors": ["Salesforce", "HubSpot", "Microsoft"],
            "focus_areas": ["products", "pricing", "market_share"]
        }
    }
)

workflow_id = response.json()["workflow_id"]
print(f"Workflow started: {workflow_id}")

# Check workflow status
status = requests.get(f"http://localhost:8000/api/v1/workflows/{workflow_id}")
print(status.json())
```

### Execute a Workflow via Python SDK

```python
from backend.workflows import MarketResearchWorkflow

# Create and run workflow
workflow = MarketResearchWorkflow()
result = await workflow.run({
    "industry": "SaaS B2B",
    "competitors": ["Salesforce", "HubSpot"],
    "focus_areas": ["products", "pricing"]
})

print(f"Report: {result['results']['report']}")
```

### Use Individual Agents

```python
from backend.agents import ResearchAgent

# Initialize agent
research_agent = ResearchAgent()

# Execute task
result = await research_agent.run(
    task="Research AI trends in 2025",
    workflow_id="standalone",
    context={
        "research_type": "web_search",
        "num_sources": 10
    }
)

print(result)
```

## 🛠️ Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# LLM Configuration
OPENAI_API_KEY=your-openai-api-key
REASONING_MODEL=gpt-4-turbo-preview
EXECUTION_MODEL=gpt-3.5-turbo

# Database
POSTGRES_HOST=localhost
POSTGRES_DB=multi_agent_system
REDIS_HOST=localhost

# Agent Configuration
MAX_AGENT_ITERATIONS=25
AGENT_TIMEOUT_SECONDS=300
ENABLE_HUMAN_IN_LOOP=true
CONFIDENCE_THRESHOLD=0.85

# Memory Settings
ENABLE_LONG_TERM_MEMORY=true
ENABLE_SEMANTIC_MEMORY=true
MEMORY_TTL_HOURS=24
```

### API Keys Required

1. **OpenAI** - For LLM capabilities
2. **Serper/Tavily/Brave** - For web search (at least one)
3. **Salesforce/HubSpot** (Optional) - For CRM integration
4. **Gmail/Outlook** (Optional) - For email automation
5. **Jira/Asana** (Optional) - For project management

## 📊 API Reference

### Workflows Endpoints

- `GET /api/v1/workflows/` - List all workflows
- `POST /api/v1/workflows/execute` - Execute workflow
- `GET /api/v1/workflows/{workflow_id}` - Get workflow status
- `GET /api/v1/workflows/{workflow_id}/progress` - Get progress
- `DELETE /api/v1/workflows/{workflow_id}` - Cancel workflow
- `POST /api/v1/workflows/{workflow_id}/retry` - Retry failed workflow

### Agents Endpoints

- `GET /api/v1/agents/` - List all agents
- `POST /api/v1/agents/execute` - Execute agent task
- `GET /api/v1/agents/{agent_type}/metrics` - Get agent metrics
- `GET /api/v1/agents/executions/recent` - Recent executions

### Health Endpoints

- `GET /health` - System health check
- `GET /metrics` - Prometheus metrics

## 🧪 Testing

Run the test suite:

```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# End-to-end tests
pytest tests/e2e -v

# Coverage report
pytest --cov=backend tests/ --cov-report=html
```

## 📈 Monitoring

### Prometheus Metrics

The system exports metrics for:
- Workflow execution counts and duration
- Agent performance and success rates
- API request latency
- System resource usage

### Grafana Dashboards

Pre-configured dashboards for:
- Workflow analytics
- Agent performance
- System health
- Error rates and trends

## 🔒 Security & Compliance

### Safety Features

- **Human-in-the-Loop**: High-impact actions require approval
- **Compliance Checking**: PII detection, legal compliance
- **Audit Trail**: Complete activity logging
- **Confidence Thresholds**: Autonomous execution only when confident
- **Error Handling**: Retry logic and graceful degradation

### Data Privacy

- PII detection and redaction
- Encrypted storage for sensitive data
- Configurable data retention policies
- GDPR compliance support

## 🚢 Deployment

### Docker Deployment

```bash
# Build and deploy
docker-compose up -d --build

# Scale workers
docker-compose up -d --scale celery-worker=4

# View logs
docker-compose logs -f backend
```

### Production Deployment

1. **Update environment variables** for production
2. **Set up SSL/TLS** for API endpoints
3. **Configure database backups**
4. **Set up monitoring alerts**
5. **Enable rate limiting**
6. **Configure CDN** for frontend assets

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI** - Multi-agent orchestration framework
- **LangChain** - LLM application framework
- **FastAPI** - Modern web framework
- **OpenAI** - Language models

## 📞 Support

For support, please:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Contact the maintainers

## 🗺️ Roadmap

- [ ] Additional pre-built workflows
- [ ] More enterprise integrations
- [ ] Advanced monitoring dashboards
- [ ] Multi-language support
- [ ] Cloud deployment templates
- [ ] Agent marketplace

---

**Built with ❤️ using CrewAI and modern AI technologies**
