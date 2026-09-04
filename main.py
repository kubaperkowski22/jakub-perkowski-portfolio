import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

SUPPORTED_LANGUAGES = {"pl", "en"}
DEFAULT_LANGUAGE = "pl"


app = FastAPI(title="CV online", description="Moje CV w formie online", version="1.0.0")

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def normalize_language(lang: str) -> str:
    if lang not in SUPPORTED_LANGUAGES:
        return DEFAULT_LANGUAGE
    return lang

def get_content(lang:str) -> dict:
    file_path = DATA_DIR / f"{lang}.json"

    if not file_path.exists():
        file_path = DATA_DIR / "pl.json"

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
async def home(lang: str = DEFAULT_LANGUAGE):
    lang = normalize_language(lang)

    return RedirectResponse(
        url=f"/o-mnie?lang={lang}"
    )

@app.get("/download_cv")
async def download_cv():
    cv_file_path = STATIC_DIR / "cv_example.pdf"

    if cv_file_path.exists():
        return FileResponse(
            str(cv_file_path),
            filename="_Jakub_Perkowski_SOFTWARE_ENGINEER_CV.pdf",
            media_type="application/pdf"
        )
    
    return HTMLResponse(content="<h1>CV file not found</h1>", status_code=404)

@app.get("/o-mnie", response_class=HTMLResponse)
async def about_page(request: Request, lang: str = DEFAULT_LANGUAGE):
    lang = normalize_language(lang)
    content = get_content(lang)
    target_lang = "en" if lang == "pl" else "pl"

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "content": content,
            "current_lang": lang,
            "target_lang": target_lang,
            "active_page": "about"
        }
    )

@app.get("/kontakt", response_class=HTMLResponse)
async def contact_page(request: Request, lang: str = DEFAULT_LANGUAGE):
    lang = normalize_language(lang)
    content = get_content(lang)
    target_lang = "en" if lang == "pl" else "pl"

    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context={
            "content": content,
            "current_lang": lang,
            "target_lang": target_lang,
            "active_page": "contact",
        }
    )

@app.get("/projekty", response_class=HTMLResponse)
async def projects_page(request: Request, lang: str = DEFAULT_LANGUAGE):
    lang = normalize_language(lang)
    content = get_content(lang)
    target_lang = "en" if lang == "pl" else "pl"

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "content": content,
            "current_lang": lang,
            "target_lang": target_lang,
            "active_page": "projects",
        }
    )