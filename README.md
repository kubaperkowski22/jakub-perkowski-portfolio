# AI Portfolio Assistant

An interactive developer portfolio with a bilingual RAG-based AI assistant that answers questions about my experience, education, skills, and projects using a curated knowledge base.

The application is built with FastAPI, PostgreSQL with pgvector, OpenAI APIs, Jinja2, and vanilla JavaScript. It is deployed as a containerized web application with automated tests and CI.

## Live Demo

**Portfolio:**  
https://jakub-perkowski-portfolio.onrender.com

Try the AI assistant:

- Polish: `/chat?lang=pl`
- English: `/chat?lang=en`

## Overview

The main goal of this project was to build more than a static portfolio.

The AI assistant can answer questions such as:

- What technologies did Jakub use in his projects?
- What was his master's thesis about?
- How was the survival analysis project evaluated?
- What is the architecture of the AI Portfolio Assistant?
- Which projects involved NLP?

The assistant uses Retrieval-Augmented Generation instead of relying on the language model's general knowledge.

Answers are generated only from an approved knowledge base and include links to relevant portfolio sections.

If the available context is insufficient, the assistant is instructed to abstain instead of inventing information.

## Architecture

```text
Browser
   |
   | HTTPS
   v
FastAPI application
   |
   +-- Jinja2 / HTML / CSS / JavaScript
   |
   +-- Chat API
          |
          +-- conversation context
          |
          +-- embedding query
          |
          v
     PostgreSQL + pgvector
          |
          +-- vector similarity search
          |
          v
     retrieved knowledge chunks
          |
          v
     LLM generation
          |
          +-- structured output
          +-- citation validation
          +-- abstention
          |
          v
     SSE response
          |
          v
       Browser
```

## Tech Stack
### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- psycopg

### AI/RAG
- OpenAI API
- text embeddings
- Retrieval-Augmented Generation
- PostgreSQL
- pgvector
- cosine-distance vector retrieval
- structured LLM output
- citation validation
- conversational context

### Frontend
- HTML
- CSS
- Jinja2
- vanilla JavaScript
- Server-Sent Events

### Infrastructure
- Docker
- Docker Compose
- Render
- PostgreSQL
- GitHub Actions
- pytest

## Knowledge Base
The assistant does not use arbitrary information from the internet.

Its knowledge comes from a curated bilingual knowledge base stored as Markdown files:
```text
knowledge_base/
├── pl/
│   ├── profile.md
│   ├── experience.md
│   ├── education.md
│   ├── skills.md
│   └── projects/
└── en/
    ├── profile.md
    ├── experience.md
    ├── education.md
    ├── skills.md
    └── projects/
```

The Markdown files are the source of truth.

During ingestion they are:
1. validated,
2. split using document structure,
3. converted to embeddings,
4. stored in PostgreSQL with pgvector.

The database is treated as a rebuildable retrieval index rather than the authoritative source of portfolio content.

## RAG Pipeline
For every user question:
1. The current question is combined with recent user questions when necessary for follow-up retrieval.
2. The retrieval query is embedded.
3. Relevant chunks are retrieved from PostgreSQL using pgvector.
4. Retrieval is restricted to the selected language.
5. The retrieved chunks are passed to the LLM as the only factual evidence.
6. The model returns structured output containing:
    - whether the question is answerable,
    - the answer,
    - citation identifiers.
7. The backend validates citations before returning the response.
8. Only actually cited sources are exposed to the frontend.

Recent assistant responses are available to the generation step for conversational continuity, but they are not treated as factual evidence.

## Retrieval Evaluation
Retrieval behavior was evaluated on a small manually created development set containing 12 Polish and English questions.

| Metric         | Result |
| -------------- | -----: |
| Document Hit@1 |   100% |
| Document Hit@5 |   100% |
| Section Hit@1  |  83.3% |
| Section Hit@5  |  91.7% |
| Section Hit@8  |   100% |
| MRR            |  0.873 |

This is a development evaluation set used to guide engineering decisions, not a large-scale benchmark.

One practical result of the evaluation was choosing top_k = 8 for answer generation.

A hard vector-distance threshold was intentionally not introduced because the observed distance distributions for answerable and unanswerable questions overlapped. Abstention is therefore handled at the generation layer instead.

## Reliability and Safety
Several safeguards are implemented around the chatbot:
- server-side API keys,
- input length limits,
- conversation context limits,
- per-client rate limiting,
- language validation,
- prompt-injection-resistant system instructions,
- structured LLM output,
- citation validation,
- explicit abstention behavior,
- no permissive CORS configuration,
- security response headers,
- database accessible by the application through Render's private network.

The assistant is instructed to use only the provided knowledge-base context for factual claims and not to invent missing qualifications, technologies, experience, or personal information.

## Streaming
The chat endpoint uses Server-Sent Events.

The current implementation streams status updates and the final validated answer rather than raw model tokens.

This was an intentional design decision: the backend can validate structured output and citations before presenting the final response.

Token-level streaming can be introduced later without changing the overall RAG architecture.

## Testing
The project includes automated tests for:
- knowledge-base loading and chunking
- RAG service behavior
- answer abstention
- citation validation
- conversational retrieval
- API validation
- API failure handling
- SSE responses
- rate limiting
- client IP handling behind the deployment proxy
- application health checks

Tests are executed with:
```bash
python -m pytest -v
```

They are also run automatically using GitHub Actions.

## Local Development
### 1. Clone the repository
```bash
git clone https://github.com/kubaperkowski22/jakub-perkowski-portfolio.git
cd jakub-perkowski-portfolio
```

### 2. Configure environment variables
Create `.env` based on `.env.example`.

Required configuration includes the OpenAI API key, database connection, embedding model, and LLM model.

### 3. Start PostgreSQL
```bash
docker compose up -d db
```

### 4. Build the application image
```bash
docker compose build app
```

### 5. Initialize the database
```bash
docker compose run --rm app python -m rag.init_db
```

### 6. Ingest the knowledge base
```bash
docker compose run --rm app python -m rag.ingest
```

### 7. Start the application
```bash
docker compose up -d app
```

The application is available at **http://localhost:8000**

## Design Decisions
Some features were intentionally kept simple in the first completed version.

### Manual RAG instead of a framework

The retrieval and generation pipeline is implemented directly instead of using LangChain or another orchestration framework.

This keeps the important RAG behavior visible and makes the architecture easier to understand, test, and explain.

### PostgreSQL + pgvector
The knowledge base is small, so PostgreSQL with pgvector provides sufficient vector-search capabilities without introducing a separate vector database.

### Exact vector search
The current corpus contains only a small number of chunks, so approximate indexes such as HNSW are unnecessary at this scale.

### Short conversation memory
Only a small recent context window is sent with chat requests.

This provides follow-up question support without introducing persistent conversation storage.

### No Redis in v1
The current deployment uses a single application instance, so an in-memory sliding-window rate limiter is sufficient.

A distributed store such as Redis would become appropriate if the application were scaled horizontally.

## Possible Future Improvements
The current version is complete and deployed, but possible future extensions include:
- token-level streaming
- larger retrieval and answer evaluation sets
- automated LLM-based evaluation
- observability and tracing
- tool calling
- job-description matching

These are optional extensions rather than requirements for the current version.

## Project Status

Completed and deployed.

The application is publicly available and the current version includes the complete portfolio, bilingual RAG chatbot, evaluation pipeline, automated tests, CI, Docker deployment, and production database.

Further work will be treated as incremental improvements to the completed version rather than unfinished core functionality.