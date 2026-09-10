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

AI Portfolio Assistant is my flagship project under development, intended to transform my online portfolio and CV into an interactive AI application. The assistant is designed to allow recruiters and technical interviewers to ask questions about my professional experience, education, projects, and skills.

The project serves as a practical environment for learning and applying AI engineering. I want to work through architecture design, data preparation, language-model integration, retrieval, evaluation, testing, and deployment myself. I will introduce technologies when they are needed to solve a specific problem.

## Problem and users

A traditional portfolio requires visitors to manually browse website sections and a PDF document. The assistant aims to make it easier to find specific information through natural-language questions, for example about my deep-learning experience, the details of my master's thesis, or the technologies used in my projects.

The primary users are recruiters and people assessing my technical competencies. The assistant is intended to help them understand my professional profile, but it is not intended to impersonate me or make recruitment decisions.

## Current implementation status

At the current stage, a local portfolio application is running with a Python and FastAPI backend. The frontend uses HTML, CSS, Jinja2, and JavaScript. The website supports Polish and English, includes About Me, Projects, and Contact sections, and allows visitors to download my CV as a PDF.

I have implemented a shared Jinja2 layout, page routing, responsive navigation, and separate JavaScript files for shared and page-specific behavior. The Projects page is generated from structured JSON data. Each project has its own URL based on a stable slug and detailed sections that can be linked to using URL anchors.

The portfolio code is available in a public GitHub repository. The project includes a description of its Python dependencies, a `.gitignore` file, example environment configuration, and setup documentation. A separate bilingual knowledge base in Markdown is also being prepared.

The conversational AI component, embeddings, vector search, automated tests, and deployment have not yet been completed. I do not present them as finished features.

## Planned AI architecture

The target query flow is as follows:

1. The user enters a question on a dedicated assistant page.
2. The frontend sends the request to the FastAPI backend.
3. The backend prepares the conversation context and retrieves relevant fragments from the approved knowledge base.
4. The language model receives the question, instructions, and selected source fragments.
5. The answer is returned with links to the relevant portfolio pages and sections.

The planned approach is Retrieval-Augmented Generation (RAG), which combines information retrieval with LLM-based answer generation. Markdown documents will be the source of knowledge, while the vector index will be a reproducible representation of that knowledge.

## Knowledge base and sources

The knowledge base will contain only information that I have deliberately approved for public disclosure. It will cover my professional profile, experience, education, skills, and detailed project descriptions.

Documents will have stable identifiers, language versions, and metadata that make it possible to associate them with public portfolio URLs. The assistant will not automatically search my private disk, private repositories, or non-public personal data.

I do not want the bot to answer using private or unapproved information. If the available knowledge is insufficient to answer a question, the system should clearly communicate that it lacks a sufficient basis rather than guess.

## Planned technology stack and technical decisions

The technologies currently in use are Python, FastAPI, Jinja2, HTML, CSS, and JavaScript. For further development, I plan to use PostgreSQL with the pgvector extension, SQLAlchemy, Pydantic, external LLM and embedding APIs, pytest, Docker, and GitHub Actions.

The choice of a specific model provider remains open. I want to compare available solutions in terms of answer quality in Polish and English, cost, latency, and data-processing conditions. The application code should be as independent as possible from any single provider.

I do not initially plan to use an extensive agent framework. I first want to understand and implement the basic RAG pipeline myself, and only then evaluate whether additional libraries genuinely simplify the project.

## Planned evaluation

The project is intended to have its own test-question dataset covering experience, projects, skills, cross-topic questions, and questions for which the knowledge base does not contain an answer.

I want to evaluate retrieval quality and generated-answer quality separately. Planned experiments include document chunking, the number of retrieved fragments, retrieval methods, and model selection. I will also analyze cases in which the system returns inappropriate sources, incorrect facts, or answers without sufficient supporting evidence.

Experiment results will be documented only after the experiments have been conducted. I am not yet claiming any metric values.

## Security and privacy

API keys and passwords will not be placed in the public repository or frontend code. Access to external services will be handled by the backend using appropriate environment configuration.

Planned safeguards include request rate limiting, error handling, cost controls, and protection against attempts to use source content or user questions to override the assistant's operating rules. Documents retrieved by RAG will be treated as data, not as higher-priority instructions.

In the public version, I do not intend to collect unnecessary personal data from users. Details concerning log retention and the privacy policy will be established before deployment.

## Planned additional features

After completing a basic, working RAG system, I am considering adding a job-posting analysis feature. It would compare the requirements of a position with my documented skills and projects, identifying both supported matches and gaps in the available information.

At a later stage, I also plan to consider selected uses of tool calling, for example to retrieve structured project data. However, I will not turn the system into a fully autonomous agent if that level of complexity is unnecessary.

## My contribution and skills being developed

I am independently developing the existing portfolio application and designing the subsequent layers of the AI system. So far, I have organized the application structure, navigation, project data, and public repository, and have started preparing knowledge-base documents.

The project is intended to give me practical experience in designing and maintaining LLM applications, semantic search, database work, testing, containerization, evaluation, and deployment. I will document completed components as development progresses so that the project description reflects the actual implementation status.

## Sources and document updates

Project repository: https://github.com/kubaperkowski22/jakub-perkowski-portfolio

This document describes the current project status and planned development directions. It will be updated before and after each major phase to distinguish implemented features from planned ones. It contains no private information, API keys, or data not intended for public disclosure.
