---
id: project.ai-portfolio-assistant
language: en
title: AI Portfolio Assistant
source_type: project
source_slug: ai-portfolio-assistant
source_path: /projekty/ai-portfolio-assistant
visibility: public
---

# AI Portfolio Assistant

## Project context and objective

AI Portfolio Assistant is a chatbot integrated into Jakub's portfolio. Its purpose is to answer questions about his professional experience, projects, education, and skills.

The project was created as a practical way to develop experience in building applications based on large language models. Its main objective is to implement a RAG system over a controlled set of public information, with emphasis on grounded answers, citations, hallucination reduction, security, and measurable evaluation.

The assistant refers to Jakub in the third person and does not impersonate him.

## Application architecture

The backend is implemented in Python with FastAPI. The frontend uses Jinja2, HTML, CSS, and vanilla JavaScript.

The chatbot's knowledge is maintained as a bilingual Markdown knowledge base. These documents are treated as the source of truth, while PostgreSQL with pgvector acts as a rebuildable retrieval index.

The RAG pipeline consists of two main parts:

1. an offline process:
   - loading and validating knowledge documents;
   - structure-aware Markdown chunking;
   - generating embeddings;
   - storing chunks and vectors in PostgreSQL with pgvector;

2. an online process:
   - preparing the user query;
   - generating its embedding;
   - retrieving the most relevant chunks;
   - supplying the retrieved context to the language model;
   - generating a source-grounded answer;
   - validating citations and returning the answer together with its sources.

## Retrieval and embeddings

Semantic retrieval is implemented using embeddings and PostgreSQL with the pgvector extension.

The embedding representation of a chunk includes the document title, section name, optional subsection, and chunk content. The original content is preserved separately and is used as the evidence presented to the language model and for citations.

Retrieval is filtered by language, so Polish questions use Polish sources and English questions use English sources.

Because the current knowledge base is small, retrieval uses exact vector search without an HNSW index. This is a deliberate choice based on the size of the dataset.

## Answer generation and citations

The language model receives only retrieved knowledge-base chunks and controlled instructions.

The generated result has a structured form containing:

- whether the available sources are sufficient to answer the question;
- the answer text;
- the numbers of the sources actually used.

Answers contain inline citations such as `[1]` and `[2]`. The backend validates that citation numbers refer to retrieved sources and that inline citations are consistent with the structured citation metadata.

Only sources that were actually used in the answer are returned to the user.

Clicking a citation or source opens the corresponding portfolio page. Selected sections of the About page also support deep links that automatically open the relevant section, such as education or professional experience.

## Abstention and hallucination reduction

When the available sources are insufficient, the assistant is expected to state that the information is not available rather than inventing an answer.

Absence of information in the knowledge base is not treated as proof that something does not exist.

A vector-distance threshold was also investigated as a possible automatic abstention mechanism. On the initial evaluation set, the score ranges for answerable and unanswerable questions overlapped, so an arbitrary similarity threshold was not introduced.

## Conversation context

The chatbot supports short conversational context.

Retrieval uses the current question together with recent user questions. This makes follow-up questions such as:

“Which of them were related to the data layer?”

possible without repeating the project name.

Previous assistant answers may be supplied to the generation step as conversational context, but they are not treated as factual evidence and are not included as retrieval material.

Conversation history is currently stored in the browser and is not persisted in the database.

## Bilingual support

The portfolio and chatbot support Polish and English.

The selected application language controls the interface, retrieval language, model instructions, and generated answer. Source links preserve the currently selected language.

## API and frontend communication

The application provides a regular JSON endpoint and an endpoint using Server-Sent Events.

SSE is currently used for processing-status events and the final validated result. The model response is not streamed token by token.

This allows the complete structured output and its citations to be validated before the answer is displayed to the user.

## Retrieval evaluation

On an initial manually prepared set of 12 Polish and English questions, the retrieval system achieved:

- Document Hit@1: 100%;
- Document Hit@5: 100%;
- Section Hit@1: 83.3%;
- Section Hit@5: 91.7%;
- Section Hit@8: 100%;
- MRR: 0.873.

Based on these measurements, the number of chunks supplied to answer generation was increased from `top_k=5` to `top_k=8`.

The 12-question set is a development evaluation set and should not be interpreted as a large production benchmark.

## Testing

The project includes automated tests covering areas such as:

- knowledge-base loading and validation;
- document chunking and content preservation;
- the RAG service contract;
- answer generation and abstention behavior;
- citation validation;
- conversation-history behavior;
- FastAPI endpoints;
- SSE responses;
- rate limiting.

Fake providers and monkeypatching are used where real language-model or database access is unnecessary, keeping the core test suite deterministic and avoiding API costs.

## Security

API keys and configuration secrets remain on the server and are not exposed to the frontend.

The application includes measures such as:

- limits on message and conversation-history size;
- rate limiting for chat endpoints;
- structured-output validation;
- citation-number validation;
- prompt-injection-oriented instructions;
- source-only grounding;
- basic HTTP security headers;
- no permissive CORS configuration because the frontend and API use the same origin.

The current rate limiter is an in-memory implementation intended for a single application instance. A multi-instance deployment would require shared state such as Redis.

## Technologies

The project uses technologies including:

- Python;
- FastAPI;
- Pydantic;
- SQLAlchemy;
- PostgreSQL;
- pgvector;
- OpenAI API;
- embeddings;
- Jinja2;
- HTML;
- CSS;
- JavaScript;
- Server-Sent Events;
- pytest;
- Docker for PostgreSQL.

Embedding and language-model providers are abstracted from the main RAG logic to reduce coupling to a single API provider.

## My contribution and skills being developed

Jakub independently designed and is implementing the project's architecture.

His work on the project includes:

- designing and implementing the RAG pipeline;
- preparing a bilingual knowledge base;
- document chunking;
- embedding integration and vector retrieval;
- working with PostgreSQL and pgvector;
- language-model integration;
- designing citation and abstention mechanisms;
- retrieval evaluation;
- conversational context;
- FastAPI API design;
- Server-Sent Events;
- unit and API testing;
- baseline security for an LLM application;
- chat-interface development.

## Current project status

The project is under active development.
