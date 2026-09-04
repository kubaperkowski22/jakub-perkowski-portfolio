# Jakub Perkowski — Portfolio

Personal portfolio website built with Python and FastAPI.

The website presents my professional experience, education, technical skills
and projects in both Polish and English.

## Current features

- About me / online CV
- Polish and English language support
- Contact page
- Downloadable PDF CV

## Tech stack

- Python
- FastAPI
- Jinja2
- HTML
- CSS

## Local development

```bash
#Create a virtual environment:
python -m venv .venv

#Install dependencies:
python -m pip install -r requirements.txt

#Run the application:
python -m uvicorn main:app --reload

#The application will be available at:
http://127.0.0.1:8000
```

## AI Portfolio Assistant

An AI-powered portfolio assistant is currently under development.

The planned system will use Retrieval-Augmented Generation (RAG) to answer
questions about my professional experience and projects based only on
information available in the portfolio knowledge base.

More technical documentation will be added as the project evolves.