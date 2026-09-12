import json
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.chat import router as chat_router


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

SUPPORTED_LANGUAGES = {"pl", "en"}
DEFAULT_LANGUAGE = "pl"


app = FastAPI(title="CV online", description="Moje CV w formie online", version="1.0.0")
app.include_router(chat_router)

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

@app.get("/projekty/{slug}", response_class=HTMLResponse, name="project_detail")
async def project_detail(request: Request, slug: str, lang: str = DEFAULT_LANGUAGE):
    lang = normalize_language(lang)
    content = get_content(lang)
    page = content["projects_page"]

    project = next(
        (
            item
            for item in page["projects"]
            if item["slug"] == slug
        ),
        None,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    section_order = (
        "overview",
        "problem",
        "approach",
        "technical_details",
        "evaluation",
        "results",
        "lessons"
    )

    sections = [
        {
            "id": key,
            "title": page["detail_labels"][key],
            "text": project["details"].get(key),
        }
        for key in section_order
        if project["details"].get(key)
    ]

    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={
            "content": content,
            "current_lang": lang,
            "active_page": "projects",
            "page": page,
            "project": project,
            "sections": sections,
        },
    )


@app.get("/chat", response_class=HTMLResponse, name="chat")
def chat_page(request: Request, lang: str = DEFAULT_LANGUAGE,):
    lang = normalize_language(lang)
    content = get_content(lang)
    
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "content": content,
            "current_lang": lang,
            "active_page": "chat",
        },
    )

@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next,
):
    response = await call_next(
        request
    )

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "Referrer-Policy"
    ] = "strict-origin-when-cross-origin"

    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), microphone=(), "
        "geolocation=()"
    )

    if request.url.path.startswith(
        "/api/chat"
    ):
        response.headers[
            "Cache-Control"
        ] = "no-cache, no-store"

    return response