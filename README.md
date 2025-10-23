# ElasticIQ

ElasticIQ is a modern search and retrieval-augmented generation (RAG) application that combines the power of Elasticsearch with AI capabilities. It features a React-based frontend and a Python backend service architecture.

## 🚀 Features

- Advanced search capabilities using Elasticsearch
- RAG (Retrieval-Augmented Generation) implementation
- Modern React frontend with real-time updates
- Scalable Python backend services
- Document upload and processing
- Chat interface for interacting with documents
- Source panel for reference tracking
- Configurable settings

## 📁 Project Structure

```
ElasticIQ/
├── frontend/               # React frontend application
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   └── ...           # Other frontend resources
│   └── public/            # Static assets
├── services/              # Backend services
│   ├── api/              # API service
│   ├── common/           # Shared utilities
│   └── ingest/           # Document ingestion service
├── docs/                 # Documentation
├── tests/                # Test suite
└── infra/               # Infrastructure configuration
```

## 🛠️ Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- Elasticsearch instance
- Google Cloud Platform account (for Vertex AI integration)

## 🚀 Getting Started

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

### Backend Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install backend dependencies:
   ```bash
   cd services
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the services directory
   - Add necessary configuration (see `.env.example` if available)

4. Start the backend services:
   ```bash
   python -m api.search_rag
   ```

## 🔧 Configuration

The application requires several configuration parameters:

- Elasticsearch connection details
- Google Cloud credentials for Vertex AI
- API endpoints and ports
- Frontend environment variables

Refer to the documentation in the `docs/` directory for detailed configuration instructions.

## 🧪 Testing

Run the test suite:

```bash
cd tests
python -m pytest
```

## 📦 Deployment

The application includes Dockerfiles for both frontend and backend services. Build and deploy using:

```bash
# Build frontend
cd frontend
docker build -t elasticiq-frontend .

# Build backend
cd services
docker build -t elasticiq-backend .
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

[Add your license information here]

## 👥 Authors

[Add author information here]
