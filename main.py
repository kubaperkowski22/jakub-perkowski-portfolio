import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="CV online", description="Moje CV w formie online", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def get_content(lang:str) -> dict:
    file_path = os.path.join("data", f"{lang}.json")
    if not os.path.exists(file_path):
        file_path = os.path.join("data", "pl.json")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, lang:str = "pl"):
    if lang not in ["pl", "en"]:
        lang = "pl"

    content = get_content(lang)
    target_lang = "en" if lang == "pl" else "pl"

    return templates.TemplateResponse(
        request = request,
        name = "index.html",
        context = {
            "request": request,
            "content": content,
            "current_lang": lang,
            "target_lang": target_lang
        },
    )

@app.get("/download-cv")
async def download_cv():
    cv_file_path = os.path.join("static", "cv_example.pdf")

    if os.path.exists(cv_file_path):
        return FileResponse(
            cv_file_path,
            filename="_Jakub_Perkowski_SOFTWARE_ENGINEER_CV.pdf",
            media_type="application/pdf"
        )
    
    return HTMLResponse(content="<h1>CV file not found</h1>", status_code=404)

@app.get("/o-mnie", response_class=HTMLResponse)
async def about_page(request: Request, lang: str = "pl"):
    if lang not in ["pl", "en"]:
        lang = "pl"

    content = get_content(lang)
    target_lang = "en" if lang == "pl" else "pl"

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "content": content,
            "current_lang": lang,
            "target_lang": target_lang
        }
    )

@app.get("/kontakt", response_class=HTMLResponse)
async def contact_page(request: Request, lang: str = "pl"):
    if lang not in ["pl", "en"]:
        lang = "pl"

    content = get_content(lang)
    target_lang = "en" if lang == "pl" else "pl"

    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context={
            "content": content,
            "current_lang": lang,
            "target_lang": target_lang
        }
    )